import pandas as pd
from pathlib import Path
import json

csv_path = "punts-mesura-ste.csv"
img_width = 2482   # replace with real image width
img_height = 1755  # replace with real image height

df = pd.read_csv(csv_path)
df = df.dropna(subset=["x", "y"])

# add relative coordinates on the image
df["x_rel"] = df["x"] / img_width
df["y_rel"] = df["y"] / img_height

# keep only what you show in HTML
columns = [
    "x", "y", "x_rel", "y_rel", "id", 
     "planta-numero",
    "DN", "OD mm", "WT mm",
    "Flow velocity ms", "volume flow rate m3s", "mass flow rate kgh"
]
df = df[columns]

points = df.to_dict("records")
js = f"const points = {json.dumps(points)};"

js_dir = "js"
Path(js_dir).mkdir(exist_ok=True)
Path(f"{js_dir}/points.js").write_text(js)

print("✅ points.js created: points =", len(points))