import pandas as pd
import numpy as np
import os
import sys
from graphviz import Digraph, backend
from pathlib import Path
import shutil

from config import at_network_data as DATA_NETWORK, at_network_output as OUTPUT_NETWORK, at_nodes_csv as nodes_csv, at_edges_csv as edges_csv

# -----------------------------
# GRAPHVIZ PATH FIX (Windows)
# -----------------------------
def check_graphviz():
    """Checks if Graphviz 'dot' is available, tries common Windows paths if not."""
    if shutil.which("dot") is not None:
        return

    # List of common installation paths for Graphviz on Windows
    possible_paths = [
        r'C:\Program Files\Graphviz\bin',
        r'C:\Program Files (x86)\Graphviz\bin',
    ]

    # Include Conda environment paths if applicable (Library/bin is standard for Conda pkgs on Windows)
    if sys.executable:
        env_path = Path(sys.executable).parent
        possible_paths.append(str(env_path / "Library" / "bin"))
        possible_paths.append(str(env_path))

    # Try adding each path until 'dot' is found
    for path in possible_paths:
        if os.path.exists(path):
            os.environ["PATH"] += os.pathsep + path
            if shutil.which("dot") is not None:
                return

    raise backend.ExecutableNotFound("Graphviz 'dot' executable not found. "
                                   "Please run 'conda install graphviz' or "
                                   "install it from graphviz.org and add to PATH.")

def normalize_id(id_val):
    """Ensures node IDs are compared consistently (e.g., '1.0' vs '1')."""
    try:
        f = float(id_val)
        if f == int(f):
            return str(int(f))
        return str(f)
    except (ValueError, TypeError):
        return str(id_val).strip()

def node_style_gv(tipus):
    """Helper function to define node visual styles for Graphviz based on type."""
    tipus = str(tipus).lower().strip()
    # Graphviz uses different attribute names and shapes than pyvis
    styles = {
        "ramificació": {"fillcolor": "#ffffff", "color": "#00991a", "width": "0.4", "shape": "circle"},
        "intercambiador": {"fillcolor": "#ffffff", "color": "#1a5aba", "width": "0.7", "shape": "box"},
        "chiller": {"fillcolor": "#ffffff", "color": "#ba1aad", "width": "0.7", "shape": "box"},
        "bomba": {"fillcolor": "#ffffff", "color": "#cc7a00", "width": "0.8", "shape": "box"},
        "reactor": {"fillcolor": "#ffffff", "color": "#b32100", "width": "0.6", "shape": "cylinder"},
        "desconegut": {"fillcolor": "#ffffff", "color": "#2b7ce9", "width": "0.3", "shape": "ellipse"}
    }

    """
        styles = {
        "ramificació": {"fillcolor": "#00f128", "color": "#00991a", "width": "0.4", "shape": "circle"},
        "intercambiador": {"fillcolor": "#2b7ce9", "color": "#1a5aba", "width": "0.7", "shape": "box"},
        "chiller": {"fillcolor": "#e92be0", "color": "#ba1aad", "width": "0.7", "shape": "box"},
        "bomba": {"fillcolor": "#ff9900", "color": "#cc7a00", "width": "0.8", "shape": "box"},
        "reactor": {"fillcolor": "#ff2f00", "color": "#b32100", "width": "0.6", "shape": "cylinder"},
        "desconegut": {"fillcolor": "#97c2fc", "color": "#2b7ce9", "width": "0.3", "shape": "ellipse"}
    }
    """

    res = styles.get(tipus, styles["desconegut"])
    return {
        "fillcolor": res["fillcolor"],
        "color": res["color"],
        "width": res["width"],
        "height": res["width"], 
        "shape": res["shape"],
        "style": "filled",
        "fixedsize": "true"
    }

