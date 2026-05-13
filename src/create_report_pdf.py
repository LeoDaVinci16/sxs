import os
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
import sys
import subprocess
import shutil
import re

# Import existing project components
from config import DATA_RAW, OUTPUT_PLOTS
from create_plots import load_csv, create_plot
from create_boxplots import create_boxplot

def tex_escape(text):
    """Escapes characters that have special meaning in LaTeX."""
    conv = {
        '&': r'\&', '%': r'\%', '$': r'\$', '#': r'\#', '_': r'\_',
        '{': r'\{', '}': r'\}', '~': r'\textasciitilde{}',
        '^': r'\^{}', '\\': r'\textbackslash{}', '<': r'\textless{}', '>': r'\textgreater{}',
    }
    regex = re.compile('|'.join(re.escape(str(key)) for key in sorted(conv.keys(), key=lambda item: -len(item))))
    return regex.sub(lambda match: conv[match.group()], text)

def get_metadata(csv_path):
    """
    Parses metadata into general info and statistical summaries.
    """
    general_info = []
    stats_info = []
    try:
        with open(csv_path, 'r', encoding='utf-8', errors='replace') as f:
            for line in f:
                clean_line = line.strip()
                if clean_line.startswith("#"):
                    if "Stats ->" in clean_line:
                        stats_info.append(clean_line.replace("#", "").strip())
                    else:
                        # Clean key-value pairs
                        content = clean_line.replace("#", "").strip()
                        if ":" in content:
                            k, v = content.split(":", 1)
                            general_info.append((k.strip(), v.strip()))
                        else:
                            general_info.append((content, ""))
                elif not clean_line:
                    continue
                else:
                    # Stop reading once we reach the header/data area
                    break
    except Exception as e:
        print(f"Error reading metadata: {e}")
    return general_info, stats_info

def parse_filename_info(filename):
    """
    Extracts ID, Date, and Time from filename format: YYMMDD_HHMM_ID_...
    """
    parts = filename.split("_")
    if len(parts) >= 3:
        raw_date = parts[0]
        raw_time = parts[1]
        point_id = parts[2]
        
        # Format date (YYMMDD -> DD/MM/YY) and time (HHMM -> HH:MM)
        try:
            fmt_date = f"{raw_date[4:6]}/{raw_date[2:4]}/{raw_date[0:2]}"
            fmt_time = f"{raw_time[0:2]}:{raw_time[2:4]}"
            return point_id, fmt_date, fmt_time
        except:
            return point_id, raw_date, raw_time # Ensure 3 values are always returned
    return "Unknown", "Unknown", "Unknown"

