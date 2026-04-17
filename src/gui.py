import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QPushButton, QVBoxLayout, QWidget
from PyQt5.QtCore import Qt
import selection_layer as controller

class SimpleGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SXS Tools")
        self.setFixedSize(300, 240)

        self._build_ui()

    def _build_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        layout.setAlignment(Qt.AlignCenter)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        title_label = QLabel("Eines")
        title_label.setStyleSheet("font: bold 14px Arial;")
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)

        sankey_btn = QPushButton("Diagrama Sankey")
        sankey_btn.setFixedWidth(250)
        sankey_btn.clicked.connect(lambda: controller.run_sankey(self))
        layout.addWidget(sankey_btn)

        map_btn = QPushButton("Mapa dels punts de mesura")
        map_btn.setFixedWidth(250)
        map_btn.clicked.connect(lambda: controller.run_map(self))
        layout.addWidget(map_btn)

        preview_btn = QPushButton("Veure un gràfic")
        preview_btn.setFixedWidth(250)
        preview_btn.clicked.connect(lambda: controller.run_preview_plot(self))
        layout.addWidget(preview_btn)

        batch_btn = QPushButton("Gràfics de tots els arxius")
        batch_btn.setFixedWidth(250)
        batch_btn.clicked.connect(lambda: controller.run_batch_plots_folder(self))
        layout.addWidget(batch_btn)

        batch_btn = QPushButton("Excel2csv")
        batch_btn.setFixedWidth(250)
        batch_btn.clicked.connect(lambda: controller.run_excel2csv_button(self))
        layout.addWidget(batch_btn)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SimpleGUI()
    window.show()
    sys.exit(app.exec_())