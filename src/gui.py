import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QPushButton, QVBoxLayout, QWidget
from PyQt5.QtCore import Qt
import controller

class SimpleGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SXS Tools")
        self.setFixedSize(350, 420)

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

        sankey_btn = QPushButton("📊 Diagrama Sankey")
        sankey_btn.setFixedSize(BTN_WIDTH, BTN_HEIGHT)
        sankey_btn.setStyleSheet(BTN_STYLE)
        sankey_btn.clicked.connect(lambda: controller.run_sankey(self))
        layout.addWidget(sankey_btn)

        network_btn = QPushButton("🧠 Network")
        network_btn.setFixedSize(BTN_WIDTH, BTN_HEIGHT)
        network_btn.setStyleSheet(BTN_STYLE)
        network_btn.clicked.connect(lambda: controller.run_network(self))
        layout.addWidget(network_btn)

        html_map_btn = QPushButton("🌐 Mapa interactiu (HTML)")
        html_map_btn.setFixedSize(BTN_WIDTH, BTN_HEIGHT)
        html_map_btn.setStyleSheet(BTN_STYLE)
        html_map_btn.clicked.connect(lambda: controller.run_html_map(self))
        layout.addWidget(html_map_btn)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SimpleGUI()
    window.show()
    sys.exit(app.exec_())