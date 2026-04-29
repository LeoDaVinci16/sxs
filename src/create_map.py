import sys
import math
from pathlib import Path
import pandas as pd
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QLabel, QPushButton, QGraphicsView,
    QGraphicsScene, QGraphicsEllipseItem, QGraphicsTextItem, QGraphicsItemGroup, QGraphicsTextItem, QGraphicsRectItem
)
from PyQt5.QtGui import QPixmap, QColor, QBrush, QPen, QFont
from PyQt5.QtCore import Qt, QPointF

from config import DATA_PUNTS, planol_at, punts_at


# ==============================
# HELPERS
# ==============================
def load_measure_points(csv_filename):
    csv_path = Path(csv_filename)
    if not csv_path.exists():
        raise FileNotFoundError(f"CSV file not found: {csv_path}")
    df = pd.read_csv(csv_path, on_bad_lines='skip')
    df = df.dropna(subset=["x", "y"])
    return df


def get_color(val):
    if val is None:
        return QColor("#6C6C6C")
    try:
        if math.isnan(float(val)) or float(val) == 0:
            return QColor("#6C6C6C")
        return QColor("#00F128")
    except:
        return QColor("#FF2F00")


def format_value(val):
    try:
        return f"{float(val):.4f}"
    except:
        return str(val)


# ==============================
# DRAGGABLE LABEL
# ==============================

class DraggableLabel(QGraphicsItemGroup):
    def __init__(self, text):
        super().__init__()

        # Text
        self.text_item = QGraphicsTextItem(text)
        font = QFont("Arial", 18)  # 👈 increase size here
        self.text_item.setFont(font)
        
        self.text_item.setDefaultTextColor(Qt.black)

        # Background box
        rect = self.text_item.boundingRect()
        padding = 4

        self.rect_item = QGraphicsRectItem(
            rect.adjusted(-padding, -padding, padding, padding)
        )

        self.rect_item.setBrush(QBrush(QColor("white")))
        self.rect_item.setPen(QPen(QColor("black")))

        # Add to group
        self.addToGroup(self.rect_item)
        self.addToGroup(self.text_item)

        # Make draggable
        self.setFlag(QGraphicsItemGroup.ItemIsMovable)

        # Ensure it's on top
        self.setZValue(2)

        self.setVisible(False)


# ==============================
# DOT ITEM
# ==============================
class DotItem(QGraphicsEllipseItem):
    def __init__(self, x, y, r, label_id, callback):
        super().__init__(x - r, y - r, 2 * r, 2 * r)
        self.label_id = label_id
        self.callback = callback
        self.setAcceptHoverEvents(True)
        self.setZValue(1)

    def mousePressEvent(self, event):
        self.callback(self.label_id)


# ==============================
# MAIN WINDOW
# ==============================
class Visualizer(QMainWindow):
    def __init__(self, img_file=planol_at, csv_file=punts_at,
                 magnitude_cols=["OD mm", "volume flow rate m3h", "Flow velocity ms"]):
        super().__init__()

        self.setWindowTitle("Visualizer")
        self.resize(1000, 800)

        self.df = load_measure_points(csv_file)
        self.magnitude_cols = magnitude_cols

        missing = [c for c in magnitude_cols if c not in self.df.columns]
        if missing:
            raise ValueError(f"Missing columns: {missing}")

        # Graphics scene
        self.view = QGraphicsView(self)
        self.setCentralWidget(self.view)
        self.scene = QGraphicsScene()
        self.view.setScene(self.scene)

        # Load image
        self.pixmap = QPixmap(str(img_file))
        self.bg_item = self.scene.addPixmap(self.pixmap)

        self.orig_width = self.pixmap.width()
        self.orig_height = self.pixmap.height()

        self.labels = {}
        self.dots = {}
        self.visible = {}

        self.create_items()

        # Button
        self.toggle_btn = QPushButton("Show/Hide All", self)
        self.toggle_btn.clicked.connect(self.toggle_all)
        self.toggle_btn.move(10, 10)
        self.toggle_btn.raise_()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.view.fitInView(self.bg_item, Qt.KeepAspectRatio)
        self.update_positions()

    def showEvent(self, event):
        super().showEvent(event)
        self.view.fitInView(self.bg_item, Qt.KeepAspectRatio)
        self.update_positions()

    def create_items(self):
        r = 6

        for _, row in self.df.iterrows():
            label_id = str(row["id"])

            # Values text
            values_text = "\n".join(
                f"{col}: {format_value(row[col])}"
                for col in self.magnitude_cols
            )

            label = DraggableLabel(f"{label_id}\n{values_text}")
            self.scene.addItem(label)

            self.labels[label_id] = label
            self.visible[label_id] = False

            # Dot
            value = row[self.magnitude_cols[0]]
            color = get_color(value)

            dot = DotItem(0, 0, r, label_id, self.on_dot_click)
            dot.setBrush(QBrush(color))
            self.scene.addItem(dot)

            self.dots[label_id] = (dot, row["x"], row["y"])

        self.update_positions()

    def update_positions(self):
        rect = self.view.sceneRect()

        scale_x = rect.width() / self.orig_width
        scale_y = rect.height() / self.orig_height

        for label_id, (dot, x_raw, y_raw) in self.dots.items():
            x = x_raw * scale_x
            y = y_raw * scale_y

            dot.setRect(x - 6, y - 6, 12, 12)

            if self.visible[label_id]:
                self.labels[label_id].setPos(QPointF(x, y - 20))

    def on_dot_click(self, label_id):
        label = self.labels[label_id]

        if self.visible[label_id]:
            label.setVisible(False)
            self.visible[label_id] = False
        else:
            dot, x_raw, y_raw = self.dots[label_id]

            rect = self.view.sceneRect()
            scale_x = rect.width() / self.orig_width
            scale_y = rect.height() / self.orig_height

            x = x_raw * scale_x
            y = y_raw * scale_y

            label.setPos(QPointF(x, y - 20))
            label.setVisible(True)
            self.visible[label_id] = True

    def toggle_all(self):
        any_visible = any(self.visible.values())

        for label_id, label in self.labels.items():
            if any_visible:
                label.setVisible(False)
                self.visible[label_id] = False
            else:
                dot, x_raw, y_raw = self.dots[label_id]

                rect = self.view.sceneRect()
                scale_x = rect.width() / self.orig_width
                scale_y = rect.height() / self.orig_height

                x = x_raw * scale_x
                y = y_raw * scale_y

                label.setPos(QPointF(x, y - 20))
                label.setVisible(True)
                self.visible[label_id] = True


# ==============================
# RUN
# ==============================
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Visualizer()
    window.show()
    sys.exit(app.exec_())