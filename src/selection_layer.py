from PyQt5.QtWidgets import (QApplication, QDialog, QVBoxLayout, QHBoxLayout, 
                           QLabel, QListWidget, QListWidgetItem, QCheckBox, 
                           QPushButton, QFileDialog, QMessageBox, QScrollArea, 
                           QMainWindow, QWidget, QFrame)
from PyQt5.QtCore import Qt

import pandas as pd
import os
import sys
import time
import webbrowser
import create_sankey # Mantenim aquest, és per als diagrames Sankey
import excel2js # Importem el nou script excel2js
import create_map
import create_plots
import excel2csv
from pathlib import Path
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from config import (DATA_PUNTS, DATA_SANKEY, DATA_RAW, OUTPUT_PLOTS, 
                    DATA_PLANOL, OUTPUT_MAPA_AT, OUTPUT_MAPA_STE)

# =========================================================
# FILE / FOLDER HELPERS
# =========================================================
def ask_file(initial_dir, title="Select file", filetypes=None):
    if hasattr(initial_dir, 'resolve'):  # pathlib.Path
        initial_dir = str(initial_dir)
    elif initial_dir is None:
        initial_dir = "."
    filetypes = filetypes or [("CSV files", "*.csv"), ("PNG files", "*.png"), ("All files", "*.*")]
    filter_str = ";;".join([f"{desc} ({pattern})" for desc, pattern in filetypes])
    result = QFileDialog.getOpenFileName(None, title, initial_dir, filter_str)
    return result[0]

def ask_folder(initial_dir, title="Select folder"):
    if hasattr(initial_dir, 'resolve'):
        initial_dir = str(initial_dir)
    elif initial_dir is None:
        initial_dir = "."
  
    dialog = QFileDialog(None, Qt.Dialog | Qt.WindowCloseButtonHint)  # <- FIXED
    dialog.setWindowTitle(title)
    dialog.setDirectory(initial_dir)
    
    # KEY SETTINGS:
    dialog.setFileMode(QFileDialog.Directory)           # Folder selection ONLY
    dialog.setOption(QFileDialog.ShowDirsOnly, False)   # Show files too (gray)
    dialog.setViewMode(QFileDialog.Detail)              # List + size/type columns
    dialog.setOption(QFileDialog.DontUseNativeDialog, True)  # <- CRITICAL: Use Qt dialog
    
    result = dialog.exec_()
    if result == QDialog.Accepted:
        return dialog.selectedFiles()[0]
    return ""

def ask_file_from_list(root, files, title="Select file"):
    dialog = QDialog(root)
    dialog.setWindowTitle(title)
    dialog.setFixedSize(400, 400)
    
    layout = QVBoxLayout()
    
    layout.addWidget(QLabel("Select a CSV file:"))
    
    list_widget = QListWidget()
    for f in files:
        list_widget.addItem(QListWidgetItem(f))
    list_widget.setCurrentRow(0)
    layout.addWidget(list_widget)
    
    ok_btn = QPushButton("OK")
    ok_btn.clicked.connect(dialog.accept)
    layout.addWidget(ok_btn)
    
    dialog.setLayout(layout)
    dialog.exec_()
    
    if list_widget.currentRow() >= 0:
        return list_widget.currentItem().text()
    return None

# =========================================================
# MULTI COLUMN SELECTOR (CHECKBOXES)
# =========================================================
def ask_magnitude_columns(root, columns, title="Select columns"):
    dialog = QDialog(root)
    dialog.setWindowTitle(title)
    dialog.resize(400, 500)
    
    layout = QVBoxLayout()
    layout.addWidget(QLabel("Select one or more columns:"))
    
    scroll = QScrollArea()
    scroll_widget = QWidget()
    scroll_layout = QVBoxLayout(scroll_widget)
    
    checkboxes = {}
    for col in columns:
        cb = QCheckBox(col)
        checkboxes[col] = cb
        scroll_layout.addWidget(cb)
    
    scroll.setWidget(scroll_widget)
    scroll.setWidgetResizable(True)
    layout.addWidget(scroll)
    
    result = []
    
    def submit():
        nonlocal result
        result = [col for col, cb in checkboxes.items() if cb.isChecked()]
        dialog.accept()
    
    ok_btn = QPushButton("OK")
    ok_btn.clicked.connect(submit)
    layout.addWidget(ok_btn)
    
    dialog.setLayout(layout)
    dialog.exec_()
    
    return result

