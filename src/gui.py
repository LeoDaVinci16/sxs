import tkinter as tk
from tkinter import filedialog, messagebox, ttk, simpledialog
import os
import subprocess
from pathlib import Path
import sys
import os
import pandas as pd
from tkinter.filedialog import askopenfilename

# -----------------------------
# Paths & defaults
# -----------------------------
ROOT_FOLDER = Path(__file__).parents[1]
DOCS_FOLDER = os.path.join(ROOT_FOLDER, "data", "docs")
CSV_FOLDER = os.path.join(ROOT_FOLDER, "data", "docs_csv")
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
        self.geometry("500x730")
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

        tk.Button(tasks_frame, text="Batch plot", command=self.run_batch_plots, **btn_style).pack(pady=5)
        tk.Button(tasks_frame, text="Preview plot", command=self.run_prev_plots, **btn_style).pack(pady=5)
        tk.Button(tasks_frame, text="Euromed Map", command=self.run_tkinter, **btn_style).pack(pady=5)
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
        top.geometry("300x500")

        tk.Label(top, text="Select magnitude column:", font=("Inter", 12)).pack(pady=5)

        # --- Canvas + Scrollbar ---
        container = tk.Frame(top)
        container.pack(fill="both", expand=True)

        canvas = tk.Canvas(container)
        scrollbar = tk.Scrollbar(container, orient="vertical", command=canvas.yview)

        scroll_frame = tk.Frame(canvas)

        scroll_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # --- Radio buttons ---
        col_var = tk.StringVar(value=default)

        for col in columns:
            tk.Radiobutton(
                scroll_frame,
                text=col,
                variable=col_var,
                value=col,
                font=("Inter", 11)
            ).pack(anchor="w", padx=10)

        result = {}

        def submit():
            result["column"] = col_var.get()
            top.destroy()

        tk.Button(top, text="OK", command=submit,
                font=("Inter", 11, "bold"),
                bg="#4CAF50", fg="white").pack(pady=10)

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
        self.run_excel2csv
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

    DEFAULT_MAP_EXCEL = "punts-mesura.csv"  # default Excel/CSV file

    def run_tkinter(self):
        # Ask for the CSV/Excel file
        excel_file = askopenfilename(
            title="Select Excel/CSV file",
            filetypes=[("CSV or Excel", "*.csv *.xlsx *.xls")]
        )
        if not excel_file:
            return

        # Try to import the Tkinter visualizer
        try:
            import create_tkinter
        except Exception as e:
            messagebox.showerror("Import Error", f"Failed to import create_tkinter:\n{e}")
            return

        # Load the data
        try:
            if excel_file.lower().endswith(".csv"):
                df = pd.read_csv(excel_file)
            else:
                # If Excel, use load_measure_points from create_tkinter
                df = create_tkinter.load_measure_points(excel_file)
        except Exception as e:
            messagebox.showerror("Load Error", f"Failed to load data:\n{e}")
            return

        # Ask for magnitude column
        columns = df.columns.tolist()
        magnitude_col = getattr(self, "ask_magnitude_column", lambda cols, default="DN": default)(columns, default="DN")

        # Open Visualizer in a Toplevel window
        try:
            top = tk.Toplevel(self)  # use Toplevel instead of Tk
            top.title("Map Visualizer")
            visualizer = create_tkinter.Visualizer(
                top, 
                create_tkinter.DEFAULT_IMG_FILE,
                excel_file,
                magnitude_col
            )
            # No mainloop! The main app already has one running
        except Exception as e:
            messagebox.showerror("Processing Error", f"Failed to run Visualizer:\n{e}")

    def run_batch_plots(self):
        script_dir = os.path.dirname(os.path.abspath(__file__))
        plot_folder = os.path.abspath(os.path.join(script_dir, "..", "outputs", "plots"))
        import create_plots
        folder_path = filedialog.askdirectory(initialdir=DEFAULT_PLOT_FOLDER)
        if not folder_path:
            folder_path = DEFAULT_PLOT_FOLDER
        # Get a sample CSV to extract columns
        csv_files = [f for f in os.listdir(folder_path) if f.lower().endswith(".csv")]
        if not csv_files:
            messagebox.showerror("Error", "No CSV files found")
            return
        sample_df = pd.read_csv(os.path.join(folder_path, csv_files[0]), sep="\t")
        # Ask user which variable(s)
        magnitude_col = self.ask_magnitude_column(sample_df.columns, default="cabal")
        # Call function directly (no subprocess)
        create_plots.batch_plot(folder_path, plot_folder, [magnitude_col])

    def run_prev_plots(self):
        import create_plots
        folder_path = filedialog.askdirectory(initialdir=DEFAULT_PLOT_FOLDER)
        if not folder_path:
            folder_path = DEFAULT_PLOT_FOLDER
        csv_files = [f for f in os.listdir(folder_path) if f.lower().endswith(".csv")]
        if not csv_files:
            messagebox.showerror("Error", "No s'han trobat els arxius CSV")
            return
        csv_path = filedialog.askopenfilename(initialdir=folder_path, title="tria l'arxiu CSV", filetypes=[("arxius CSV", "*.csv")])
        if not csv_path or not csv_path.lower().endswith(".csv"):
            messagebox.showerror("Error", "Arxiu seleccionat invalid")
            return
        df = create_plots.load_csv(csv_path)
        sample_df = pd.read_csv(os.path.join(folder_path, csv_files[0]), sep="\t")
        magnitude_col = self.ask_magnitude_column(sample_df.columns, default="cabal")
        create_plots.preview_plot(csv_path, variables=[magnitude_col], plot_folder=DEFAULT_PLOT_FOLDER, gui=True)

    def run_sankey(self):
        self.run_excel2csv
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
