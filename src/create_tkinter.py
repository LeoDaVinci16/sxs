# create_tkinter.py

import tkinter as tk
from tkinter import filedialog
from pathlib import Path
import pandas as pd
from PIL import Image, ImageTk
from tkinter.filedialog import askopenfilename
import math
from config import DATA_PUNTS, planol_at, planol_ste, punts_at, punts_ste


# ==============================
# HELPER FUNCTIONS
# ==============================
def load_measure_points(csv_filename):
    csv_path = csv_filename
    if not csv_path.exists():
        raise FileNotFoundError(f"CSV file not found: {csv_path}")
    df = pd.read_csv(csv_path, on_bad_lines='skip')
    df = df.dropna(subset=["x", "y"])
    return df
    
def get_color(val):
    if val is None:
        return "#6C6C6C"
    try:
        if math.isnan(float(val)) or float(val) == 0:
            return "#6C6C6C"
        return "#00F128"
    except:
        return "#FF2F00"

def format_value(val):
    try:
        return f"{float(val):.4f}"
    except (ValueError, TypeError):
        return str(val)

# ==============================
# DRAGGABLE LABEL
# ==============================
class DraggableLabel:
    def __init__(self, widget):
        self.widget = widget
        self.widget.bind("<ButtonPress-1>", self.on_press)
        self.widget.bind("<B1-Motion>", self.on_drag)

    def on_press(self, event):
        self.startX = event.x
        self.startY = event.y

    def on_drag(self, event):
        x = self.widget.winfo_x() + (event.x - self.startX)
        y = self.widget.winfo_y() + (event.y - self.startY)
        self.widget.place(x=x, y=y)

# ==============================
# VISUALIZER
# ==============================
class Visualizer:
    def __init__(self, root, img_file=planol_at, csv_file=punts_at, magnitude_cols=["OD mm", "mass flow rate m3h", "Flow velocity ms"]):
        self.root = root
        self.magnitude_cols = magnitude_cols
        
        self.df = load_measure_points(csv_file)

        missing = [c for c in self.magnitude_cols if c not in self.df.columns]
        if missing:
            raise ValueError(f"Aquesta magnitud no existeix: {missing}")
        
        self.labels = {}
        self.dot_ids = {}
        self.visible = {}
        # Load original image
        #path = askopenfilename(
        #    title="Selecciona una imatge",
        #    filetypes=[("Images", "*.png *.jpg *.jpeg *.pdf")])
        #self.orig_image = Image.open(path)
        self.orig_image = Image.open(img_file) # old version without askopenfilename
        self.orig_width, self.orig_height = self.orig_image.size

        # Canvas fills window
        self.canvas = tk.Canvas(root)
        self.canvas.pack(fill="both", expand=True)
        self.canvas.bind("<Configure>", self.on_resize)

        """# Create labels
        for _, row in self.df.iterrows():
            label_id = str(row["id"])
            value = format_value(row[self.magnitude_col])
            lbl = tk.Label(root, text=f"{label_id}\n{self.magnitude_col}={value}",
                           bg="white", font=("Arial", 10), bd=1, relief="solid")
            DraggableLabel(lbl)
            self.labels[label_id] = lbl
            self.visible[label_id] = False """
        
        for _, row in self.df.iterrows():
            label_id = str(row["id"])

            values_text = "\n".join(
                f"{col}: {format_value(row[col])}"
                for col in self.magnitude_cols
            )

            lbl = tk.Label(
                root,
                text=f"{label_id}\n{values_text}",
                bg="white",
                font=("Arial", 9),
                bd=1,
                relief="solid",
                justify="left",
                padx=5,
                pady=3
            )

            DraggableLabel(lbl)
            self.labels[label_id] = lbl
            self.visible[label_id] = False

        # Buttons
        self.toggle_btn = tk.Button(root, text="Show/Hide All", command=self.toggle_all)
        self.toggle_btn.pack(pady=5)

    def on_resize(self, event):
        w, h = event.width, event.height
        self.scale_x = w / self.orig_width
        self.scale_y = h / self.orig_height

        self.resized_image = self.orig_image.resize((w, h), Image.Resampling.LANCZOS)
        self.bg_photo = ImageTk.PhotoImage(self.resized_image)

        self.canvas.delete("all")
        self.canvas.create_image(0, 0, anchor="nw", image=self.bg_photo)
        self.canvas.bg_photo = self.bg_photo  # keep reference

        self.dot_ids.clear()
        for _, row in self.df.iterrows():
            x = row["x"] * self.scale_x
            y = row["y"] * self.scale_y
            r = 6
            value = row[self.magnitude_cols]
            color = get_color(value)
            dot = self.canvas.create_oval(x-r, y-r, x+r, y+r, fill=color, outline="")
            label_id = str(row["id"])
            self.dot_ids[dot] = label_id
            self.canvas.tag_bind(dot, "<Button-1>", self.on_dot_click)

        # Reposition visible labels
        for label_id, lbl in self.labels.items():
            if self.visible[label_id]:
                for dot_id, l_id in self.dot_ids.items():
                    if l_id == label_id:
                        coords = self.canvas.coords(dot_id)
                        x = (coords[0]+coords[2])/2
                        y = coords[1]-20
                        lbl.place(x=x, y=y)

    def on_dot_click(self, event):
        dot = event.widget.find_withtag("current")[0]
        label_id = self.dot_ids[dot]
        lbl = self.labels[label_id]
        if self.visible[label_id]:
            lbl.place_forget()
            self.visible[label_id] = False
        else:
            coords = self.canvas.coords(dot)
            x = (coords[0]+coords[2])/2
            y = coords[1]-20
            lbl.place(x=x, y=y)
            self.visible[label_id] = True

    def toggle_all(self):
        any_visible = any(self.visible.values())
        for label_id, lbl in self.labels.items():
            if any_visible:
                lbl.place_forget()
                self.visible[label_id] = False
            else:
                for dot_id, l_id in self.dot_ids.items():
                    if l_id == label_id:
                        coords = self.canvas.coords(dot_id)
                        x = (coords[0]+coords[2])/2
                        y = coords[1]-20
                        lbl.place(x=x, y=y)
                        self.visible[label_id] = True


# ==============================
# TEST RUN
# ==============================
if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("1000x800")
    visualizer = Visualizer(root)
    root.mainloop()