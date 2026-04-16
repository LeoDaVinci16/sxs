import pandas as pd
from pathlib import Path
import json

csv_path = "punts-mesura-at.csv"
df = pd.read_csv(csv_path)

# Keep only valid x,y
df = df.dropna(subset=["x", "y"])

# Decide which columns you want to show in the tooltip
columns = [
    "id",
    "x", "y",
    "planta",
    "planta-numero",
    "DN",
    "OD mm",
    "WT mm",
    "Flow velocity ms",
    "Mass flow rate m3s",
    "mass flow rate m3h"
]
df = df[columns]

points = df.to_dict("records")
js = f"const points = {json.dumps(points)};\n"

output_js = "js/points.js"
Path(output_js).parent.mkdir(exist_ok=True)
Path(output_js).write_text(js)

print("✅ points.js created: points =", len(points))