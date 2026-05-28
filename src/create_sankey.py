# create_sankey.py

import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import itertools
import os
from datetime import datetime
from pathlib import Path
import sys
from config import at_sankey_output as OUTPUT_SANKEY, at_edges_csv as sankey_at, ste_edges_csv as sankey_ste
from collections import defaultdict

# ==============================
# 1️⃣ LOAD DATA
# ==============================
def load_file(file_path):
    """Load CSV or Excel file and validate numeric columns."""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

    ext = os.path.splitext(file_path)[1].lower()
    if ext == ".csv":
        df = pd.read_csv(file_path, sep=None, engine='python')
        # Ensure column names are clean
        df.columns = df.columns.str.strip()
    elif ext in [".xls", ".xlsx"]:
        df = pd.read_excel(file_path)
    else:
        raise ValueError(f"Unsupported file type: {ext}")
    return df

def choose_magnitude_column(df, default="cabal"):
    """Prompt user to select magnitude column, default if empty or invalid."""
    print("Columnes disponibles:", ", ".join(df.columns))
    user_input = input(f"Escriu el nom de la columna de magnitud (enter per defecte '{default}'): ").strip()
    if user_input and user_input in df.columns:
        return user_input
    else:
        if user_input and user_input not in df.columns:
            print(f"[WARNING] '{user_input}' no existeix en el DataFrame. S'utilitza la columna per defecte: '{default}'")
        return default

# ==============================
# 2️⃣ SANKEY PROCESSING
# ==============================
def validate_sankey_df(df, source_col, target_col, colors_col, magnitude_col):
    # Check for mandatory columns required to build the graph structure
    for col in [source_col, target_col, magnitude_col]:
        if col not in df.columns:
            print(f"Error: Falta la columna essencial '{col}'")

    # If the color column is missing, we create it with a default value
    # so that the rest of the code (like build_sankey_figure) doesn't crash.
    if colors_col not in df.columns:
        df[colors_col] = "rgba(144, 144, 144, 0.5)"

def build_graph(df, source_col, target_col):
    out_edges = defaultdict(list)
    in_edges = defaultdict(list)
    nodes = set()

    for _, row in df.iterrows():
        s = row[source_col]
        t = row[target_col]

        out_edges[s].append(t)
        in_edges[t].append(s)

        nodes.add(s)
        nodes.add(t)
    #print("Nodes:", nodes, "\nOut edges:", dict(out_edges), "\nIn edges:", dict(in_edges))
    return nodes, out_edges, in_edges

def propagate_order(nodes, out_edges, in_edges):
    # 1. Rank assignment: Longest Path Layering
    # Ensures nodes appear after ALL their dependencies
    node_layer = {n: 0 for n in nodes}
    
    # Relax edges to find longest path to each node
    for _ in range(len(nodes)):
        changed = False
        for u in nodes:
            for v in out_edges[u]:
                if node_layer[v] < node_layer[u] + 1:
                    node_layer[v] = node_layer[u] + 1
                    changed = True
        if not changed:
            break

    # 2. Ordering within layers: Barycenter heuristic
    node_order = {}
    layers_map = defaultdict(list)
    for n, l in node_layer.items():
        layers_map[l].append(n)

    for l in sorted(layers_map.keys()):
        def get_sort_val(n):
            parents = in_edges[n]
            if not parents: return (0, str(n))
            p_orders = [node_order[p] for p in parents if p in node_order]
            # Sort by average parent position to minimize link crossings
            return (sum(p_orders)/len(p_orders) if p_orders else 0, str(n))
        
        layer_nodes = sorted(layers_map[l], key=get_sort_val)
        for i, n in enumerate(layer_nodes):
            node_order[n] = i
    print("Node layers:", node_layer)
    print("Node order within layers:", node_order)
    return node_layer, node_order

def build_sankey_output(df, source_col, target_col, magnitude_col, node_layer, node_order, nodes):
    sorted_nodes = sorted(
        nodes,
        key=lambda n: (
            node_layer.get(n, 999),
            node_order.get(n, 999),
            str(n)
        )
    )
        
    all_nodes = sorted_nodes
    node_indices = {name: i for i, name in enumerate(all_nodes)}

    df_copy = df.copy()
    df_copy["source_idx"] = df_copy[source_col].map(node_indices)
    df_copy["target_idx"] = df_copy[target_col].map(node_indices)

    node_labels_max = []
    for i, label in enumerate(sorted_nodes):
        incoming = df_copy.loc[df_copy["target_idx"] == i, magnitude_col].sum()
        outgoing = df_copy.loc[df_copy["source_idx"] == i, magnitude_col].sum()
        max_flow = max(incoming, outgoing)
        node_labels_max.append(f"{label} ({max_flow:.2f})")

    return df_copy, sorted_nodes, node_labels_max, node_layer, node_order
    
def prepare_sankey_nodes(df, source_col, target_col, magnitude_col):
    nodes, out_edges, in_edges = build_graph(df, source_col, target_col)
    # Pass the full nodes set to propagate_order for proper rank calculation
    node_layer, node_order = propagate_order(nodes, out_edges, in_edges)
    df_copy, sorted_nodes, node_labels, node_layer, node_order = build_sankey_output(
        df,
        source_col,
        target_col,
        magnitude_col,
        node_layer,
        node_order,
        nodes
    )
    #print("\n\n===========\nSorted Nodes:\n", sorted_nodes, "\n===========\n")
    #print("\n\n===========\nNode_abels:\n", node_labels, "\n===========\n")
    #print("\n\n===========\nNode_layer:\n", node_layer, "\n===========\n")
    #print("\n\n===========\nNode_order:\n", node_order, "\n===========\n")
    return df_copy, sorted_nodes, node_labels, node_layer, node_order


