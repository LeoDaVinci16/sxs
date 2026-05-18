import pandas as pd
import networkx as nx
from pyvis.network import Network
import numpy as np
import matplotlib.pyplot as plt
import os

from config import DATA_NETWORK, OUTPUT_NETWORK, nodes_csv, edges_csv


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
        "bomba": {"background": "#00f128", "border": "#00991a", "size": 20},
        "intercambiador": {"background": "#2b7ce9", "border": "#1a5aba", "size": 25},
        "diposit": {"background": "#ff9900", "border": "#cc7a00", "size": 30},
        "valve": {"background": "#ff2f00", "border": "#b32100", "size": 15},
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

def main_network(nodes_path=nodes_csv, edges_path=edges_csv, magnitude_col="cabal"):
    # -----------------------------
    # LOAD
    # -----------------------------
    nodes_df = pd.read_csv(nodes_path)
    edges_df = pd.read_csv(edges_path)

    nodes_df["node"] = nodes_df["node"].apply(normalize_id)
    nodes_df["tipus"] = nodes_df["tipus"].apply(normalize_id)

    edges_df["source"] = edges_df["source"].apply(normalize_id)
    edges_df["target"] = edges_df["target"].apply(normalize_id)

    edges_df["cabal"] = pd.to_numeric(edges_df[magnitude_col], errors="coerce").fillna(0)


    # -----------------------------
    # FLOW RANGE
    # -----------------------------
    flows = edges_df["cabal"].values
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
        return f"rgb(0,{g},0)"

    def scale_width_false(val):
        if val <= 0:
            return 0.5

        v = np.log10(val + 1)
        vmin = np.log10(fmin + 1)
        vmax = np.log10(fmax + 1)

        t = (v - vmin) / (vmax - vmin + 1e-9)

        return 0.5 + 18 * (t ** 2)
    
    def scale_width(val):
        return val/20
    


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
    tipus = {}
    for i in range(len(nodes_df)):
        print(nodes_df["node"][i], nodes_df["tipus"][i])
        tipus
    for n in G.nodes():
        n_str = normalize_id(n)
        px, py = None, None
        fixed = False
        physics = True
        print(n)

        net.add_node(
            n_str,
            label="",
            title=f"Node: {n_str}\nType: {n_str}",
            x=px,
            y=py,
            fixed=fixed,
            physics=physics,
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
            arrows={}   
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