# =========================================================
# SANKEY
# =========================================================
def run_sankey(root):
    run_excel2csv(DATA_SANKEY)
    file_path = ask_file(DATA_SANKEY, "Select Sankey file")
    
    if not file_path:
        return
    
    df = create_sankey.load_file(file_path)
    cols = ask_magnitude_columns(root, df.columns.tolist(), "Sankey magnitudes")
    
    if not cols:
        QMessageBox.warning(None, "Warning", "No columns selected")
        return
    
    create_sankey.main_sankey(
        file_path=file_path, 
        magnitude_col=cols[0]
    )

# =========================================================
# MAP (MULTI MAGNITUDE SUPPORT)
# =========================================================

def run_map(root):
    run_excel2csv(DATA_PUNTS)
    map_file = ask_file(DATA_PLANOL, "Tria una imatge de fons", [("PNG files", "*.png"), ("All files", "*.*")])
    if not map_file:
        return
    
    file_path = ask_file(DATA_PUNTS, "Arxiu dels punts de mesura")
    if not file_path:
        return
    
    try:
        df = create_map.load_measure_points(file_path)  # From create_pyqt
    except:
        df = pd.read_csv(file_path)
    
    cols = ask_magnitude_columns(root, df.columns.tolist(), "Map magnitudes")
    if not cols:
        QMessageBox.warning(None, "Warning", "No columns selected")
        return
    
    # Pure PyQt5!
    dialog = create_map.Visualizer(map_file, file_path, cols)
    dialog.show()

# =========================================================
# PLOTS
# =========================================================
def run_preview_plot(root):
    # Directly ask for a CSV file, allowing the user to navigate from DATA_RAW
    file_path = ask_file(DATA_RAW, "Select CSV to plot", [("CSV files", "*.csv")])
    
    if not file_path: # User cancelled file selection
        return
    
    # Load the selected CSV file
    df = create_plots.load_csv(file_path)
    
    # Handle potential errors during CSV loading
    if df is None:
        QMessageBox.critical(None, "Error", "Could not load file")
        return
    
    cols = ask_magnitude_columns(root, df.columns.tolist(), "Select magnitudes")
    if not cols:
        return
    
    # Create and show a plot for each selected column
    for col in cols:
        fig = create_plots.plot_preview_plot(file_path, col)
        if fig is not None:
            show_preview_window(root, fig, file_path, col)

def show_preview_window(root, fig, csv_path, variable):
    dialog = QDialog(root)
    dialog.setWindowTitle(f"Preview: {variable}")
    dialog.resize(800, 600)
    
    layout = QVBoxLayout()
    
    canvas = FigureCanvas(fig)
    layout.addWidget(canvas)
    
    btn_layout = QHBoxLayout()
    
    save_btn = QPushButton("Save")
    def save():
        filename = f"{Path(csv_path).stem}_{variable}.png"
        output_path = Path(OUTPUT_PLOTS) / filename
        fig.savefig(output_path, dpi=300, bbox_inches='tight')
        QMessageBox.information(None, "Saved", f"Saved to:\n{output_path}")
    
    discard_btn = QPushButton("Discard")
    def discard():
        plt.close(fig)
        dialog.close()
    
    save_btn.clicked.connect(save)
    discard_btn.clicked.connect(discard)
    
    btn_layout.addWidget(save_btn)
    btn_layout.addWidget(discard_btn)
    layout.addLayout(btn_layout)
    
    dialog.setLayout(layout)
    dialog.exec_()
    plt.close(fig)