def build_sankey_figure(
    df,
    all_nodes,
    node_labels,
    node_layer,
    node_order,
    colors_col,
    title="",
    file_path=None,
    magnitude_col="value"):
    coords = compute_coordinates(node_layer, node_order)
    x, y = build_node_xy(all_nodes, coords)
    fig = go.Figure(go.Sankey(
        arrangement="snap",
        node=dict(
            label=node_labels,
            #x=x,
            #y=y,
            color="#8aa512",
            pad=20,
            thickness=25,
            align="left"
        ),
        link=dict(
            source=df["source_idx"],
            target=df["target_idx"],
            value=df[magnitude_col],
            color=df[colors_col],   
            hovertemplate="%{source.label} → %{target.label}<br>Flow: %{value}<extra></extra>"
        )
    ))

    creation_date = datetime.now().strftime("%Y-%m-%d %H:%M")
    file_name = os.path.basename(file_path) if file_path else "Unknown file"
    subtitle = f"Arxiu: {file_name} | Data creació: {creation_date} | Magnitud: {magnitude_col}"

    fig.update_layout(
        title=dict(
            text=f"<b>{title}</b><br><span style='font-size:12px;color:gray;'>{subtitle}</span>",
            x=0.5,
            xanchor='center'
        ),
        font=dict(size=12),
        margin=dict(l=50, r=50, t=100, b=80),
    )
    return fig
# =============================
# Manual order
# =============================
def compute_coordinates(node_layer, node_order):
    from collections import defaultdict
    
    # Group nodes by their layer index
    layer_groups = defaultdict(list)
    for node, layer in node_layer.items():
        layer_groups[layer].append(node)
    
    # Determine max layer index for X normalization (avoiding division by zero)
    max_l = max(node_layer.values()) if node_layer and max(node_layer.values()) > 0 else 1
    
    # This dictionary maps the node name to its computed (x, y) coordinates
    layers = {}
    
    for layer_idx, nodes in layer_groups.items():
        # X coordinate: constant for every node in the same layer
        x = 0.05 + 0.9 * (layer_idx / max_l)
        
        nodes_sorted = sorted(nodes, key=lambda n: node_order.get(n, 0))
        n_in_layer = len(nodes_sorted)
        
        for i, node in enumerate(nodes_sorted):
            # Y coordinate: distributed based on the node's index within the layer
            y_norm = 0.5 if n_in_layer == 1 else i / (n_in_layer - 1)
            y = 0.1 + 0.8 * y_norm
            
            layers[node] = (layer_idx, x, y)
    print("Computed node coordinates (node: [layer, x, y]):", layers)        
    return layers

def build_node_xy(all_nodes, coords):
    x = []
    y = []

    for n in all_nodes:
        layer, xi, yi = coords[n]
        x.append(xi)
        y.append(yi)
    return x, y


# ==============================
# 3️⃣ MAIN SANKEY FUNCTION
# ==============================
def generate_sankey_title(file_path, magnitude_col):
    """Generates a title based on the filename suffix and magnitude."""
    if not file_path:
        return f"Diagrama de flux: {magnitude_col}"
    
    raw_suffix = Path(file_path).stem.split("-")[-1].lower()
    mapping = {"ste": "Vapor", "at": "Aigua de torres"}
    display_suffix = mapping.get(raw_suffix, "")
    
    title_prefix = f" {display_suffix}" if display_suffix else ""
    return f"Diagrama Sankey - {title_prefix}"

def main_sankey(file_path=None, magnitude_col=None, title=None):
    title = title or generate_sankey_title(file_path, magnitude_col)
    df = load_file(file_path)
    validate_sankey_df(df, "source", "target", "color", magnitude_col)
    df_prepared, all_nodes, node_labels, node_layer, node_order = prepare_sankey_nodes(df, "source", "target", magnitude_col)
    fig = build_sankey_figure(
        df_prepared,
        all_nodes,
        node_labels,
        node_layer,
        node_order,
        colors_col="color",
        title=title,
        file_path=file_path,
        magnitude_col=magnitude_col
    )

    # 1️⃣ Guardar el sankey com a fitxer HTML
    from os.path import join
    output_dir = OUTPUT_SANKEY
    os.makedirs(output_dir, exist_ok=True)

    # nom del fitxer: p.ex. sankey_at_20241001.html
    base_name = os.path.splitext(os.path.basename(file_path))[0]
    now = datetime.now().strftime("%Y%m%d_%H%M")
    html_path = join(output_dir, f"{base_name}_local.html")

    fig.write_html(html_path, auto_open=False)  # no obre el navegador, només guarda
    print(f"Sankey guardat a: {html_path}")

    fig.show()

def columnes_disponibles(df):
    print("Columnes disponibles:", ", ".join(df.columns))
    return df.columns

def main():
    main_sankey(file_path= sankey_at, 
                magnitude_col="cabal m3h", 
    )

# ==============================
# 4️⃣ ENTRY POINT
# ==============================
if __name__ == "__main__":
    main()