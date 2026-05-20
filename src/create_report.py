import os
import matplotlib
# Force 'Agg' backend to avoid conflicts with GUI backends and fix fileno issues
matplotlib.use('Agg')

import subprocess
import shutil
import re
from pathlib import Path

import matplotlib.pyplot as plt

# Import existing project components
import config
from create_plots import batch_plot, safe_filename as safe_fn_plots
from create_boxplots import batch_boxplot

def tex_escape(text):
    """Escapes characters that have special meaning in LaTeX."""
    conv = {
        '&': r'\&', '%': r'\%', '$': r'\$', '#': r'\#', '_': r'\_',
        '{': r'\{', '}': r'\}', '~': r'\textasciitilde{}',
        '^': r'\^{}', '\\': r'\textbackslash{}', '<': r'\textless{}', '>': r'\textgreater{}',
    }
    regex = re.compile('|'.join(re.escape(str(key)) for key in sorted(conv.keys(), key=lambda item: -len(item))))
    return regex.sub(lambda match: conv[match.group()], text)

def generate_report(variables=None):
    """
    Generates all plots/boxplots and compiles them into a single PDF report via LaTeX.
    """
    if variables is None:
        # Default variables to process based on existing project usage
        variables = ["A Flow velocity [m/s]", "MEASURE"]

    # 1. Setup Output Directory
    # User requested 'outputs/informe/'
    report_dir = config.ROOT / "outputs" / "informe"
    assets_dir = report_dir / "assets"
    
    # Ensure directories exist and are clean for a fresh run
    report_dir.mkdir(parents=True, exist_ok=True)
    if assets_dir.exists():
        shutil.rmtree(assets_dir)
    assets_dir.mkdir(parents=True, exist_ok=True)

    # 2. Generate Plots and Boxplots
    # We redirect the output of batch functions to our new informe/assets folder
    print(f"Generating time-series plots into {assets_dir}...")
    batch_plot(config.DATA_RAW, assets_dir, variables)
    
    print(f"Generating boxplots into {assets_dir}...")
    batch_boxplot(config.DATA_RAW, assets_dir, variables)

    # 3. Create LaTeX content
    print("Generating LaTeX document...")
    tex_content = [
        r"\documentclass{article}",
        r"\usepackage[utf8]{inputenc}",
        r"\usepackage{graphicx}",
        r"\usepackage[margin=0.6in]{geometry}",
        r"\usepackage{float}",
        r"\usepackage{booktabs}",
        r"\usepackage{caption}",
        r"\title{Informe Global de Mesures}",
        r"\author{SXS Automated System}",
        r"\date{\today}",
        r"\begin{document}",
        r"\maketitle",
        r"\tableofcontents",
        r"\newpage"
    ]

    # Iterate through CSV files to organize the report
    csv_files = sorted(list(config.DATA_RAW.glob("*.csv")))
    
    if not csv_files:
        print("⚠️ No CSV files found in raw data folder.")
        return

    for csv_file in csv_files:
        # Extract POINTNAME for the report section title
        filename = csv_file.name
        match = re.search(r"^\d{6}_\d{4,6}_(.+?)(?:_OD\d+)?(?:_Type\d+)?\.csv$", filename)
        point_name = match.group(1) if match else csv_file.stem
        
        # Gather generated images for this specific file
        produced_items = []
        for var in variables:
            ts_plot = assets_dir / f"{stem}_{safe_fn_plots(var)}.png"
            bx_plot = assets_dir / f"{stem}_boxplot_{safe_fn_plots(var)}.png"
            if ts_plot.exists() or bx_plot.exists():
                produced_items.append((var, ts_plot, bx_plot))
        
        if not produced_items:
            continue

        # Add section for the data file
        tex_content.append(r"\section{Point: " + tex_escape(point_name) + " (" + tex_escape(csv_file.stem) + ")}")
        
        for var, ts_path, bx_path in produced_items:
            safe_var = tex_escape(var)
            tex_content.append(r"\subsection{Variable: " + safe_var + "}")
            
            # Include Time Series and Boxplot one after the other
            for img_path in [ts_path, bx_path]:
                if img_path.exists():
                    tex_content.append(r"\begin{figure}[H]")
                    tex_content.append(r"\centering")
                    tex_content.append(r"\includegraphics[width=0.9\textwidth]{assets/" + img_path.name + "}")
                    tex_content.append(r"\end{figure}")
            
            tex_content.append(r"\newpage")

    tex_content.append(r"\end{document}")

    # Write .tex file
    tex_path = report_dir / "report.tex"
    with open(tex_path, "w", encoding="utf-8") as f:
        f.write("\n".join(tex_content))

    # 4. Compile PDF
    print("Compiling PDF...")
    try:
        # Run twice to generate TOC correctly
        for _ in range(2):
            subprocess.run(["pdflatex", "-interaction=nonstopmode", "report.tex"], 
                           cwd=report_dir, check=True, capture_output=True)
        print(f"Success! PDF Report created at: {report_dir / 'report.pdf'}")
    except Exception:
        print(f"❌ Error compiling PDF. Ensure pdflatex is installed and in PATH.")
        print(f"Manual compilation source: {tex_path}")

if __name__ == "__main__":
    generate_report()