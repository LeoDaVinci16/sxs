import tkinter as tk
from tkinter import filedialog, messagebox
import os
import subprocess
from pathlib import Path
import sys

# Paths
ROOT_FOLDER = Path(__file__).parents[1]
DOCS_FOLDER = os.path.join(ROOT_FOLDER, "docs")
CSV_FOLDER = os.path.join(ROOT_FOLDER, "data", "csv")
DATA_FOLDER = os.path.join(ROOT_FOLDER, "data", "raw")

# Defaults
DEFAULT_MAP_IMG = "planol.png"
DEFAULT_MAP_EXCEL = "punts-mesura.xlsx"
DEFAULT_PLOT_FOLDER = os.path.join(ROOT_FOLDER, "data", "raw")
DEFAULT_SANKEY_FILE = "sankey_nodes.csv"


class SXS_GUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("SXS Tools GUI")
        self.geometry("450x400")
        self.create_widgets()

    def create_widgets(self):
        tk.Label(self, text="Projecte SuperSònic", font=("Inter", 20)).pack(pady=10)

        # Task selection
        tk.Label(self, text="Tria què vols crear:").pack()
        tk.Button(self, text="Plots", width=20, command=self.run_plots).pack(pady=5)
        tk.Button(self, text="Euromed map", width=20, command=self.run_map).pack(pady=5)
        tk.Button(self, text="Sankey diagram", width=20, command=self.run_sankey).pack(pady=5)

        # Tools section
        tk.Label(self, text="Eines addicionals:").pack(pady=10)
        tk.Button(self, text="add_date", width=20, command=self.run_add_date).pack(pady=2)
        tk.Button(self, text="excel2csv", width=20, command=self.run_excel2csv).pack(pady=2)
        tk.Button(self, text="Obre carpeta als docs", width=20, command=self.open_docs_folder).pack(pady=5)

    # -----------------------------
    # Utility methods
    # -----------------------------
    def ask_file(self, default_file=None, file_types=[("All files", "*.*")]):
        file_path = filedialog.askopenfilename(initialdir=CSV_FOLDER, filetypes=file_types)
        if not file_path and default_file:
            file_path = os.path.join(CSV_FOLDER, default_file)
            if not os.path.exists(file_path):
                messagebox.showerror("Error", f"Fitxer per defecte no trobat: {file_path}")
                return None
        return file_path

    def ask_magnitude_column(self, columns, default="DN"):
        top = tk.Toplevel(self)
        top.title("Select Magnitude Column")
        tk.Label(top, text="Select magnitude column:").pack(pady=5)

        col_var = tk.StringVar(value=default)
        for col in columns:
            tk.Radiobutton(top, text=col, variable=col_var, value=col).pack(anchor="w")

        result = {}

        def submit():
            result["column"] = col_var.get()
            top.destroy()

        tk.Button(top, text="OK", command=submit).pack(pady=5)
        top.grab_set()
        top.wait_window()
        return result.get("column", default)

    def run_script(self, script_name, args=None):
        args = args or []
        script_path = os.path.join(ROOT_FOLDER, "src", script_name)
        if not os.path.exists(script_path):
            messagebox.showerror("Error", f"Script no trobat: {script_path}")
            return
        try:
            subprocess.run([sys.executable, script_path, *args], check=True)
        except subprocess.CalledProcessError as e:
            messagebox.showerror("Error", f"Error executant {script_name}:\n{e}")

    # -----------------------------
    # Tasks
    # -----------------------------
    def run_map(self):
        # Ask for file (CSV or Excel)
        excel_file = self.ask_file(DEFAULT_MAP_EXCEL, [("CSV or Excel", "*.csv *.xlsx *.xls")])
        if not excel_file:
            return

        try:
            import create_map
        except Exception as e:
            messagebox.showerror("Import Error", f"Failed to import create_map:\n{e}")
            return

        # Load the data (CSV or Excel)
        try:
            if excel_file.lower().endswith(".csv"):
                import pandas as pd
                df = pd.read_csv(excel_file)
            else:
                df = create_map.load_measure_points(excel_file)  # existing Excel loader
        except Exception as e:
            messagebox.showerror("Load Error", f"Failed to load data:\n{e}")
            return

        # Ask for magnitude column
        magnitude_col = self.ask_magnitude_column(df.columns, default="DN")

        # Run the main function
        try:
            create_map.main_file(excel_file, magnitude_col)
        except Exception as e:
            messagebox.showerror("Processing Error", f"Failed in main_file:\n{e}")


    def run_plots(self):
        folder_path = filedialog.askdirectory(initialdir=DEFAULT_PLOT_FOLDER)
        if not folder_path:
            folder_path = DEFAULT_PLOT_FOLDER
        self.run_script("create_plots.py", [folder_path])

    def run_sankey(self):
        sankey_file = self.ask_file(DEFAULT_SANKEY_FILE, [("CSV/Excel", "*.csv *.xlsx *.xls")])
        if not sankey_file:
            return
        try:
            import create_sankey
            df, _, _ = create_sankey.load_file(sankey_file)
            magnitude_col = self.ask_magnitude_column(df.columns, default="cabal")
            create_sankey.main_sankey(df, magnitude_col=magnitude_col, file_path=sankey_file)
        except Exception as e:
            messagebox.showerror("Error", str(e))

    # -----------------------------
    # Tools
    # -----------------------------
    def run_add_date(self):
        self.run_script("add_date.py")

    def run_excel2csv(self):
        self.run_script("excel2csv.py")

    def open_docs_folder(self):
        os.startfile(DOCS_FOLDER)


if __name__ == "__main__":
    app = SXS_GUI()
    app.mainloop()