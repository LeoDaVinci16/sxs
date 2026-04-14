# create_report_html_all.py

import os
import re
from collections import defaultdict
import plotly.io as pio
from points_dict import main


# Configuration
csv_folder = "data/raw"
qmd_file = "report_generated_html.qmd"
variables_to_plot = ["A Flow velocity [m/s]"]  # add more if needed
cache_folder = "_quarto_cache_html"
output_folder = "outputs"

# Ensure output folder exists (optional)
os.makedirs(output_folder, exist_ok=True)
os.makedirs(cache_folder, exist_ok=True)

# 1️⃣ Scan CSV files and group by measurement point
files_by_point = defaultdict(list)
for f in os.listdir(csv_folder):
    if f.lower().endswith(".csv"):
        point = f.rsplit("_", 1)[-1].replace(".csv", "")
        files_by_point[point].append(f)

# 1.1 Sort measurement points like STE-1, STE-2, ..., non-STE alphabetically
def point_sort_key(point_name):
    m = re.match(r"STE-(\d+)(?:_(.*))?$", point_name)
    if m:
        number = int(m.group(1))
        suffix = m.group(2) or ""
        return (0, number, suffix)
    else:
        return (1, point_name)

sorted_points = sorted(files_by_point.keys(), key=point_sort_key)

# 2️⃣ Write QMD file for HTML only
with open(qmd_file, "w", encoding="utf-8") as f:
    f.write(f"""---
title: "Informe dels cabals (HTML)"
author: Arnau Coronado Nadal
execute:
  cache: true
  cache-dir: {cache_folder}
format:
  html:
    toc: true
    code-fold: true
---\n\n""")

    # Iterate over points and CSVs
    for point, files in sorted(files_by_point.items()):
        f.write(f"## Punt de mesura {point}\n\n")
        f.write(f"Gràfiques de les mesures fetes en el punt {point}:\n\n")
        
        for csv_file in files:
            csv_path = os.path.join(csv_folder, csv_file)
            date_str = csv_file.split("_")[0]
            date_formatted = f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:]}"  # YYYY-MM-DD
            f.write(f"### {csv_file} ({date_formatted})\n\n")
            
            for var in variables_to_plot:
                # Python chunk for interactive HTML
                f.write(f"""```{{python}}
import sys, os
sys.path.append(os.path.abspath("src"))
from create_plots import load_csv, create_plotly_plot
import plotly.io as pio

csv_path = r"{csv_path}"
variable = "{var}"

df = load_csv(csv_path)
fig = create_plotly_plot(df, variable, csv_path)

# Show interactive plot in HTML
pio.renderers.default = "notebook_connected"
fig.show()
```\n\n""")

print(f"✅ Generated {qmd_file}")