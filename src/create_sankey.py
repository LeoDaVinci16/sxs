# create_sankey.py

import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import itertools
import os
from datetime import datetime
from pathlib import Path
import sys
from config import OUTPUT_SANKEY, sankey_at, sankey_ste

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
    required_cols = {source_col, target_col, colors_col, magnitude_col}
    missing = required_cols - set(df.columns)
    if missing:
        raise ValueError(f"Falta aquesta dada: {missing}")

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

def build_sankey_figure(df, node_labels, colors_col, title="", file_path=None, magnitude_col="value"):
    fig = go.Figure(go.Sankey(
        node=dict(
            label=node_labels,
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
        font=dict(size=12)
    )
    return fig

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
    df_prepared, all_nodes, node_labels = prepare_sankey_nodes(df, "source", "target", magnitude_col)
    link_colors = generate_link_colors(len(df_prepared))
    fig = build_sankey_figure(df_prepared, node_labels, "color", title, file_path, magnitude_col)

    # 1️⃣ Guardar el sankey com a fitxer HTML
    from os.path import join
    output_dir = OUTPUT_SANKEY
    os.makedirs(output_dir, exist_ok=True)

    # nom del fitxer: p.ex. sankey_at_20241001.html
    base_name = os.path.splitext(os.path.basename(file_path))[0]
    now = datetime.now().strftime("%Y%m%d_%H%M")
    html_path = join(output_dir, f"{base_name}_{now}.html")

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