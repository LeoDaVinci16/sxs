import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import itertools
import os
from datetime import datetime


def create_sankey(
    df,
    magnitude_col,
    title="",
    source_col="source",
    target_col="target",
    file_path=None
):
    # --- 0️⃣ Validation ---
    required_cols = {source_col, target_col, magnitude_col}
    missing = required_cols - set(df.columns)
    if missing:
        raise ValueError(f"Missing columns in dataframe: {missing}")

    # --- 1️⃣ Prepare nodes ---
    all_nodes = list(pd.unique(df[[source_col, target_col]].values.ravel()))
    node_indices = {name: i for i, name in enumerate(all_nodes)}

    df = df.copy()
    df["source_idx"] = df[source_col].map(node_indices)
    df["target_idx"] = df[target_col].map(node_indices)

    # --- 2️⃣ Colors ---
    palette = px.colors.qualitative.Plotly
    colors = list(itertools.islice(itertools.cycle(palette), len(df)))

    def hex_to_rgba(hex_color, alpha=0.4):
        hex_color = hex_color.lstrip('#')
        r = int(hex_color[0:2], 16)
        g = int(hex_color[2:4], 16)
        b = int(hex_color[4:6], 16)
        return f"rgba({r},{g},{b},{alpha})"

    link_colors = [hex_to_rgba(c, 0.4) for c in colors]

    # --- 3️⃣ Node labels with max flow ---
    node_labels_max = []
    for i, label in enumerate(all_nodes):
        incoming = df.loc[df["target_idx"] == i, magnitude_col].sum()
        outgoing = df.loc[df["source_idx"] == i, magnitude_col].sum()
        max_flow = max(incoming, outgoing)
        node_labels_max.append(f"{label} ({max_flow:.2f})")

    # --- 4️⃣ Build figure ---
    fig = go.Figure(go.Sankey(
        node=dict(
            label=node_labels_max,
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

    # --- 5️⃣ Layout ---
    creation_date = datetime.now().strftime("%Y-%m-%d %H:%M")
    file_name = os.path.basename(file_path) if file_path else "Unknown file"

    subtitle = (
        f"Source: {file_name} | Generated: {creation_date} | Magnitude: {magnitude_col}"
    )

    fig.update_layout(
        title=dict(
            text=f"<b>{title}</b><br><span style='font-size:12px;color:gray;'>{subtitle}</span>",
            x=0.5,
            xanchor='center'
        ),
        font=dict(size=12)
    )

    return fig
