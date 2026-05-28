import pandas as pd
import networkx as nx
from pyvis.network import Network
import numpy as np
import matplotlib.pyplot as plt
import os

from config import at_network_output, ste_network_output, at_network_html, ste_network_html, at_edges_csv, ste_edges_csv, at_nodes_csv, ste_edges_csv, ste_nodes_csv

nodes_csv = at_nodes_csv
edges_csv = at_edges_csv


# optional manual layout (only some nodes)
NODE_POS = {
    "1.0": (0, 0),
    "2.0": (0.1, 0),
    "3.0": (0.2, 0),
    "4.0": (0.4, 0),
    "5.0": (0.5, 0),
    "6.0": (0.46, 0.1),
    "7.0": (0.43, 0.2),
    "8.0": (0.39, 0.3),
    "9.0": (0.36, 0.4),
    "10.0": (0.33, 0.5),
    "11.0": (0.3, 0.6),
    "12.0": (0.2, 0.6),
    "13.0": (0.1, 0.6),
    "14.0": (0, 0.6),
    "15.0": (0, 0.65),
    "16.0": (0, 0.7),
    "17.0": (0, 0.75),
    "18.0": (0, 0.8),
    "19.0": (0.4, 0.6),
    "20.0": (0.6, 0.6),
    "21.0": (0.8, 0.6),
    "22.0": (0.3, 0.1),

}

def normalize_id(id_val):
    """Ensures node IDs are compared consistently (e.g., '1.0' vs '1')."""
    try:
        f = float(id_val)
        if f == int(f):
            return str(int(f))
        return str(f)
    except (ValueError, TypeError):
        return str(id_val).strip()

def node_style(tipus):
    """Helper function to define node visual styles based on type."""
    tipus = str(tipus).lower().strip()
    styles = {
        "ramificació": {"background": "#00f128", "border": "#00991a", "size": 20},
        "intercambiador": {"background": "#2b7ce9", "border": "#1a5aba", "size": 25},
        "chiller": {"background": "#2b7ce9", "border": "#1a5aba", "size": 25},
        "bomba": {"background": "#ff9900", "border": "#cc7a00", "size": 30},
        "reactor": {"background": "#ff2f00", "border": "#b32100", "size": 15},
        "desconegut": {"background": "#97c2fc", "border": "#2b7ce9", "size": 10}
    }
    res = styles.get(tipus, styles["desconegut"])
    return {
        "color": {
            "background": res["background"], 
            "border": res["border"],
            "highlight": {"background": res["background"], "border": res["border"]}
        },
        "size": res["size"]
    }

def main_network(nodes_path=nodes_csv, edges_path=edges_csv, magnitude_col="DN"):
    # -----------------------------
    # LOAD
    # -----------------------------
    nodes_df = pd.read_csv(nodes_path)
    edges_df = pd.read_csv(edges_path)

    nodes_df["node"] = nodes_df["node"].apply(normalize_id)
    nodes_df["tipus"] = nodes_df["tipus"].apply(normalize_id)

    edges_df["source"] = edges_df["source"].apply(normalize_id)
    edges_df["target"] = edges_df["target"].apply(normalize_id)

    edges_df[magnitude_col] = pd.to_numeric(edges_df[magnitude_col], errors="coerce").fillna(0)

    # -----------------------------
    # FLOW RANGE
    # -----------------------------
    flows = edges_df[magnitude_col].values
    fmin, fmax = flows.min(), flows.max()

    nodes_df["node"] = nodes_df["node"].astype(str)

    pos_map = {
        k: (float(v[0]), float(v[1]))
        for k, v in NODE_POS.items()
    }

    punts = {}
    for n_id, coords in pos_map.items():
        normalized_n_id = normalize_id(n_id)
        punts[normalized_n_id] = {
            "x": coords[0],
            "y": coords[1],
        }

    # -----------------------------
    # COLOR (single green intensity)
    # -----------------------------
    def flow_color(val):
        t = (val - fmin) / (fmax - fmin + 1e-9)
        # nonlinear boost so differences are visible
        t = np.sqrt(t)
        g = 60 + int(195 * t)   # 60 → 255
        return f"#00{g:02x}00"

    def scale_width(val):
        # Normalize relative to the maximum flow to keep widths within a reasonable range (1 to 10)
        t = (val - fmin) / (fmax - fmin + 1e-9)
        return 1.0 + 9.0 * np.sqrt(t)

    # -----------------------------
    # GRAPH
    # -----------------------------
    G = nx.from_pandas_edgelist(edges_df, "source", "target", edge_attr=magnitude_col, create_using=nx.DiGraph())

    # -----------------------------
    # PYVIS
    # -----------------------------
    net = Network(height="800px", width="100%", directed=True)
    net.toggle_physics(True)

    # -----------------------------
    # NODES
    # -----------------------------
    # Create a mapping from node ID to its type for quick lookup
    type_map = dict(zip(nodes_df["node"], nodes_df["tipus"]))
    name_map = dict(zip(nodes_df["node"], nodes_df["nom"]))

    for n in G.nodes():
        n_str = normalize_id(n)
        n_type = type_map.get(n_str, "desconegut")
        n_name = name_map.get(n_str, "desconegut")
        styles = node_style(n_type)

        px, py = None, None
        fixed = False
        physics = True

        net.add_node(
            n_str,
            label="",
            title=f"Node: {n_str} ({n_name})\nType: {n_type}",
            x=px,
            y=py,
            fixed=fixed,
            physics=physics,
            **styles
        )

    # -----------------------------
    # EDGES
    # -----------------------------
    for u, v, data in G.edges(data=True):
        val = data.get(magnitude_col, 0)
        net.add_edge(
            str(u), str(v),
            label=str(round(val, 1)) if val else "",
            title=f"{u} → {v}\n{magnitude_col}: {val:.2f}",
            width=scale_width(val),
            color=flow_color(val),
            arrows={}   
        )

    output_path = at_network_html / "network_auto_layout.html"
    os.makedirs(at_network_html, exist_ok=True)
    net.write_html(str(output_path), notebook=False)
    print(f"Saved: {output_path}")
    return output_path

if __name__ == "__main__":
    import excel2csv
    import webbrowser


    # Assegurem que els fitxers CSV estiguin actualitzats abans de carregar-los
    excel2csv.main(at_network_output)
    html_path = main_network()
    webbrowser.open(html_path.as_uri())