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
import excel2csv
from pathlib import Path
import config

# =========================================================
# FILE / FOLDER HELPERS
# =========================================================
def ask_system(root):
    """Mètode robust per triar el sistema de treball (AT o STE)."""
    msg = QMessageBox(root)
    msg.setWindowTitle("Seleccionar Sistema")
    msg.setText("Amb quin sistema vols treballar?")
    at_btn = msg.addButton("Aigua de Torres (AT)", QMessageBox.ActionRole)
    ste_btn = msg.addButton("Vapor (STE)", QMessageBox.ActionRole)
    msg.addButton("Cancel·lar", QMessageBox.RejectRole)
    
    msg.exec_()
    
    if msg.clickedButton() == at_btn:
        return "AT"
    elif msg.clickedButton() == ste_btn:
        return "STE"
    return None

def ask_file(initial_dir, title="Select file", filetypes=None):
    if hasattr(initial_dir, 'resolve'):  # pathlib.Path
        initial_dir = str(initial_dir)
    if initial_dir is None or initial_dir == "":
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
    sys_type = ask_system(root)
    if not sys_type: return

    data_dir = config.at_sankey_data if sys_type == "AT" else config.ste_sankey_data
    run_excel2csv(data_dir)
    file_path = ask_file(data_dir, f"Selecciona fitxer Sankey ({sys_type})")
    
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
    sys_type = ask_system(root)
    if not sys_type: return

    data_dir = config.at_network_data if sys_type == "AT" else config.ste_network_data
    run_excel2csv(data_dir)
    
    edges_file = ask_file(data_dir, f"Branques (edges) de {sys_type}", [("CSV files", "*.csv")])
    if not edges_file:
        return
    
    df_edges = pd.read_csv(edges_file)
    cols = ask_magnitude_columns(root, df_edges.columns.tolist(), "Selecciona la magnitud del flux")
    if not cols:
        QMessageBox.warning(None, "Atenció", "No s'ha seleccionat cap columna de dades")
        return
        
    suffix = "at" if sys_type == "AT" else "ste"
    nodes_file = os.path.join(os.path.dirname(edges_file), f"nodes-{suffix}.csv")
    if not os.path.exists(nodes_file):
        nodes_file = ask_file(data_dir, f"Nodes de {sys_type} (nodes-{suffix}.csv)", [("CSV files", "*.csv")])
        if not nodes_file:
            return

    target_dir = config.at_network_output if sys_type == "AT" else config.ste_network_output
    target_dir.mkdir(parents=True, exist_ok=True)

    html_path = create_network.main_network(nodes_file, edges_file, cols[0])
    
    target_path = target_dir / html_path.name

    if html_path.exists():
        html_path.replace(target_path)
        webbrowser.open(target_path.as_uri())
    else:
        QMessageBox.warning(root, "Error", f"No s'ha trobat el fitxer:\n{html_path}")

# =========================================================
# MAP
# =========================================================

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
    sys_type = ask_system(root)
    if sys_type == "AT":
        run_excel2js_for_map("AT") 
        path = config.at_mapa_output / "index.html"
    elif sys_type == "STE":
        run_excel2js_for_map("STE") 
        path = config.ste_mapa_output / "index.html"
    else:
        return

    if path.exists():
        webbrowser.open(path.as_uri())
    else:
        QMessageBox.warning(root, "Error", f"No s'ha trobat el fitxer:\n{path}")

def main(func):
    app = QApplication.instance() or QApplication([])
    root = QMainWindow()
    root.setWindowTitle("SXS Tools Helper")
    root.hide()
    func(root)
    root.close()