import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import os
import subprocess
from pathlib import Path
import sys

# -----------------------------
# Paths & defaults
# -----------------------------
ROOT_FOLDER = Path(__file__).parents[1]
DOCS_FOLDER = os.path.join(ROOT_FOLDER, "docs")
CSV_FOLDER = os.path.join(ROOT_FOLDER, "data", "csv")
DATA_FOLDER = os.path.join(ROOT_FOLDER, "data", "raw")

DEFAULT_MAP_IMG = "planol.png"
DEFAULT_MAP_EXCEL = "punts-mesura.xlsx"
DEFAULT_PLOT_FOLDER = os.path.join(ROOT_FOLDER, "data", "raw")
DEFAULT_SANKEY_FILE = "sankey_nodes.csv"


# -----------------------------
# Main GUI
# -----------------------------
class SXS_GUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Supersonic Tools")
        self.geometry("500x600")
        self.resizable(False, False)
        self.configure(bg="#F5F5F5")
        self.create_widgets()

    def create_widgets(self):
        # Title
        tk.Label(self, text="Projecte SuperSònic", font=("Inter", 24, "bold"), bg="#F5F5F5", fg="#0B5394").pack(pady=15)

        # -----------------------------
        # Tasks frame
        # -----------------------------
        tasks_frame = tk.LabelFrame(self, text="Tasques", font=("Inter", 14, "bold"), fg="#0B5394", padx=15, pady=10)
        tasks_frame.pack(fill="x", padx=20, pady=(0,10))

        btn_style = {"width": 25, "height": 2, "bg": "#4CAF50", "fg": "white", "font": ("Inter", 11, "bold")}

        tk.Button(tasks_frame, text="Plots", command=self.run_plots, **btn_style).pack(pady=5)
        tk.Button(tasks_frame, text="Euromed Map", command=self.run_map, **btn_style).pack(pady=5)
        tk.Button(tasks_frame, text="Sankey Diagram", command=self.run_sankey, **btn_style).pack(pady=5)

        # -----------------------------
        # Tools frame
        # -----------------------------
        tools_frame = tk.LabelFrame(self, text="Eines addicionals", font=("Inter", 14, "bold"), fg="#0B5394", padx=15, pady=10)
        tools_frame.pack(fill="x", padx=20, pady=(0,10))

        tool_btn_style = {"width": 25, "height": 2, "bg": "#2196F3", "fg": "white", "font": ("Inter", 11, "bold")}

        tk.Button(tools_frame, text="Add Date", command=self.run_add_date, **tool_btn_style).pack(pady=5)
        tk.Button(tools_frame, text="Excel → CSV", command=self.run_excel2csv, **tool_btn_style).pack(pady=5)
        tk.Button(tools_frame, text="Obre carpeta docs", command=self.open_docs_folder, **tool_btn_style).pack(pady=5)

        # -----------------------------
        # Status bar
        # -----------------------------
        self.status_var = tk.StringVar(value="Ready")
        tk.Label(self, textvariable=self.status_var, relief="sunken", anchor="w", bg="#E0E0E0").pack(side="bottom", fill="x")

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
        top.geometry("300x200")
        tk.Label(top, text="Select magnitude column:", font=("Inter", 12)).pack(pady=5)

        col_var = tk.StringVar(value=default)
        for col in columns:
            tk.Radiobutton(top, text=col, variable=col_var, value=col, font=("Inter", 11)).pack(anchor="w", padx=20)

        result = {}

        def submit():
            result["column"] = col_var.get()
            top.destroy()

        tk.Button(top, text="OK", command=submit, font=("Inter", 11, "bold"), bg="#4CAF50", fg="white").pack(pady=10)
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
            self.status_var.set(f"Running {script_name}...")
            self.update()
            subprocess.run([sys.executable, script_path, *args], check=True)
            self.status_var.set(f"Finished {script_name}")
        except subprocess.CalledProcessError as e:
            messagebox.showerror("Error", f"Error executant {script_name}:\n{e}")
            self.status_var.set("Error occurred")

    # -----------------------------
    # Tasks
    # -----------------------------
    def run_map(self):
        excel_file = self.ask_file(DEFAULT_MAP_EXCEL, [("CSV or Excel", "*.csv *.xlsx *.xls")])
        if not excel_file:
            return

        try:
            import create_map
        except Exception as e:
            messagebox.showerror("Import Error", f"Failed to import create_map:\n{e}")
            return

        try:
            if excel_file.lower().endswith(".csv"):
                import pandas as pd
                df = pd.read_csv(excel_file)
            else:
                df = create_map.load_measure_points(excel_file)
        except Exception as e:
            messagebox.showerror("Load Error", f"Failed to load data:\n{e}")
            return

        magnitude_col = self.ask_magnitude_column(df.columns, default="DN")

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