import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QPushButton, QVBoxLayout, QWidget
from PyQt5.QtCore import Qt
import selection_layer as controller

class SimpleGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SXS Tools")
        self.setFixedSize(350, 600) # Increased height for new boxplot button

        self._build_ui()

    def _build_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        layout.setAlignment(Qt.AlignCenter)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        title_label = QLabel("Eines")
        title_label.setStyleSheet("font: bold 16px Arial; margin-bottom: 5px;")
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)

        # Definim dimensions i estil comuns per als botons
        BTN_WIDTH = 300
        BTN_HEIGHT = 40
        BTN_STYLE = "font-size: 14px;"

        import_btn = QPushButton("📥 Importar dades (Serial)")
        import_btn.setFixedSize(BTN_WIDTH, BTN_HEIGHT)
        import_btn.setStyleSheet(BTN_STYLE) # Removed special background/font-weight
        import_btn.clicked.connect(lambda: controller.run_serial_import(self))
        layout.addWidget(import_btn)

        monitor_btn = QPushButton("🔍 Monitoritzar Port (Consola)")
        monitor_btn.setFixedSize(BTN_WIDTH, BTN_HEIGHT)
        monitor_btn.setStyleSheet(BTN_STYLE)
        monitor_btn.clicked.connect(lambda: controller.run_serial_monitor(self))
        layout.addWidget(monitor_btn)

        sankey_btn = QPushButton("📊 Diagrama Sankey")
        sankey_btn.setFixedSize(BTN_WIDTH, BTN_HEIGHT)
        sankey_btn.setStyleSheet(BTN_STYLE)
        sankey_btn.clicked.connect(lambda: controller.run_sankey(self))
        layout.addWidget(sankey_btn)

        map_btn = QPushButton("🗺️ Mapa dels punts de mesura")
        map_btn.setFixedSize(BTN_WIDTH, BTN_HEIGHT)
        map_btn.setStyleSheet(BTN_STYLE)
        map_btn.clicked.connect(lambda: controller.run_map(self))
        #layout.addWidget(map_btn)

        html_map_btn = QPushButton("🌐 Mapa interactiu (HTML)")
        html_map_btn.setFixedSize(BTN_WIDTH, BTN_HEIGHT)
        html_map_btn.setStyleSheet(BTN_STYLE)
        html_map_btn.clicked.connect(lambda: controller.run_html_map(self))
        layout.addWidget(html_map_btn)

        preview_btn = QPushButton("📈 Veure un gràfic")
        preview_btn.setFixedSize(BTN_WIDTH, BTN_HEIGHT)
        preview_btn.setStyleSheet(BTN_STYLE)
        preview_btn.clicked.connect(lambda: controller.run_preview_plot(self))
        layout.addWidget(preview_btn)

        batch_btn = QPushButton("📉 Gràfics de tots els arxius")
        batch_btn.setFixedSize(BTN_WIDTH, BTN_HEIGHT)
        batch_btn.setStyleSheet(BTN_STYLE)
        batch_btn.clicked.connect(lambda: controller.run_batch_plots_folder(self))
        layout.addWidget(batch_btn)

        box_btn = QPushButton("📦 Boxplots de tots els arxius")
        box_btn.setFixedSize(BTN_WIDTH, BTN_HEIGHT)
        box_btn.setStyleSheet(BTN_STYLE)
        box_btn.clicked.connect(lambda: controller.run_batch_boxplots_folder(self))
        layout.addWidget(box_btn)

        csv_btn = QPushButton("📝 Excel2csv")
        csv_btn.setFixedSize(BTN_WIDTH, BTN_HEIGHT)
        csv_btn.setStyleSheet(BTN_STYLE)
        csv_btn.clicked.connect(lambda: controller.run_excel2csv_button(self))
        layout.addWidget(csv_btn) # Assegurem que el botó Excel2csv s'afegeix

        excel2js_btn = QPushButton("📜 Excel2js")
        excel2js_btn.setFixedSize(BTN_WIDTH, BTN_HEIGHT)
        excel2js_btn.setStyleSheet(BTN_STYLE)
        excel2js_btn.clicked.connect(lambda: controller.run_excel2js_button(self))
        layout.addWidget(excel2js_btn)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SimpleGUI()
    window.show()
    sys.exit(app.exec_())