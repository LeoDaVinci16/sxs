import pandas as pd
import os
import sys
from graphviz import Digraph, backend
from pathlib import Path
import shutil

def check_graphviz():
    """Checks if Graphviz 'dot' is available, tries common Windows paths if not."""
    if shutil.which("dot") is not None:
        return
    possible_paths = [
        r'C:\Program Files\Graphviz\bin',
        r'C:\Program Files (x86)\Graphviz\bin',
    ]
    if sys.executable:
        env_path = Path(sys.executable).parent
        possible_paths.append(str(env_path / "Library" / "bin"))
    for path in possible_paths:
        if os.path.exists(path):
            os.environ["PATH"] += os.pathsep + path
            if shutil.which("dot") is not None:
                return
    raise backend.ExecutableNotFound("Graphviz 'dot' executable not found.")

def normalize_id(id_val):
    """Ensures node IDs are compared consistently."""
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
    styles = {
        "ramificació": {"fillcolor": "#00f128", "color": "#00991a", "width": "0.05"},
        "intercambiador": {"fillcolor": "#2b7ce9", "color": "#1a5aba", "width": "0.08"},
        "chiller": {"fillcolor": "#2b7ce9", "color": "#1a5aba", "width": "0.08"},
        "bomba": {"fillcolor": "#ff9900", "color": "#cc7a00", "width": "0.1"},
        "reactor": {"fillcolor": "#ff2f00", "color": "#b32100", "width": "0.08"},
        "desconegut": {"fillcolor": "#97c2fc", "color": "#2b7ce9", "width": "0.05"}
    }
    res = styles.get(tipus, styles["desconegut"])
    return {
        "fillcolor": res["fillcolor"],
        "color": res["color"],
        "width": res["width"],
        "height": res["width"], 
        "shape": "circle",
        "style": "filled",
        "fixedsize": "true"
    }

def main(nodes_path, edges_path, output_folder, title="coordinate_network_graphviz", scaling_factor=1000):
    check_graphviz()
    
    # Load data
    nodes_df = pd.read_csv(nodes_path)
    edges_df = pd.read_csv(edges_path)

    # Normalize IDs
    nodes_df["node"] = nodes_df["node"].apply(normalize_id)
    edges_df["source"] = edges_df["source"].apply(normalize_id)
    edges_df["target"] = edges_df["target"].apply(normalize_id)

    # Initialize Graphviz Digraph with neato engine for fixed positioning
    dot = Digraph(name=title, format="svg", engine="neato")
    dot = Digraph(name=title, format=output_format, engine="neato")
    dot.attr(bgcolor="transparent", overlap="false", splines="true", rankdir="TB", dpi="300")
    dot.attr("node", fontname="Arial", fontsize="7")
    dot.attr("edge", fontname="Arial", fontsize="7")

    # Add Nodes from coordinates
    type_map = dict(zip(nodes_df["node"], nodes_df["tipus"]))
    name_map = dict(zip(nodes_df["node"], nodes_df["nom"]))
    
    for n_str, row in nodes_df.set_index("node").iterrows():
        n_type = type_map.get(n_str, "desconegut")
        n_name = str(row.get("nom", n_str))
        x, y = row.get("x"), row.get("y")
        
        if pd.notna(x) and pd.notna(y):
            styles = node_style_gv(n_type)
            label = n_name if n_name != "nan" else n_str
            
            # The '!' suffix in pos forces the node to the exact coordinate
            pos_val = f"{float(x) * 2 * scaling_factor},{float(y) * scaling_factor * -1}!"
            dot.node(str(n_str), label="", xlabel=label, pos=pos_val, **styles)

    # Add Edges
    for _, row in edges_df.iterrows():
        dot.edge(
            str(row["source"]), 
            str(row["target"]), 
            label="",
            color="gray",
            penwidth="2.5" # Thickened edges for visibility
        )

    os.makedirs(output_folder, exist_ok=True)
    base_filename = Path(output_folder) / Path(title).stem
    output_path = dot.render(filename=str(base_filename), cleanup=True)
    print(f"Network diagram saved to: {output_path}")
    return output_path

if __name__ == "__main__":
    base_dir = Path(__file__).resolve().parents[1]
    nodes = base_dir / "data" / "at_nodes.csv"
    edges = base_dir / "data" / "at_edges.csv"
    out = base_dir / "outputs" / "at" / "at_network_graphviz_coord"
    main(str(nodes), str(edges), str(out), scaling_factor=5000)
    # Output directly to the LaTeX report figures folder as PDF
    out = base_dir / "memoria" / "report_figures"
    main(str(nodes), str(edges), str(out), title="network", scaling_factor=5000, output_format="pdf")