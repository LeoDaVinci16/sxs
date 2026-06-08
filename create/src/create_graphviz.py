import pandas as pd
import numpy as np
import os
import sys
from graphviz import Digraph, backend
from pathlib import Path
import shutil

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
        "ramificació": {"fillcolor": "#ffffff", "color": "#000000", "width": "0.25", "shape": "circle", "fixedsize": "true",},
        "intercambiador": {"fillcolor": "#ffffff", "color": "#000000", "width": "0.7", "shape": "box"},
        "chiller": {"fillcolor": "#ffffff", "color": "#000000", "width": "0.9", "shape": "box3d"},
        "bomba": {"fillcolor": "#ffffff", "color": "#000000", "width": "0.8", "shape": "ellipse"},
        "reactor": {"fillcolor": "#ffffff", "color": "#000000", "width": "0.8", "shape": "cylinder"},
        "desconegut": {"fillcolor": "#ffffff", "color": "#000000", "width": "0.3", "shape": "ellipse"}
    }

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

def main(nodes_path, edges_path, output_folder, magnitude_col="cabal", output_format="svg", title="graphviz_local"):
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
        t = 1-t
        g = 60 + int(195 * t)
        return f"#00{g:02x}00" # Graphviz prefers hex strings

    def scale_width(val):
        # penwidth in Graphviz
        # Normalize relative to the maximum flow to keep widths within a reasonable range (1 to 7)
        # This prevents thick lines from looking like squares.
        t = (val - fmin) / (fmax - fmin + 1e-9)
        v_scale = 1
        return str(1)
        #return str((1.0 + 6.0 * np.sqrt(t)) * v_scale)

    # -----------------------------
    # GRAPHVIZ INITIALIZATION
    # -----------------------------
    engine = "dot"

    # Use the explicit output_format parameter
    dot = Digraph(name=title, comment="SXS Flow Network", format=output_format, engine=engine)
    dot.attr(rankdir="LR", overlap="false", splines="true", nodesep="0.4") # These are layout attributes, not visual size
    dot.attr("node", fontname="Arial", fontsize="12") # Revert to original font size
    dot.attr("edge", fontname="Arial", fontsize="10")  # Revert to original font size

    # -----------------------------
    # NODES
    # -----------------------------
    type_map = dict(zip(nodes_df["node"], nodes_df["tipus"]))
    name_map = dict(zip(nodes_df["node"], nodes_df["nom_2"]))
    
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

    os.makedirs(output_folder, exist_ok=True)
    base_filename = Path(title).stem
    output_file = dot.render(filename=str(Path(output_folder) / base_filename), cleanup=True)
    print(f"Diagram rendered to: {output_file}")
    dot.view(filename=str(Path(output_folder) / base_filename))
    if show:
        dot.view(filename=str(Path(output_folder) / base_filename))
    return Path(output_file)

if __name__ == "__main__":
    base_dir = Path(__file__).resolve().parents[1]
    nodes = base_dir / "data" / "at_nodes.csv"
    edges = base_dir / "data" / "at_edges.csv"
    out = base_dir / "outputs" / "at" / "at_graphviz"
    main(str(nodes), str(edges), str(out), "cabal")