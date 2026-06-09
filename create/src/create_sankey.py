# create_sankey.py

import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import itertools
import os
from datetime import datetime
import sys
from collections import defaultdict
from pathlib import Path
from html2image import Html2Image

collector_map = {
    0: "MAIN",
    1: "MAIN", 
    2: "MAIN", 
    3: "MAIN", 
    4: "MAIN", 
    5: "MAIN", 
    6: "MAIN", 
    7: "MAIN", 
    8: "MAIN", 
    9: "MAIN", 
    10: "MAIN", 
    11: "MAIN", 
    12: "MAIN", 
    13: "MAIN", 
    14: "MAIN", 
    15: "MAIN", 
    16: "MAIN", 
    17: "MAIN", 
    18: "MAIN", 
    19: "MAIN", 
}
    
def collapse_graph(df, magnitude_col=None):
    df = df.copy()

    def collapse(node):
        try:
            n = int(float(node))

            if 0 <= n <= 9: # 24 -> tot
                return "MAIN"

            return str(node)

        except:
            return str(node)

    df["source"] = df["source"].apply(collapse)
    df["target"] = df["target"].apply(collapse)

    print("\nAfter collapsing:")
    print(df[["source", "target"]].head(30))

    # remove MAIN -> MAIN links
    df = df[df["source"] != df["target"]]

    # Define aggregation rules dynamically
    agg_map = {
        "DN": "mean",
        "planta": "first"
    }
    
    # Columns that should be summed if present
    sum_cols = ["cabal", "area_m2", "cabal_m3h"]
    if magnitude_col and magnitude_col not in sum_cols and magnitude_col not in agg_map:
        sum_cols.append(magnitude_col)

    for col in sum_cols:
        if col in df.columns:
            agg_map[col] = "sum"

    df = (
        df.groupby(["source", "target"], as_index=False)
        .agg(agg_map)
    )

    return df


# ==============================
# 1️⃣ LOAD DATA
# ==============================
def normalize_id(id_val):
    """Ensures node IDs are compared consistently (e.g., '1.0' vs '1')."""
    try:
        f = float(id_val)
        if f == int(f):
            return str(int(f))
        return str(f)
    except (ValueError, TypeError):
        return str(id_val).strip()

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
    """Validates columns and assigns link colors based on 'planta' if available."""
    for col in [source_col, target_col, magnitude_col]:
        if col not in df.columns:
            print(f"Error: Falta la columna essencial '{col}'")

    # Assign colors based on 'planta' description if explicitly requested
    if "planta" in df.columns and colors_col not in df.columns:
        unique_plantas = df["planta"].unique()
        palette = px.colors.qualitative.Plotly
        
        def hex_to_rgba(h, a):
            h = h.lstrip('#')
            return f"rgba({int(h[0:2],16)},{int(h[2:4],16)},{int(h[4:6],16)},{a})"
        
        color_map = {p: hex_to_rgba(palette[i % len(palette)], 0.4) for i, p in enumerate(unique_plantas)}
        df[colors_col] = df["planta"].map(color_map)

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
    return node_layer, node_order

def build_sankey_output(df, source_col, target_col, magnitude_col, node_layer, node_order, nodes, nodes_df=None):
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

    # Predefined color mapping for equipment types
    node_type_colors = {
        "ramificació": "#2E8B57",
        "intercambiador": "#1F77B4",
        "chiller": "#17BECF",
        "bomba": "#FF7F0E",
        "reactor": "#D62728",
        "desconegut": "#9467BD"
    }
    
    tipus_dict = {}
    name_dict = {}
    if nodes_df is not None:
        normalized_ids = nodes_df["node"].apply(normalize_id)
        tipus_dict = dict(zip(normalized_ids, nodes_df["tipus"]))
        name_dict = dict(zip(normalized_ids, nodes_df["nom"]))

    node_labels_max = []
    node_colors = []
    for i, label in enumerate(sorted_nodes):
        incoming = df_copy.loc[df_copy["target_idx"] == i, magnitude_col].sum()
        outgoing = df_copy.loc[df_copy["source_idx"] == i, magnitude_col].sum()
        max_flow = max(incoming, outgoing)
        
        node_id = normalize_id(label)
        # Use the descriptive name if available, otherwise fallback to the ID
        display_name = name_dict.get(node_id, label)
        if pd.isna(display_name): display_name = label
        node_labels_max.append(f"{display_name} ({max_flow:.2f})")
        
        # Assign color based on 'tipus' column
        ntype = str(tipus_dict.get(node_id, "desconegut")).lower().strip()
        node_colors.append(node_type_colors.get(ntype, node_type_colors["desconegut"]))

    return df_copy, sorted_nodes, node_labels_max, node_colors, node_layer, node_order
    
