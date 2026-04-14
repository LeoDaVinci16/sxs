import tkinter as tk
from tkinter import filedialog, messagebox
import os
import subprocess
from pathlib import Path
import sys
import pandas as pd

# -----------------------------
# PATHS
# -----------------------------
ROOT_FOLDER = Path(__file__).parents[1]
DOCS_FOLDER = os.path.join(ROOT_FOLDER, "data", "docs")
CSV_FOLDER = os.path.join(ROOT_FOLDER, "data")
DEFAULT_PLOT_FOLDER = os.path.join(ROOT_FOLDER, "outputs", "plots")
DEFAULT_SANKEY_FILE = "sankey_nodes.csv"


# -----------------------------
# MAIN GUI
# -----------------------------
class SXS_GUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Supersonic Tools")
        self.geometry("500x730")
        self.resizable(False, False)
        self.configure(bg="#F5F5F5")
        self.create_widgets()

    def create_widgets(self):
        tk.Label(self, text="Projecte SuperSònic",
                 font=("Inter", 24, "bold"),
                 bg="#F5F5F5", fg="#0B5394").pack(pady=15)

        tk.Button(self, text="Batch plot", command=self.run_batch_plots).pack(pady=5)

        self.status_var = tk.StringVar(value="Ready")
        tk.Label(self, textvariable=self.status_var,
                 relief="sunken", anchor="w").pack(side="bottom", fill="x")


    # -----------------------------
    # MULTI-SELECT COLUMN PICKER (FIXED + SCROLLABLE)
    # -----------------------------
    def ask_magnitude_column(self, columns):
        top = tk.Toplevel(self)
        top.title("Select magnitude columns")
        top.geometry("400x500")

        tk.Label(top, text="Select one or more variables:").pack()

        container = tk.Frame(top)
        container.pack(fill="both", expand=True)

        canvas = tk.Canvas(container)
        scrollbar = tk.Scrollbar(container, orient="vertical", command=canvas.yview)

        frame = tk.Frame(canvas)

        frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Mouse wheel support
        def _wheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

        canvas.bind_all("<MouseWheel>", _wheel)

        vars_map = {}
        for col in columns:
            v = tk.BooleanVar()
            tk.Checkbutton(frame, text=col, variable=v).pack(anchor="w")
            vars_map[col] = v

        result = {"cols": []}

        def submit():
            result["cols"] = [c for c, v in vars_map.items() if v.get()]
            top.destroy()

        tk.Button(top, text="OK", command=submit).pack(pady=10)

        top.grab_set()
        top.wait_window()

        return result["cols"]


    # -----------------------------
    # BATCH PLOT
    # -----------------------------
    def run_batch_plots(self):
        import create_plots

        folder_path = filedialog.askdirectory(initialdir=DEFAULT_PLOT_FOLDER)
        if not folder_path:
            return

        csv_files = [f for f in os.listdir(folder_path) if f.lower().endswith(".csv")]
        if not csv_files:
            messagebox.showerror("Error", "No CSV files found")
            return

        # IMPORTANT: use first file only as sample (OK for selection UI)
        sample_path = os.path.join(folder_path, csv_files[0])
        sample_df = pd.read_csv(sample_path, sep="\t")

        sample_df.columns = sample_df.columns.str.strip()

        selected_vars = self.ask_magnitude_column(sample_df.columns)

        if not selected_vars:
            messagebox.showinfo("Cancelled", "No variables selected")
            return

        self.status_var.set("Generating plots...")
        self.update()

        create_plots.batch_plot(
            folder_path,
            DEFAULT_PLOT_FOLDER,
            selected_vars
        )

        self.status_var.set("Done")


    # -----------------------------
    # DOCS
    # -----------------------------
    def open_docs_folder(self):
        os.startfile(DOCS_FOLDER)


if __name__ == "__main__":
    app = SXS_GUI()
    app.mainloop()