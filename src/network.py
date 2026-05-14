# =================================================
# HYDRAULIC NETWORK VISUALISATION (PyVis)
# =================================================

import pandas as pd
import networkx as nx
from pyvis.network import Network
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import numpy as np

from config import edges, nodes


# -------------------------------------------------
# LOAD DATA
# -------------------------------------------------

nodes_df = pd.read_excel(nodes)
edges_df = pd.read_excel(edges)


# -------------------------------------------------
# CLEAN / NORMALISE TYPES
# -------------------------------------------------

nodes_df["node"] = nodes_df["node"].astype(str)

nodes_df["x"] = pd.to_numeric(nodes_df["x"], errors="coerce").fillna(0)
nodes_df["y"] = pd.to_numeric(nodes_df["y"], errors="coerce").fillna(0)
nodes_df["tipus"] = nodes_df["tipus"].astype(str).str.lower().fillna("unknown")

edges_df["source"] = edges_df["source"].astype(str)
edges_df["target"] = edges_df["target"].astype(str)

edges_df["cabal"] = pd.to_numeric(edges_df["cabal"], errors="coerce").fillna(0)


# -------------------------------------------------
# BUILD DICTIONARIES
# -------------------------------------------------

punts = dict(zip(
    nodes_df["node"],
    zip(nodes_df["x"], nodes_df["y"], nodes_df["tipus"])
))

branch = list(
    edges_df[["source", "target", "cabal"]]
    .itertuples(index=False, name=None)
)


# -------------------------------------------------
# BUILD NETWORKX GRAPH (optional but useful later)
# -------------------------------------------------

G = nx.DiGraph()

for n, (x, y, tipus) in punts.items():
    G.add_node(n, pos=(x, y), type=tipus)

for u, v, val in branch:
    G.add_edge(u, v, flow=val)


# -------------------------------------------------
# FLOW SCALING FUNCTIONS
# -------------------------------------------------

flows = [v for _, _, v in branch if v is not None]

fmin = min(flows) if flows else 0
fmax = max(flows) if flows else 1

def scale_width(val, wmin=0.5, wmax=12):

    if val is None or val <= 0:
        return wmin

    # log compression
    v = np.log10(val)

    vmin = np.log10(5)      # your minimum meaningful flow
    vmax = np.log10(1000)   # your maximum flow

    return wmin + (v - vmin) / (vmax - vmin) * (wmax - wmin)

def flow_color(val):
    t = (val - fmin) / (fmax - fmin + 1e-9)

    # nonlinear boost so differences are visible
    t = np.sqrt(t)

    g = 60 + int(195 * t)   # 60 → 255
    return f"rgb(0,{g},0)"



# -------------------------------------------------
# NODE STYLING
# -------------------------------------------------

def node_style(node_id):

    # simple rule (replace later with node type column)
    if "b" in node_id:
        return {"color": "#ff4d4d", "size": 6}

    elif "ramificació" in node_id:
        return {"color": "#bfbfbf", "size": 6}

    else:
        return {"color": "#4da6ff", "size": 6}


# -------------------------------------------------
# CREATE PYVIS NETWORK
# -------------------------------------------------

net = Network(
    height="800px",
    width="100%",
    directed=True,
    bgcolor="#ffffff",
    font_color="black"
)

net.toggle_physics(False)


# -------------------------------------------------
# ADD NODES
# -------------------------------------------------

for n, (x, y, tipus) in punts.items():

    n = str(n)

    style = node_style(tipus)

    net.add_node(
        n,
        label="",

        title=f"Node: {n}\nType: {tipus}",

        x=float(x) * 2000,
        y=-float(y) * -1415,

        physics=False,

        color=style["color"],
        size=style["size"]
    )


# -------------------------------------------------
# ADD EDGES
# -------------------------------------------------

for u, v, val in branch:

    u = str(u)
    v = str(v)

    net.add_edge(
        u,
        v,

        #label=str(round(val, 1)) if val else "",
        label="",

        title=f"{u} → {v}\nFlow: {val:.2f} m³/h",

        width=scale_width(val),
        color={"color": flow_color(val), "opacity": 0.9},

        smooth=True,

        arrows={}   # removes arrows reliably
    )


# -------------------------------------------------
# LAYOUT OPTIONS
# -------------------------------------------------

net.set_options("""
{
  "layout": {
    "improvedLayout": false
  },
  "physics": {
    "enabled": false
  },
  "interaction": {
    "dragNodes": true,
    "zoomView": true
  },
  "edges": {
    "smooth": true,
    "arrows": {
      "to": {
        "enabled": false
      }
    }
  }
}
""")


# -------------------------------------------------
# EXPORT
# -------------------------------------------------

net.write_html("network.html", notebook=False)

print("Saved: network.html")