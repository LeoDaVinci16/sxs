# create_report_pdf.py

import os
import subprocess
from create_plots import batch_plot
import re


# Configuration
csv_folder = "data/raw"
plot_folder = "outputs/plots"
qmd_file = "report_generated_pdf.qmd"
variables_to_plot = ["A Flow velocity [m/s]"]

# Ensure output folder exists
os.makedirs(plot_folder, exist_ok=True)

# 1️⃣ Generate (or check) all plots
print("Generating plots (batch_plot)...")
batch_plot(csv_folder, plot_folder, variables_to_plot)
print("All plots generated.\n")

# 2️⃣ Index plot paths
plot_index = {}
for csv_file in os.listdir(csv_folder):
    if not csv_file.lower().endswith(".csv"):
        continue
    for var in variables_to_plot:
        variable_clean = re.sub(r"[^\w\-_\. ]", "", var).replace(" ", "_")
        plot_name = f"{os.path.splitext(csv_file)[0]}_{variable_clean}.png"
        plot_path = os.path.join(plot_folder, plot_name)
        plot_index.setdefault(csv_file, {})[var] = plot_path

# 3️⃣ Write QMD
print(f"Writing QMD file: {qmd_file}")
with open(qmd_file, "w", encoding="utf-8") as f:
    f.write(
        """---
title: "Informe dels cabals (PDF)"
author: Arnau Coronado Nadal
execute:
  cache: false
format:
  pdf:
    toc: true
    documentclass: article
    geometry: margin=1.5cm
    header-includes: |
      \\usepackage{caption}
      \\captionsetup[figure]{skip=5pt}
      \\usepackage{parskip}
      \\setlength{\\parskip}{0.2em}
---
"""
    )

    # Iterate points and CSVs
    points = sorted({f.rsplit("_", 1)[-1].replace(".csv", "") for f in os.listdir(csv_folder)})
    for point in points:
        f.write(f"\\newpage\n\n")  # <-- forces a page break in PDF
        f.write(f"\n## Punt de mesura {point}\n\n")
        f.write(f"Gràfiques de les mesures fetes en el punt {point}:\n\n")
        for csv_file in sorted(os.listdir(csv_folder)):
            if not csv_file.lower().endswith(".csv"):
                continue
            if not csv_file.endswith(point + ".csv"):
                continue
            f.write(f"### {csv_file}\n\n")
            for var in variables_to_plot:
                plot_path = plot_index[csv_file].get(var)
                if plot_path and os.path.exists(plot_path):
                    f.write(f"![{var}]({plot_path})\n\n")
                else:
                    f.write(f"*⚠️ Plot not found for {var}*\n\n")

print("✅ QMD file written successfully.")

# 4️⃣ Render PDF
print("Rendering PDF via Quarto...")
subprocess.run([
    "quarto", "render", qmd_file,
    "--to", "pdf"
], check=True)
print("✅ PDF generated successfully.")