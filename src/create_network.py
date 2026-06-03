import pandas as pd
import networkx as nx
from pyvis.network import Network
import numpy as np
import matplotlib.pyplot as plt
import os
from pathlib import Path

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

def main(nodes_path, edges_path, output_folder, magnitude_col="DN", title="network"):
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

        if n_str in punts:
            px = punts[n_str]["x"] * 2000
            py = punts[n_str]["y"] * 2000
            fixed = True
            physics = False

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

    os.makedirs(output_folder, exist_ok=True)
    output_path = Path(output_folder) / f"{title}.html"
    net.write_html(str(output_path))
    print(f"Network saved to: {output_path}")
    return output_path


if __name__ == "__main__":
    # Internal defaults for standalone testing
    base_dir = Path(__file__).resolve().parents[1]
    nodes = base_dir / "data" / "at_nodes.csv"
    edges = base_dir / "data" / "at_edges.csv"
    out = base_dir / "outputs" / "at" / "at_network"
    main(str(nodes), str(edges), str(out), "DN")