def main_diagram(nodes_path=nodes_csv, edges_path=edges_csv, magnitude_col="cabal", output_format="svg", title="network_diagram"):
    check_graphviz()
    # -----------------------------
    # LOAD
    # -----------------------------
    nodes_df = pd.read_csv(nodes_path)
    edges_df = pd.read_csv(edges_path)

    nodes_df["node"] = nodes_df["node"].apply(normalize_id)
    nodes_df["tipus"] = nodes_df["tipus"].astype(str)

    edges_df["source"] = edges_df["source"].apply(normalize_id)
    edges_df["target"] = edges_df["target"].apply(normalize_id)
    edges_df[magnitude_col] = pd.to_numeric(edges_df[magnitude_col], errors="coerce").fillna(0)

    # -----------------------------
    # FLOW RANGE
    # -----------------------------
    flows = edges_df[magnitude_col].values
    fmin, fmax = flows.min(), flows.max()

    # -----------------------------
    # COLOR & WIDTH HELPERS
    # -----------------------------
    def flow_color(val):
        t = (val - fmin) / (fmax - fmin + 1e-9)
        t = np.sqrt(t)
        g = 60 + int(195 * t)
        return f"#00{g:02x}00" # Graphviz prefers hex strings

    def scale_width(val):
        # penwidth in Graphviz
        # Normalize relative to the maximum flow to keep widths within a reasonable range (1 to 7)
        # This prevents thick lines from looking like squares.
        t = (val - fmin) / (fmax - fmin + 1e-9)
        v_scale = 1
        return str((1.0 + 6.0 * np.sqrt(t)) * v_scale)

    # -----------------------------
    # GRAPHVIZ INITIALIZATION
    # -----------------------------
    engine = "dot"

    # Use the explicit output_format parameter
    dot = Digraph(name=title, comment="SXS Flow Network", format=output_format, engine=engine)
    dot.attr(rankdir="LR", overlap="false", splines="true", nodesep="0.5") # These are layout attributes, not visual size
    dot.attr("node", fontname="Arial", fontsize="7") # Revert to original font size
    dot.attr("edge", fontname="Arial", fontsize="9")  # Revert to original font size

    # -----------------------------
    # NODES
    # -----------------------------
    type_map = dict(zip(nodes_df["node"], nodes_df["tipus"]))
    name_map = dict(zip(nodes_df["node"], nodes_df["nom"]))
    
    all_nodes = set(edges_df["source"]).union(set(edges_df["target"]))
    for n_str in all_nodes:
        n_type = type_map.get(n_str, "desconegut")
        n_name = name_map.get(n_str, "desconegut")
        styles = node_style_gv(n_type)
        if n_type != "ramificació":
            label = f"{n_str}\n({n_name})" if n_name != "desconegut" else n_str
        else:
            label = f"{n_name}" if n_name != "desconegut" else n_str
        dot.node(n_str, label=label, **styles)

    # -----------------------------
    # EDGES
    # -----------------------------
    for _, row in edges_df.iterrows():
        dot.edge(
            str(row["source"]), str(row["target"]),
            label=f"{row[magnitude_col]:.1f}",
            penwidth=scale_width(row[magnitude_col]),
            color=flow_color(row[magnitude_col])
        )

    os.makedirs(OUTPUT_NETWORK, exist_ok=True)
    base_filename = Path(title).stem # Define base_filename from the title
    output_file = dot.render(filename=str(OUTPUT_NETWORK / base_filename), cleanup=True)
    print(f"Diagram rendered to: {output_file}")
    return Path(output_file)

if __name__ == "__main__":
    input_file = r"data/at_edges.csv"
    magnitude_col = "cabal"  # cabal, DN, OD_mm	WT_mm	d_m	area_m2	vel_ms	cabal_m3s	cabal_kgs	cabal_m3h	cabal_teo-real
    output_format = "svg"
    title = "network_1"

    import excel2csv
    excel2csv.main(DATA_NETWORK)
    main_diagram(magnitude_col=magnitude_col, output_format=output_format, title=title)
