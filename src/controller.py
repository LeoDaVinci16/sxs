from PyQt5.QtWidgets import (QApplication, QDialog, QVBoxLayout, QHBoxLayout, 
                           QLabel, QListWidget, QListWidgetItem, QCheckBox, 
                           QPushButton, QFileDialog, QMessageBox, QScrollArea, 
                           QMainWindow, QWidget, QFrame, QProgressDialog)
from PyQt5.QtCore import Qt

import pandas as pd
import os
import sys
import time
import subprocess
import webbrowser
import create_network
import create_sankey 
import excel2js 
import create_map
import create_plots
import create_boxplots
import excel2csv
from pathlib import Path
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from config import (at_punts_data as DATA_PUNTS, at_sankey_data as DATA_SANKEY, DATA_RAW, at_plots as OUTPUT_PLOTS, 
                    at_planol_data as DATA_PLANOL, OUTPUT_MAPA_AT, OUTPUT_MAPA_STE, at_boxplots as OUTPUT_BOXPLOTS, at_network_data as DATA_NETWORK, ROOT)

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
  
    dialog = QFileDialog(None, Qt.Dialog | Qt.WindowCloseButtonHint)
    dialog.setWindowTitle(title)
    dialog.setDirectory(initial_dir)
    
    dialog.setFileMode(QFileDialog.Directory)           
    dialog.setOption(QFileDialog.ShowDirsOnly, False)   
    dialog.setViewMode(QFileDialog.Detail)              
    dialog.setOption(QFileDialog.DontUseNativeDialog, True)  
    
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
# NETWORK
# =========================================================
def run_network(root):
    run_excel2csv(DATA_NETWORK)
    
    edges_file = ask_file(DATA_NETWORK, "Selecciona l'arxiu de branques (edges)", [("CSV files", "*.csv")])
    if not edges_file:
        return
    
    df_edges = pd.read_csv(edges_file)
    cols = ask_magnitude_columns(root, df_edges.columns.tolist(), "Selecciona la magnitud del flux")
    if not cols:
        QMessageBox.warning(None, "Atenció", "No s'ha seleccionat cap columna de dades")
        return
        
    nodes_file = os.path.join(os.path.dirname(edges_file), "nodes.csv")
    if not os.path.exists(nodes_file):
        nodes_file = ask_file(DATA_NETWORK, "Selecciona l'arxiu de nodes", [("CSV files", "*.csv")])
        if not nodes_file:
            return

    html_path = create_network.main_network(nodes_file, edges_file, cols[0])
    
    output_dir = ROOT / "outputs" / "network"
    output_dir.mkdir(parents=True, exist_ok=True)
    target_path = output_dir / html_path.name

    if html_path.exists():
        html_path.replace(target_path)
        webbrowser.open(target_path.as_uri())
    else:
        QMessageBox.warning(root, "Error", f"No s'ha trobat el fitxer:\n{html_path}")

# =========================================================
# MAP
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
        df = create_map.load_measure_points(file_path)  
    except:
        df = pd.read_csv(file_path)
    
    cols = ask_magnitude_columns(root, df.columns.tolist(), "Map magnitudes")
    if not cols:
        QMessageBox.warning(None, "Warning", "No columns selected")
        return
    
    dialog = create_map.Visualizer(map_file, file_path, cols)
    dialog.show()

# =========================================================
# PLOTS
# =========================================================
def run_preview_plot(root):
    file_path = ask_file(DATA_RAW, "Select CSV to plot", [("CSV files", "*.csv")])
    
    if not file_path:
        return
    
    df = create_plots.load_csv(file_path)
    
    if df is None:
        QMessageBox.critical(None, "Error", "Could not load file")
        return
    
    cols = ask_magnitude_columns(root, df.columns.tolist(), "Select magnitudes")
    if not cols:
        return
    
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
        filename = f"{Path(csv_path).stem}_{create_plots.safe_filename(variable)}.png"
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
    
    all_columns = set()
    
    for file in files:
        file_path = os.path.join(folder, file)
        try:
            df = create_plots.load_csv(file_path)
            if df is not None:
                all_columns.update(df.columns)
        except:
            continue  
    
    if not all_columns:
        QMessageBox.critical(None, "Error", "No columns found in any file")
        return
    
    cols = ask_magnitude_columns(root, sorted(list(all_columns)), "Available columns (across all files)")
    if not cols:
        return
    
    create_plots.batch_plot(folder, str(OUTPUT_PLOTS), variables=cols)

def run_preview_boxplot(root):
    file_path = ask_file(DATA_RAW, "Select CSV for Boxplot", [("CSV files", "*.csv")])
    
    if not file_path:
        return
    
    df = create_plots.load_csv(file_path)
    
    if df is None:
        QMessageBox.critical(None, "Error", "Could not load file")
        return
    
    cols = ask_magnitude_columns(root, df.columns.tolist(), "Select magnitudes for Boxplot")
    if not cols:
        return
    
    for col in cols:
        fig = create_boxplots.plot_preview_boxplot(file_path, col)
        if fig is not None:
            show_preview_boxplot_window(root, fig, file_path, col)

