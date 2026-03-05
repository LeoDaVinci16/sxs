# plot_helper.py

import os
import re
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import pandas as pd

# -----------------------------
# Numeric columns
# -----------------------------
def get_numeric_columns(df):
    """Return list of numeric columns in a dataframe."""
    return df.select_dtypes(include='number').columns.tolist()

# -----------------------------
# Create plot
# -----------------------------
def create_plot(df, variable, csv_path, points_dict=None, show_date=True):

    filename = os.path.basename(csv_path)
    name_no_ext = filename.rsplit(".csv", 1)[0]
    parts = name_no_ext.split("_")
    point_id = "_".join(parts[2:])  # everything after second underscore

    fig, ax = plt.subplots(figsize=(12, 6))
    ax.plot(df.index, df[variable], linewidth=1)

    # Main title
    ax.set_title(f"{variable}", fontsize=16, pad=20)

    # Subtitle: Punt de mesura
    fig.suptitle(f"Punt de mesura: {point_id}", fontsize=12, y=0.92)

    # Axes labels and formatting
    ax.set_xlabel("Time", fontsize=12)
    ax.set_ylabel(variable, fontsize=12)
    ax.grid(True, linestyle="--", linewidth=0.5)
    ax.yaxis.set_major_locator(ticker.MaxNLocator(8))

    # Format x-axis
    ax.xaxis.set_major_formatter(plt.matplotlib.dates.DateFormatter('%H:%M'))
    fig.autofmt_xdate()
    fig.tight_layout(rect=[0, 0.05, 1, 0.95])

    # Show date of last point below x-axis
    if show_date and not df.empty:
        last_day_str = df.index[-1].strftime("%d %b %Y")
        fig.text(0.99, 0.01, last_day_str, ha="right", va="bottom", fontsize=10, color="gray")

    return fig, ax

# -----------------------------
# Save plot
# -----------------------------
def save_plot(fig, plot_folder, csv_file, variable):
    os.makedirs(plot_folder, exist_ok=True)
    csv_name_only = os.path.splitext(os.path.basename(csv_file))[0]
    variable_clean = re.sub(r"[^\w\-_\. ]", "", variable).replace(" ", "_")
    plot_name = f"{csv_name_only}_{variable_clean}.png"
    plot_path = os.path.join(plot_folder, plot_name)
    fig.savefig(plot_path, dpi=300)
    plt.close(fig)  # Free memory
    return plot_path