def create_report_pdf(target_extension="", variables=None, output_filename=None):
    """
    Generates a multi-page PDF report. 
    Filters files in DATA_RAW by target_extension.
    For each file/variable, includes metadata, time-series plot, and boxplot.
    """
    if variables is None:
        variables = ["MEASURE", "SSPEED"]

    # 1. Setup Output Directory
    # We create a 'reports' directory in the same parent as plots
    reports_dir = Path(OUTPUT_PLOTS).parent / "reports"
    reports_dir.mkdir(parents=True, exist_ok=True)
    
    # 2. Image assets directory
    img_dir = reports_dir / "tex_assets"
    if img_dir.exists():
        shutil.rmtree(img_dir)
    img_dir.mkdir(parents=True, exist_ok=True)

    if not output_filename:
        safe_ext = "".join(x for x in target_extension if x.isalnum()) or "all"
        output_filename = f"Report_{safe_ext}"
    
    tex_path = reports_dir / f"{output_filename}.tex"

    # 3. File Selection
    all_files = list(DATA_RAW.glob("*.csv"))
    filtered_files = sorted([f for f in all_files if target_extension.lower() in f.name.lower()])

    if not filtered_files:
        print(f"No files found matching '{target_extension}' in {DATA_RAW}")
        return

    print(f"Generating PDF report for {len(filtered_files)} files...")

    tex_content = [
        r"\documentclass{article}",
        r"\usepackage[utf8]{inputenc}",
        r"\usepackage{graphicx}",
        r"\usepackage[margin=0.6in]{geometry}",
        r"\usepackage{float}",
        r"\usepackage{booktabs}",
        r"\title{SXS Measurement Report}",
        r"\author{SXS Automated System}",
        r"\date{\today}",
        r"\begin{document}",
        r"\maketitle",
    ]

    img_counter = 0

    for csv_file in filtered_files:
        print(f" -> Processing: {csv_file.name}")
        df = load_csv(csv_file)
        if df is None or df.empty:
            continue
        
        general_meta, stats_meta = get_metadata(csv_file)
        point_id, date, time = parse_filename_info(csv_file.name)
        target_cols = [v for v in variables if v in df.columns]

        for col in target_cols:
            series_data = df[col]
            if isinstance(series_data, pd.DataFrame):
                series_data = series_data.iloc[:, 0]
            df_clean = pd.to_numeric(series_data, errors='coerce').dropna().sort_index()

            if df_clean.empty:
                continue

            img_counter += 1
            
            # Generate Plots as PNG
            fig_ts, ax_ts = plt.subplots(figsize=(10, 4))
            _embed_plot(df_clean, col, ax_ts, title=f"Time Series Analysis")
            ts_img_path = img_dir / f"ts_{img_counter}.png"
            fig_ts.savefig(ts_img_path, bbox_inches='tight', dpi=150)
            plt.close(fig_ts)

            fig_bx, ax_bx = plt.subplots(figsize=(10, 2))
            _embed_boxplot(df_clean, col, ax_bx, title=f"Statistical Distribution (Boxplot)")
            bx_img_path = img_dir / f"bx_{img_counter}.png"
            fig_bx.savefig(bx_img_path, bbox_inches='tight', dpi=150)
            plt.close(fig_bx)

            # Build LaTeX section
            safe_name = tex_escape(csv_file.name)
            safe_col = tex_escape(col)
            summary_text = f"Dades del punt de mesura {tex_escape(point_id)} en el dia {tex_escape(date)} a les {tex_escape(time)}."
            
            tex_content.append(r"\section*{" + safe_name + "}")
            tex_content.append(r"\subsection*{Variable: " + safe_col + "}")

            # Add Summary Text after tables
            tex_content.append(r"\paragraph{}" + summary_text + r"\vspace{1em}")
            
            # 1. Metadata Table
            tex_content.append(r"\subsubsection*{Configuració del Punt}")
            tex_content.append(r"\begin{tabular}{ll}")
            tex_content.append(r"\toprule \textbf{Paràmetre} & \textbf{Valor} \\ \midrule")
            for k, v in general_meta:
                if k: tex_content.append(f"{tex_escape(k)} & {tex_escape(v)} \\\\")
            tex_content.append(r"\bottomrule \end{tabular} \vspace{1em}")

            # 2. Stats Table
            if stats_meta:
                tex_content.append(r"\subsubsection*{Resum Estadístic}")
                tex_content.append(r"\begin{tabular}{lccccc}")
                tex_content.append(r"\toprule \textbf{Variable} & \textbf{Avg} & \textbf{Med} & \textbf{Mode} & \textbf{Max} & \textbf{Min} \\ \midrule")
                for stat_line in stats_meta:
                    # Parse: "MEASURE Stats -> Avg: 0.1 | Median: 0.1 | Mode: 0.1 | Max: 0.1 | Min: 0.1"
                    parts = stat_line.split("->")
                    label = parts[0].replace("Stats", "").strip()
                    metrics = parts[1].split("|")
                    vals = [m.split(":")[1].strip() for m in metrics]
                    tex_content.append(f"{tex_escape(label)} & {' & '.join(vals)} \\\\")
                tex_content.append(r"\bottomrule \end{tabular} \vspace{1em}")

            tex_content.append(r"\begin{figure}[H]")
            tex_content.append(r"\centering")
            tex_content.append(r"\includegraphics[width=0.5\textwidth]{tex_assets/ts_" + str(img_counter) + ".png}")
            tex_content.append(r"\end{figure}")

            tex_content.append(r"\begin{figure}[H]")
            tex_content.append(r"\centering")
            tex_content.append(r"\includegraphics[width=0.5\textwidth]{tex_assets/bx_" + str(img_counter) + ".png}")
            tex_content.append(r"\end{figure}")
            
            # Add Summary Text after plots
            tex_content.append(r"\centerline{" + summary_text + "}")

    tex_content.append(r"\end{document}")

    with open(tex_path, "w", encoding="utf-8") as f:
        f.write("\n".join(tex_content))

    print(f"LaTeX file generated: {tex_path}")
    
    try:
        print("Compiling PDF with pdflatex...")
        subprocess.run(["pdflatex", "-interaction=nonstopmode", tex_path.name], 
                       cwd=reports_dir, check=True, capture_output=True)
        print(f"Success! Report created at: {reports_dir / (output_filename + '.pdf')}")
    except Exception:
        print(f"[ERROR] Could not compile PDF. Ensure pdflatex (TeX Live/MiKTeX) is installed and in PATH.")
        print(f"You can manually compile: {tex_path}")

def _embed_plot(df_series, variable, ax, title):
    """Helper to render the time series plot into a specific axis."""
    ax.plot(df_series.index, df_series.values, linewidth=1, color='#1f77b4')
    median_val = df_series.median()
    ax.axhline(median_val, color='red', linestyle='--', linewidth=1, alpha=0.7)
    ax.set_title(title, fontsize=10, weight='bold')
    ax.grid(True, linestyle="--", alpha=0.5)
    ax.set_ylabel(variable, fontsize=9)
    ax.tick_params(labelsize=8)

def _embed_boxplot(df_series, variable, ax, title):
    """Helper to render the boxplot into a specific axis."""
    ax.boxplot(df_series.values, patch_artist=True, vert=False,
               boxprops=dict(facecolor='lightblue', color='blue'),
               medianprops=dict(color='red', linewidth=2))
    ax.set_title(title, fontsize=10, weight='bold')
    ax.set_xlabel(variable, fontsize=9)
    ax.set_yticks([]) 
    ax.grid(True, linestyle="--", alpha=0.5, axis='x')
    ax.tick_params(labelsize=8)

if __name__ == "__main__":
    # Default values for direct execution: date 260512 and variable MEASURE
    filter_val = ""
    vars_val = ["MEASURE"]

    # Override defaults with CLI arguments if provided:
    # e.g., python create_report_pdf.py "STE" "MEASURE,SSPEED"
    if len(sys.argv) > 1:
        filter_val = sys.argv[1]

    if len(sys.argv) > 2:
        vars_val = [v.strip() for v in sys.argv[2].split(",")]

    create_report_pdf(filter_val, variables=vars_val)