def prepare_sankey_nodes(df, source_col, target_col, magnitude_col, nodes_df=None):
    nodes, out_edges, in_edges = build_graph(df, source_col, target_col)
    node_layer, node_order = propagate_order(nodes, out_edges, in_edges)
    return build_sankey_output(
        df,
        source_col,
        target_col,
        magnitude_col,
        node_layer,
        node_order,
        nodes,
        nodes_df=nodes_df
    )

def build_sankey_figure(
    df,
    all_nodes,
    node_labels,
    node_colors,
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
            color=node_colors,
            pad=15,
            thickness=15,
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
            text=f"<b>{title}</b><br><span style='font-size:{15}px;color:gray;'>{subtitle}</span>",
            x=0.5,
            xanchor='center'
        ),
        width=2560/2.5,
        height=1440/2.5,
        font=dict(size=12),
        margin=dict(l=50, r=50, t=100, b=80),
        paper_bgcolor='white',
        plot_bgcolor='white',
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
    
    mapping = {"ste": "Vapor", "at": "Aigua de torres"}
    
    return f"Diagrama Sankey"

def main(nodes_path, edges_path, output_folder, magnitude_col, title=None, output_format="html"):
    title = title or generate_sankey_title(edges_path, magnitude_col)
    nodes_df = load_file(nodes_path)
    edges_df = load_file(edges_path)

    edges_df = collapse_graph(edges_df, magnitude_col)

    print("\nNodes after collapse:")
    print(sorted(set(edges_df["source"]) | set(edges_df["target"])))

    print(
        edges_df[
            (edges_df["source"] == "MAIN") |
            (edges_df["target"] == "MAIN")
        ]
    )
    
    validate_sankey_df(edges_df, "source", "target", "color", magnitude_col)
    
    df_prepared, all_nodes, node_labels, node_colors, node_layer, node_order = prepare_sankey_nodes(edges_df, "source", "target", magnitude_col, nodes_df=nodes_df)
    
    fig = build_sankey_figure(
        df_prepared,
        all_nodes,
        node_labels,
        node_colors,
        node_layer,
        node_order,
        colors_col="color",
        title=title,
        file_path=edges_path,
        magnitude_col=magnitude_col
    )

    os.makedirs(output_folder, exist_ok=True)

    base_name = os.path.splitext(os.path.basename(edges_path))[0]
    
    html_filename = f"{base_name}_sankey.html"
    html_full_path = os.path.join(output_folder, html_filename)
    fig.write_html(html_full_path, auto_open=False)
    print(f"Sankey guardat a: {html_full_path}")

    if output_format.lower() == "png":
        png_filename = f"{base_name}_sankey.png"
        png_full_path = os.path.join(output_folder, png_filename)
        
        # Use Plotly's built-in image export for precise figure sizing.
        # This requires the 'kaleido' package (pip install kaleido).
        # The width and height are already set in fig.update_layout.
        # scale=1 means 1:1 pixel ratio, higher values increase resolution.
        fig.write_image(png_full_path, scale=1) 
        print(f"Sankey PNG generat amb Plotly a: {png_full_path}")
        return png_full_path
    
    return html_full_path

def columnes_disponibles(df):
    print("Columnes disponibles:", ", ".join(df.columns))
    return df.columns

# ==============================
# 4️⃣ ENTRY POINT
# ==============================
if __name__ == "__main__":
    at = True
    if at:
        circuit = "at"
    else:
        circuit = "ste"

    
    base_dir = Path(__file__).resolve().parents[1]
    nodes_in = base_dir / "data" / f"{circuit}_nodes.csv"
    edges_in = base_dir / "data" / f"{circuit}_edges.csv"
    folder_out = base_dir / "outputs" / circuit / f"{circuit}_sankey"
    main(str(nodes_in), str(edges_in), str(folder_out), magnitude_col="error", output_format="png")