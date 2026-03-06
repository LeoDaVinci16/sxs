# create_map.py

from pathlib import Path
import os
import matplotlib.pyplot as plt
from PIL import Image
import pandas as pd
from matplotlib.widgets import Button
import sys

# ==============================
# 0️⃣ CONFIG
# ==============================
ROOT_FOLDER = Path(__file__).parents[1]
RAW_FOLDER = os.path.join(ROOT_FOLDER, "data")

DEFAULT_IMG_FILE = "planol.png"
DEFAULT_EXCEL_FILE = "punts-mesura.csv"
DEFAULT_MAGNITUDE = "DN"

# ==============================
# 1️⃣ INPUT FILE HANDLER
# ==============================
def get_input_file(default_file):
    """Return file path: sys.argv[1] if provided, else default_file."""
    if len(sys.argv) >= 2:
        file_path = sys.argv[1]
        print(f"Using file from command line: {file_path}")
    else:
        file_path = default_file
        print(f"No file provided. Using default: {file_path}")
    return file_path

# ==============================
# 2️⃣ LOAD DATA
# ==============================
def load_background_image(img_filename):
    img_path = os.path.join(RAW_FOLDER, img_filename)
    if not os.path.exists(img_path):
        raise FileNotFoundError(f"Image not found: {img_path}")
    return Image.open(img_path)

def load_measure_points(csv_filename):
    csv_path = os.path.join(RAW_FOLDER, "csv", csv_filename)
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"Excel file not found: {csv_path}")
    df = pd.read_csv(csv_path, encoding="cp1252")
    df = df.dropna(subset=["x", "y"])  # Only keep rows with coordinates
    return df

# ==============================
# 3️⃣ PLOT SETUP
# ==============================
def setup_plot(background_image):
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.imshow(background_image)
    plt.axis("off")
    fig.subplots_adjust(left=0, right=1, top=1, bottom=0)
    return fig, ax

def plot_points(ax, df):
    for _, row in df.iterrows():
        ax.plot(row["x"], row["y"], "ro")

# ==============================
# 4️⃣ CLICK HANDLER
# ==============================
def create_click_handler(ax, df, magnitude_col, text_boxes):
    def on_click(event):
        if event.xdata is None or event.ydata is None:
            return

        for _, row in df.iterrows():
            x, y = row["x"], row["y"]
            label = str(row["id"])
            od_val = row[magnitude_col]

            if abs(event.xdata - x) < 20 and abs(event.ydata - y) < 20:
                if label in text_boxes:
                    text_boxes[label].remove()
                    del text_boxes[label]
                else:
                    txt = ax.text(
                        x, y + 20,
                        f"Measure point: {label}\n {magnitude_col} = {od_val} mm",
                        fontsize=12,
                        ha="center",
                        bbox=dict(facecolor="white", alpha=0.7)
                    )
                    text_boxes[label] = txt
                ax.figure.canvas.draw()
    return on_click

def toggle_all(ax, df, magnitude_col, text_boxes, fig):
    any_visible = any([txt.get_visible() for txt in text_boxes.values()]) if text_boxes else False

    for _, row in df.iterrows():
        label = str(row["id"])
        x, y = row["x"], row["y"]
        od_val = row[magnitude_col]

        if label not in text_boxes:
            txt = ax.text(
                x, y + 20,
                f"Measure point: {label}\n {magnitude_col} = {od_val} mm",
                fontsize=12,
                ha="center",
                bbox=dict(facecolor="white", alpha=0.7)
            )
            text_boxes[label] = txt

        text_boxes[label].set_visible(not any_visible)

    fig.canvas.draw()   

# ==============================
# 5️⃣ MAGNITUDE SELECTION
# ==============================
def choose_magnitude_column(df, default=DEFAULT_MAGNITUDE):
    print("Columnes disponibles:", ", ".join(df.columns))
    user_input = input(f"Escriu el nom de la columna de magnitud (enter per defecte '{default}'): ").strip()
    
    if user_input and user_input in df.columns:
        return user_input
    else:
        if user_input and user_input not in df.columns:
            print(f"[WARNING] '{user_input}' no existeix. S'utilitza la columna per defecte: '{default}'")
        return default

# ==============================
# 6️⃣ MAIN
# ==============================
def main():
    img_file = get_input_file(DEFAULT_IMG_FILE)
    excel_file = get_input_file(DEFAULT_EXCEL_FILE)

    img = load_background_image(img_file)
    df = load_measure_points(excel_file)
    magnitude_col = choose_magnitude_column(df, DEFAULT_MAGNITUDE)

    fig, ax = setup_plot(img)
    plot_points(ax, df)

    text_boxes = {}
    click_handler = create_click_handler(ax, df, magnitude_col, text_boxes)
    fig.canvas.mpl_connect("button_press_event", click_handler)

    # Toggle button
    ax_toggle = plt.axes([0.81, 0.01, 0.1, 0.05])
    btn_toggle = Button(ax_toggle, "Show/Hide All")
    btn_toggle.on_clicked(lambda event: toggle_all(ax, df, magnitude_col, text_boxes, fig))

    plt.show()

if __name__ == "__main__":
    main()