def show_preview_boxplot_window(root, fig, csv_path, variable):
    dialog = QDialog(root)
    dialog.setWindowTitle(f"Boxplot Preview: {variable}")
    dialog.resize(800, 600)
    
    layout = QVBoxLayout()
    
    canvas = FigureCanvas(fig)
    layout.addWidget(canvas)
    
    btn_layout = QHBoxLayout()
    
    save_btn = QPushButton("Save")
    def save():
        filename = f"{Path(csv_path).stem}_boxplot_{create_boxplots.safe_filename(variable)}.png"
        output_path = Path(OUTPUT_BOXPLOTS) / filename
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

def run_batch_boxplots_folder(root):
    folder = ask_folder(DATA_RAW, "Select folder with CSVs for Boxplots")
    if not folder:
        return
    
    files = [f for f in os.listdir(folder) if f.endswith(".csv")]
    if not files:
        QMessageBox.critical(None, "Error", "No s'han trobat CSVs")
        return
    
    all_columns = set()
    
    for file in files:
        file_path = os.path.join(folder, file)
        try:
            df = create_plots.load_csv(file_path)
            if df is not None:
                all_columns.update(df.columns)
        except:
            continue  
    
    if not all_columns:
        QMessageBox.critical(None, "Error", "No columns found in any file")
        return
    
    cols = ask_magnitude_columns(root, sorted(list(all_columns)), "Available columns (across all files)")
    if not cols:
        return
    
    create_boxplots.batch_boxplot(folder, str(OUTPUT_BOXPLOTS), variables=cols)

def run_excel2csv(folder):
    excel2csv.main(folder)

def run_excel2js_for_map(map_type: str):
    excel2js.main(map_type)

def run_excel2csv_button(root):
    script_path = Path(__file__).parent / "excel2csv.py"
    subprocess.run([sys.executable, str(script_path)])

def run_excel2js_button(root):
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
        run_excel2js_for_map("AT") 
        path = OUTPUT_MAPA_AT / "index.html"
    elif msg.clickedButton() == ste_btn:
        run_excel2js_for_map("STE") 
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
    script_path = Path(__file__).parent / "serial_import.py"
    
    proc = subprocess.Popen([sys.executable, str(script_path)])
    
    msg = QMessageBox(root)
    msg.setIcon(QMessageBox.Information)
    msg.setWindowTitle("Importació en curs")
    msg.setText("S'està esperant la transmissió del dispositiu...")
    msg.setInformativeText("Un cop detectat el flux de dades (Header \\DEVICE), el fitxer es crearà i es tancarà sol.\n\nPots forçar la finalització amb el botó d'aquí sota.")
    stop_btn = msg.addButton("Finalitzar / Aturar", QMessageBox.RejectRole)
    msg.setModal(True)
    msg.show()

    while proc.poll() is None:
        QApplication.processEvents() 
        if msg.clickedButton() == stop_btn:
            proc.terminate()
            break
        time.sleep(0.1)
    
    msg.accept()
    
    if proc.returncode == 0:
        QMessageBox.information(root, "Èxit", "Importació finalitzada i fitxer processat correctament.") 
    else:
        QMessageBox.warning(root, "Informació", "El procés d'importació s'ha aturat manualment o per timeout.")

def run_serial_monitor(root):
    script_path = Path(__file__).parent / "serial_read.py"
    if sys.platform == "win32":
        subprocess.Popen(["cmd", "/c", "start", sys.executable, str(script_path)])
    else:
        subprocess.Popen([sys.executable, str(script_path)])

def run_create_report(root):
    script_path = Path(__file__).parent / "create_report.py"
    
    msg = QMessageBox(root)
    msg.setIcon(QMessageBox.Information)
    msg.setWindowTitle("Generant Informe PDF")
    msg.setText("S'està generant l'informe PDF. Això pot trigar uns minuts...")
    msg.setInformativeText("Si us plau, espera. Pots cancel·lar el procés, però l'informe podria quedar incomplet.")
    
    cancel_button = msg.addButton("Cancel·lar", QMessageBox.RejectRole)
    msg.setStandardButtons(QMessageBox.NoButton) 
    msg.setModal(True)
    msg.show()

    process = None
    try:
        process = subprocess.Popen([sys.executable, str(script_path)], 
                                   stdout=subprocess.PIPE, 
                                   stderr=subprocess.PIPE,
                                   text=True,
                                   encoding='utf-8') 
        
        while process.poll() is None:
            QApplication.processEvents() 
            if msg.clickedButton() == cancel_button:
                process.terminate() 
                process.wait() 
                QMessageBox.warning(root, "Cancel·lat", "La generació de l'informe ha estat cancel·lada.")
                msg.close()
                return
            time.sleep(0.1) 

        stdout, stderr = process.communicate() 
        
        if process.returncode == 0:
            QMessageBox.information(root, "Èxit", "L'informe PDF s'ha generat correctament a 'outputs/informe/report.pdf'.")
        else:
            error_message = f"La generació de l'informe ha fallat amb el codi {process.returncode}.\n"
            if stderr:
                error_message += f"Error: {stderr.strip()}"
            QMessageBox.critical(root, "Error", error_message)

    except Exception as e:
        QMessageBox.critical(root, "Error Inesperat", f"S'ha produït un error inesperat: {e}")
    finally:
        if process and process.poll() is None: 
            process.terminate()
            process.wait()
        msg.close() 

def main(func):
    app = QApplication.instance() or QApplication([])
    root = QMainWindow()
    root.setWindowTitle("SXS Tools Helper")
    root.hide()
    func(root)
    root.close()