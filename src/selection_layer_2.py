import tkinter as tk
from tkinter import filedialog, messagebox
import pandas as pd
import os
import create_sankey
import create_tkinter
import create_plots
from pathlib import Path
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from config import DATA_PUNTS, DATA_SANKEY, DATA_RAW, OUTPUT_PLOTS, DATA_PLANOL

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

def ask_file_from_list(root, files, title="Select file"):
    top = tk.Toplevel(root)
    top.title(title)
    top.geometry("300x400")

    tk.Label(top, text="Select a CSV file:").pack(pady=5)

    var = tk.StringVar(value=files[0])

    lb = tk.Listbox(top)
    lb.pack(fill="both", expand=True)

    for f in files:
        lb.insert(tk.END, f)

    def submit():
        selection = lb.curselection()
        if selection:
            var.set(files[selection[0]])
        top.destroy()

    tk.Button(top, text="OK", command=submit).pack(pady=5)

    top.grab_set()
    root.wait_window(top)

    return var.get()

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
    run_excel2csv()
    file_path = ask_file(
        DATA_SANKEY,
        "Select Sankey file",
        [("All files", "*.*")]
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
    map_file = ask_file(
        DATA_PLANOL,
        "Tria una imatge de fons",
        [("All files", "*.*")]
    )

    if not map_file:
        return
    

    file_path = ask_file(
        DATA_PUNTS,
        "Arxiu dels punts de mesura",
        [("All files", "*.*")]
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
        img_file=map_file,
        csv_file=file_path,
        magnitude_cols=cols
    )

# =========================================================
# PLOTS
# =========================================================
def run_preview_plot(root):
    folder = ask_folder(DATA_RAW, "Select folder with CSVs")

    if not folder:
        return

    files = [f for f in os.listdir(folder) if f.endswith(".csv")]

    if not files:
        messagebox.showerror("Error", "No CSVs found")
        return

    file = ask_file_from_list(root, files, title="Select CSV to plot")

    if not file:
        return

    file_path = os.path.join(folder, file)

    df = create_plots.load_csv(file_path)

    if df is None:
        messagebox.showerror("Error", "Could not load file")
        return

    cols = ask_magnitude_columns(root, df.columns, "Select magnitudes")

    if not cols:
        return

    # ONE AT A TIME PREVIEW
    for col in cols:
        fig = create_plots.plot_preview_plot(file_path, col)

        if fig is not None:
            show_preview_window(root, fig, file_path, col)

def show_preview_window(root, fig, csv_path, variable):
    win = tk.Toplevel(root)
    win.title(f"Preview: {variable}")

    canvas = FigureCanvasTkAgg(fig, master=win)
    canvas.draw()
    canvas.get_tk_widget().pack(fill="both", expand=True)

    def save():
        filename = f"{Path(csv_path).stem}_{variable}.png"
        output_path = Path(OUTPUT_PLOTS) / filename
        fig.savefig(output_path, dpi=300)
        messagebox.showinfo("Saved", f"Saved to:\n{output_path}")
        plt.close(fig)

    def discard():
        win.destroy()
        plt.close(fig)

    btn_frame = tk.Frame(win)
    btn_frame.pack(pady=10)

    tk.Button(btn_frame, text="Save", command=save).pack(side="left", padx=5)
    tk.Button(btn_frame, text="Discard", command=discard).pack(side="left", padx=5)

def run_batch_plots_folder(root):
    folder = ask_folder(DATA_RAW, "Select folder with CSVs")

    if not folder:
        return

    files = [f for f in os.listdir(folder) if f.endswith(".csv")]

    if not files:
        messagebox.showerror("Error", "No s'han trobat CSVs")
        return

    sample_path = os.path.join(folder, files[0])
    sample_df = create_plots.load_csv(sample_path)

    if sample_df is None:
        messagebox.showerror("Error", "Could not load sample file")
        return

    cols = ask_magnitude_columns(root, sample_df.columns, "Plot magnitudes")

    if not cols:
        return

    create_plots.batch_plot(folder, OUTPUT_PLOTS, variables=cols)

def run_excel2csv():
        import subprocess       
        subprocess.run(["python", "excel2csv.py"])

def main(func):
    root = tk.Tk()
    root.withdraw()
    root.protocol("WM_DELETE_WINDOW", root.destroy)
    root.after(0, lambda: func(root))
    root.mainloop()
    plt.close('all')
    print("GUI done, script exiting")   # <- add this line

if __name__ == "__main__":
    main(run_map)

### functions: run_sankey, run_map, run_preview_plot, run_batch_plots_folder