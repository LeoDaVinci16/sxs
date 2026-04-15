import tkinter as tk
from tkinter import filedialog, messagebox
import pandas as pd
import os

import create_sankey
import create_tkinter
import create_plots

from config import DATA_PUNTS, DATA_SANKEY, DATA_RAW


# =========================================================
# FILE / FOLDER HELPERS
# =========================================================
def ask_file(initial_dir, title="Select file", filetypes=None):
    return filedialog.askopenfilename(
        initialdir=initial_dir,
        title=title,
        filetypes=filetypes or [("All files", "*.*")]
    )


def ask_folder(initial_dir, title="Select folder"):
    return filedialog.askdirectory(
        initialdir=initial_dir,
        title=title
    )


# =========================================================
# MULTI COLUMN SELECTOR (CHECKBOXES)
# =========================================================
def ask_magnitude_columns(root, columns, title="Select columns"):
    top = tk.Toplevel(root)
    top.title(title)
    top.geometry("400x500")

    tk.Label(top, text="Select one or more columns:").pack(pady=5)

    vars_map = {}

    frame = tk.Frame(top)
    frame.pack(fill="both", expand=True)

    canvas = tk.Canvas(frame)
    scrollbar = tk.Scrollbar(frame, orient="vertical", command=canvas.yview)
    scroll = tk.Frame(canvas)

    scroll.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )

    canvas.create_window((0, 0), window=scroll, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    for col in columns:
        var = tk.BooleanVar(value=False)
        tk.Checkbutton(scroll, text=col, variable=var).pack(anchor="w")
        vars_map[col] = var

    result = {"cols": []}

    def submit():
        result["cols"] = [c for c, v in vars_map.items() if v.get()]
        top.destroy()

    tk.Button(top, text="OK", command=submit).pack(pady=10)

    top.grab_set()
    root.wait_window(top)

    return result["cols"]


# =========================================================
# SANKEY
# =========================================================
def run_sankey(root):
    file_path = ask_file(
        DATA_SANKEY,
        "Select Sankey file",
        [("CSV/Excel", "*.csv *.xlsx *.xls")]
    )

    if not file_path:
        return

    df = create_sankey.load_file(file_path)

    cols = ask_magnitude_columns(root, df.columns, "Sankey magnitudes")

    if not cols:
        messagebox.showwarning("Warning", "No columns selected")
        return

    # if your sankey still expects single column, take first
    create_sankey.main_sankey(
        file_path=file_path,
        magnitude_col=cols[0]
    )


# =========================================================
# MAP (MULTI MAGNITUDE SUPPORT)
# =========================================================
def run_map(root):
    file_path = ask_file(
        DATA_PUNTS,
        "Select Map file",
        [("CSV/Excel", "*.csv *.xlsx *.xls")]
    )

    if not file_path:
        return

    try:
        df = create_tkinter.load_measure_points(file_path)
    except Exception:
        df = pd.read_csv(file_path)

    cols = ask_magnitude_columns(root, df.columns, "Map magnitudes")

    if not cols:
        messagebox.showwarning("Warning", "No columns selected")
        return

    top = tk.Toplevel(root)

    create_tkinter.Visualizer(
        top,
        csv_file=file_path,
        magnitude_cols=cols
    )


# =========================================================
# PLOTS
# =========================================================
def run_plots(root):
    folder = ask_folder(DATA_RAW, "Select folder with CSVs")

    if not folder:
        return

    files = [f for f in os.listdir(folder) if f.endswith(".csv")]

    if not files:
        messagebox.showerror("Error", "No CSV files found")
        return

    sample_df = pd.read_csv(os.path.join(folder, files[0]))

    cols = ask_magnitude_columns(root, sample_df.columns, "Plot magnitudes")

    if not cols:
        return

    create_plots.batch_plot(folder, variables=cols)