import pandas as pd
import networkx as nx
from pyvis.network import Network
import numpy as np
import matplotlib.pyplot as plt
import os

from config import DATA_NETWORK, OUTPUT_NETWORK, nodes_csv, edges_csv

def node_style(tipus):
    """Helper function to define node visual styles based on type."""
    styles = {
        "bomba": {"color": "#00f128", "size": 15},
        "intercambiador": {"color": "#2b7ce9", "size": 20},
        "diposit": {"color": "#ff9900", "size": 25},
        "valve": {"color": "#ff2f00", "size": 10}
    }
    return styles.get(tipus, {"color": "#97c2fc", "size": 10})

def main_network(nodes_path=nodes_csv, edges_path=edges_csv, magnitude_col="cabal"):
    # -----------------------------
    # LOAD
    # -----------------------------
    nodes_df = pd.read_csv(nodes_path)
    edges_df = pd.read_csv(edges_path)

    nodes_df["node"] = nodes_df["node"].astype(str)
    edges_df["source"] = edges_df["source"].astype(str)
    edges_df["target"] = edges_df["target"].astype(str)

    edges_df["cabal"] = pd.to_numeric(edges_df[magnitude_col], errors="coerce").fillna(0)

    # -----------------------------
    # FLOW RANGE
    # -----------------------------
    flows = edges_df["cabal"].values
    fmin, fmax = flows.min(), flows.max()

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

    nodes_df["node"] = nodes_df["node"].astype(str)

    pos_map = {
        k: (float(v[0]), float(v[1]))
        for k, v in NODE_POS.items()
    }

    # -----------------------------
    # COLOR (single green intensity)
    # -----------------------------
    def flow_color(val):
        t = (val - fmin) / (fmax - fmin + 1e-9)
        # nonlinear boost so differences are visible
        t = np.sqrt(t)
        g = 60 + int(195 * t)   # 60 → 255
        return f"rgb(0,{g},0)"

    def scale_width(val):
        t = (val - fmin) / (fmax - fmin + 1e-9)
        return 1 + 10 * np.sqrt(t)

    # -----------------------------
    # GRAPH
    # -----------------------------
    G = nx.from_pandas_edgelist(edges_df, "source", "target", edge_attr="cabal", create_using=nx.DiGraph())

    # -----------------------------
    # PYVIS
    # -----------------------------
    net = Network(height="800px", width="100%", directed=True)
    net.toggle_physics(True)

    # -----------------------------
    # NODES
    # -----------------------------
    for n in G.nodes():
        # net.add_node(str(n), label=str(n), size=10)
        if n in pos_map:
            x, y = pos_map[n]
            fixed = {"x": True, "y": True}
            px, py = float(x) * 2000, float(y) * 2000
        else:
            fixed = {"x": False, "y": False}
            px, py = None, None
        net.add_node(
            n,
            #label=n,
            size=10,

            title=f"Node: {n}",

            x=px,
            y=py,

            fixed=fixed,
            physics=True,
        )

    # -----------------------------
    # EDGES
    # -----------------------------
    for u, v, data in G.edges(data=True):
        val = data.get("cabal", 0)
        net.add_edge(
            str(u), str(v),
            label=str(round(val, 1)) if val else "",
            title=f"{u} → {v}\nFlow: {val:.2f} m³/h",
            width=scale_width(val),
            color=flow_color(val),
            arrows="to"
        )

    output_path = OUTPUT_NETWORK / "network_auto_layout.html"
    os.makedirs(OUTPUT_NETWORK, exist_ok=True)
    net.write_html(str(output_path), notebook=False)
    print(f"Saved: {output_path}")
    return output_path

if __name__ == "__main__":
    import excel2csv
    import webbrowser
    # Assegurem que els fitxers CSV estiguin actualitzats abans de carregar-los
    excel2csv.main(DATA_NETWORK)
    html_path = main_network()
    webbrowser.open(html_path.as_uri())