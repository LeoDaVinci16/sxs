from pathlib import Path
import os
import matplotlib.pyplot as plt
from PIL import Image
import pandas as pd

# ==============================
# 1️⃣ LOAD IMAGE
# ==============================

ROOT_FOLDER = Path(__file__).parents[1]
RAW_FOLDER = os.path.join(ROOT_FOLDER, "docs")

img_path = os.path.join(RAW_FOLDER, "planol.png")
img = Image.open(img_path)

# ==============================
# 2️⃣ LOAD EXCEL DATA
# ==============================

excel_path = os.path.join(RAW_FOLDER, "punts-mesura.xlsx")
magnitude = "WT"
df = pd.read_excel(excel_path)

# Keep only rows that have coordinates
df = df.dropna(subset=["x", "y"])

# ==============================
# 3️⃣ SETUP FIGURE
# ==============================

fig, ax = plt.subplots(figsize=(10, 6))
ax.imshow(img)
plt.axis("off")

# Draw points from Excel
for _, row in df.iterrows():
    ax.plot(row["x"], row["y"], "ro")

# ==============================
# 4️⃣ KEEP TRACK OF TEXT BOXES
# ==============================

text_boxes = {}

# ==============================
# 5️⃣ CLICK EVENT
# ==============================

def on_click(event):
    if event.xdata is None or event.ydata is None:
        return

    for _, row in df.iterrows():
        x = row["x"]
        y = row["y"]
        label = str(row["id"])  # 👈 THIS IS NOW THE LABEL
        od_val = row[magnitude]

        if abs(event.xdata - x) < 20 and abs(event.ydata - y) < 20:

            if label in text_boxes:
                text_boxes[label].remove()
                del text_boxes[label]
            else:
                txt = ax.text(
                    x,
                    y + 20,
                    f"Measure point: {label}\n {magnitude} = {od_val} mm",
                    fontsize=12,
                    ha="center",
                    bbox=dict(facecolor="white", alpha=0.7)
                )
                text_boxes[label] = txt

            fig.canvas.draw()

fig.canvas.mpl_connect("button_press_event", on_click)

# ==============================
# 6️⃣ SHOW
# ==============================

plt.show()