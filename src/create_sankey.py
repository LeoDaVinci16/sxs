# create_sankey.py

import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import itertools
import os
from datetime import datetime
import sys

# ==============================
# 0️⃣ FILE INPUT HANDLER
# ==============================
def get_input_file(default_file):
    """Return file path: sys.argv[1] if exists, otherwise default_file."""
    if len(sys.argv) >= 2:
        file_path = sys.argv[1]
    else:
        file_path = default_file
        print(f"No file provided. Using default: {file_path}")
    return file_path

# ==============================
# 1️⃣ LOAD DATA
# ==============================
def load_file(file_path):
    """Load CSV or Excel file and validate numeric columns."""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

    ext = os.path.splitext(file_path)[1].lower()
    if ext == ".csv":
        df = pd.read_csv(file_path)
    elif ext in [".xls", ".xlsx"]:
        df = pd.read_excel(file_path)
    else:
        raise ValueError(f"Unsupported file type: {ext}")

    numeric_cols = df.select_dtypes(include="number").columns.tolist()
    if not numeric_cols:
        raise RuntimeError(f"No numeric columns found in file: {file_path}")

    return df, file_path, numeric_cols

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
def validate_sankey_df(df, source_col, target_col, magnitude_col):
    required_cols = {source_col, target_col, magnitude_col}
    missing = required_cols - set(df.columns)
    if missing:
        raise ValueError(f"Missing columns in dataframe: {missing}")

def prepare_sankey_nodes(df, source_col, target_col, magnitude_col):
    all_nodes = list(pd.unique(df[[source_col, target_col]].values.ravel()))
    node_indices = {name: i for i, name in enumerate(all_nodes)}

    df_copy = df.copy()
    df_copy["source_idx"] = df_copy[source_col].map(node_indices)
    df_copy["target_idx"] = df_copy[target_col].map(node_indices)

    node_labels_max = []
    for i, label in enumerate(all_nodes):
        incoming = df_copy.loc[df_copy["target_idx"] == i, magnitude_col].sum()
        outgoing = df_copy.loc[df_copy["source_idx"] == i, magnitude_col].sum()
        max_flow = max(incoming, outgoing)
        node_labels_max.append(f"{label} ({max_flow:.2f})")

    return df_copy, all_nodes, node_labels_max

def generate_link_colors(n_links, palette=None, alpha=0.4):
    palette = palette or px.colors.qualitative.Plotly
    colors = list(itertools.islice(itertools.cycle(palette), n_links))

    def hex_to_rgba(hex_color, alpha):
        hex_color = hex_color.lstrip("#")
        r = int(hex_color[0:2], 16)
        g = int(hex_color[2:4], 16)
        b = int(hex_color[4:6], 16)
        return f"rgba({r},{g},{b},{alpha})"

    return [hex_to_rgba(c, alpha) for c in colors]

def build_sankey_figure(df, node_labels, link_colors, title="", file_path=None, magnitude_col="value"):
    fig = go.Figure(go.Sankey(
        node=dict(
            label=node_labels,
            color="#8aa512",
            pad=20,
            thickness=25
        ),
        link=dict(
            source=df["source_idx"],
            target=df["target_idx"],
            value=df[magnitude_col],
            color=link_colors,
            hovertemplate="%{source.label} → %{target.label}<br>Flow: %{value}<extra></extra>"
        )
    ))

    creation_date = datetime.now().strftime("%Y-%m-%d %H:%M")
    file_name = os.path.basename(file_path) if file_path else "Unknown file"
    subtitle = f"Source: {file_name} | Generated: {creation_date} | Magnitude: {magnitude_col}"

    fig.update_layout(
        title=dict(
            text=f"<b>{title}</b><br><span style='font-size:12px;color:gray;'>{subtitle}</span>",
            x=0.5,
            xanchor='center'
        ),
        font=dict(size=12)
    )
    return fig

# ==============================
# 3️⃣ MAIN SANKEY FUNCTION
# ==============================
def main_sankey(df, magnitude_col, title="", file_path=None):
    validate_sankey_df(df, "source", "target", magnitude_col)
    df_prepared, all_nodes, node_labels = prepare_sankey_nodes(df, "source", "target", magnitude_col)
    link_colors = generate_link_colors(len(df_prepared))
    fig = build_sankey_figure(df_prepared, node_labels, link_colors, title, file_path, magnitude_col)
    fig.show()

# ==============================
# 4️⃣ ENTRY POINT
# ==============================
if __name__ == "__main__":
    DEFAULT_FILE = os.path.join("data", "csv", "sankey_nodes.csv")
    file_path = get_input_file(DEFAULT_FILE)
    df, file_path, numeric_cols = load_file(file_path)
    magnitude_col = choose_magnitude_column(df)
    main_sankey(df, magnitude_col=magnitude_col, title="Estudi dels cabals", file_path=file_path)