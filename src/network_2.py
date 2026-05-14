import pandas as pd
import networkx as nx
from pyvis.network import Network
import numpy as np
import matplotlib.colors as mcolors
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import numpy as np

from config import edges, nodes


# -----------------------------
# LOAD
# -----------------------------
nodes_df = pd.read_csv(nodes)
edges_df = pd.read_csv(edges)

nodes_df["node"] = nodes_df["node"].astype(str)
edges_df["source"] = edges_df["source"].astype(str)
edges_df["target"] = edges_df["target"].astype(str)

edges_df["cabal"] = pd.to_numeric(edges_df["cabal"], errors="coerce").fillna(0)

# -----------------------------
# FLOW RANGE
# -----------------------------
flows = edges_df["cabal"].values
fmin, fmax = flows.min(), flows.max()

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

# Optional: nicer hierarchical layout (try both)

net.set_options("""
{
  "physics": {
    "enabled": false
  },
  "interaction": {
    "dragNodes": true,
    "dragView": true,
    "zoomView": true
  },
  "manipulation": {
    "enabled": true
  }
}
""")

'''
net.set_options("""
{
  "physics": {
    "enabled": true,
    "stabilization": {"iterations": 200}
  },
  "layout": {
    "improvedLayout": true
  },
  "edges": {
    "smooth": false,
    "arrows": {
      "to": {
        "enabled": false
      }
    }
  }
}
""")
'''

# -----------------------------
# NODES
# -----------------------------
for n in G.nodes():
    net.add_node(str(n), label=str(n), size=10)

# -----------------------------
# EDGES
# -----------------------------
for u, v, data in G.edges(data=True):
    val = data.get("cabal", 0)

    net.add_edge(
        str(u),
        str(v),

        #value=val,
        label=str(round(val, 1)) if val else "",
        title=f"{u} → {v}\nFlow: {val:.2f} m³/h",

        width=scale_width(val),
        color=flow_color(val),
        arrows="to"
    )

# -----------------------------
# OUTPUT
# -----------------------------
net.write_html("network_auto_layout.html", notebook=False)

print("Saved: network_auto_layout.html")