def run_batch_plots_folder(root):
    folder = ask_folder(DATA_RAW, "Select folder with CSVs")
    if not folder:
        return
    
    files = [f for f in os.listdir(folder) if f.endswith(".csv")]
    if not files:
        QMessageBox.critical(None, "Error", "No s'han trobat CSVs")
        return
    
    # Get ALL unique columns across ALL files
    all_columns = set()
    
    for file in files:
        file_path = os.path.join(folder, file)
        try:
            df = create_plots.load_csv(file_path)
            if df is not None:
                all_columns.update(df.columns)
        except:
            continue  # Skip broken files
    
    if not all_columns:
        QMessageBox.critical(None, "Error", "No columns found in any file")
        return
    
    # User selects from ALL available columns
    cols = ask_magnitude_columns(root, sorted(list(all_columns)), "Available columns (across all files)")
    if not cols:
        return
    
    # Pass folder and selected columns (skips missing columns per file)
    create_plots.batch_plot(folder, str(OUTPUT_PLOTS), variables=cols)

def run_excel2csv(folder):
    excel2csv.main(folder)

def run_excel2js_for_map(map_type: str):
    excel2js.main(map_type)

def run_excel2csv_button(root):
    import subprocess
    script_path = Path(__file__).parent / "excel2csv.py"
    subprocess.run([sys.executable, str(script_path)])

def run_excel2js_button(root):
    import subprocess
    script_path = Path(__file__).parent / "excel2js.py"
    subprocess.run([sys.executable, str(script_path)])

def run_html_map(root):
    msg = QMessageBox(root)
    msg.setWindowTitle("Seleccionar Mapa HTML")
    msg.setText("Quin mapa vols obrir al navegador?")
    at_btn = msg.addButton("Aigua de Torres (AT)", QMessageBox.ActionRole)
    ste_btn = msg.addButton("Vapor (STE)", QMessageBox.ActionRole)
    msg.addButton("Cancel·lar", QMessageBox.RejectRole)
    
    msg.exec_()
    
    if msg.clickedButton() == at_btn:
        run_excel2js_for_map("AT") # Genera points.js per a Aigua de Torres
        path = OUTPUT_MAPA_AT / "index.html"
    elif msg.clickedButton() == ste_btn:
        run_excel2js_for_map("STE") # Genera points.js per a Vapor
        path = OUTPUT_MAPA_STE / "index.html"
    else:
        return

    if path.exists():
        webbrowser.open(path.as_uri())
    else:
        QMessageBox.warning(root, "Error", f"No s'ha trobat el fitxer:\n{path}")

# =========================================================
# SERIAL INTEGRATION
# =========================================================
def run_serial_import(root):
    import subprocess
    script_path = Path(__file__).parent / "serial_import.py"
    
    # Start the process
    proc = subprocess.Popen([sys.executable, str(script_path)])
    
    # Create a modal dialog to keep the UI "frozen" but allowing a "Stop" button
    msg = QMessageBox(root)
    msg.setIcon(QMessageBox.Information)
    msg.setWindowTitle("Importació en curs")
    msg.setText("S'està esperant la transmissió del dispositiu...")
    msg.setInformativeText("Un cop detectat el flux de dades (Header \\DEVICE), el fitxer es crearà i es tancarà sol.\n\nPots forçar la finalització amb el botó d'aquí sota.")
    stop_btn = msg.addButton("Finalitzar / Aturar", QMessageBox.RejectRole)
    msg.setModal(True)
    msg.show()

    # Wait for process or user stop
    while proc.poll() is None:
        QApplication.processEvents() # Keep the "Stop" button responsive
        if msg.clickedButton() == stop_btn:
            proc.terminate()
            break
        time.sleep(0.1)
    
    msg.accept()
    
    if proc.returncode == 0:
        QMessageBox.information(root, "Èxit", "Importació finalitzada i fitxer processat correctament.") # Keep this message
    else:
        QMessageBox.warning(root, "Informació", "El procés d'importació s'ha aturat manualment o per timeout.")

def run_serial_monitor(root):
    import subprocess
    script_path = Path(__file__).parent / "serial_read.py"
    # For a raw monitor, we open it in a separate console window for better visibility
    if sys.platform == "win32":
        subprocess.Popen(["cmd", "/c", "start", sys.executable, str(script_path)])
    else:
        subprocess.Popen([sys.executable, str(script_path)])

# Keep main for backward compatibility
def main(func):
    app = QApplication.instance() or QApplication([])
    # Create dummy root if needed
    root = QMainWindow()
    root.setWindowTitle("SXS Tools Helper")
    root.hide()
    func(root)
    root.close()