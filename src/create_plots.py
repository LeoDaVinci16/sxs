from pathlib import Path
import pandas as pd
from pandas import to_datetime
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import re
from config import at_raw as AT_RAW, ste_raw as STE_RAW, at_plots as OUTPUT_PLOTS

# =========================
# UTIL
# =========================
def safe_filename(text: str) -> str:
    text = re.sub(r"[^\w\-_. ]", "", text)
    return text.replace(" ", "_")

def parse_datetime_series(series):
    known_formats = [
        "%m/%d/%Y %I:%M:%S %p",  # English / US format
        "%d/%m/%Y %H:%M:%S",     # European format
        "%Y-%m-%d %H:%M:%S",     # ISO-like
        "%H:%M:%S",              # Time-only (from serial_update)
        ]
    for fmt in known_formats:
        try:
            parsed = to_datetime(series, format=fmt, errors="raise")
            return parsed
        except Exception:
            continue
    # fallback (slower but flexible)
    return to_datetime(series, errors="coerce")


# =========================
# LOAD DATA
# =========================
def detect_delimiter(filepath):
    """Safely sniffs the delimiter (comma, semicolon, or tab) by skipping metadata."""
    with open(filepath, "r", encoding="utf-8", errors="replace") as f:
        # Read past the metadata lines starting with '#'
        sample_lines = []
        for line in f:
            clean_line = line.strip()
            if not clean_line or clean_line.startswith("#"):
                continue
            sample_lines.append(clean_line)
            if len(sample_lines) >= 3:  # Grab a few lines of actual data
                break
        
        if not sample_lines:
            return ","  # Fallback default
            
        # Join the sample lines and sniff the delimiter
        sample_text = "\n".join(sample_lines)
        if ";" in sample_text:
            return ";"
        elif "\t" in sample_text:
            return "\t"
        else:
            return ","

def load_csv(csv_path):
    csv_path = Path(csv_path)
    
    # 1. Detect the delimiter manually and safely
    detected_sep = detect_delimiter(csv_path)
    
    # 2. Read the CSV using the precise delimiter found
    try:
        df = pd.read_csv(
            csv_path,
            sep=detected_sep,
            comment="#",
            engine="python",
            skip_blank_lines=True
        )
    except Exception as e:
        print(f"[ERROR] Could not read {csv_path.name}: {e}")
        return None
    
    # Strip any accidental white spaces from column names
    df.columns = df.columns.astype(str).str.strip()
    
    # Try to locate a date or time column
    date_col = next(
        (c for c in df.columns if any(x in c.lower() for x in ["date", "data", "fecha", "time"])),
        None
    )

    if date_col: 
        df[date_col] = parse_datetime_series(df[date_col])
        df_cleaned_by_date = df.dropna(subset=[date_col])

        if df_cleaned_by_date.empty:
            print(f"[WARNING] No valid dates found in '{date_col}'. Using numeric index.")
            return df
        else:
            df = df_cleaned_by_date.set_index(date_col)
    else: 
        print(f"[INFO] No date column in {csv_path.name}. Using sample number index.")

    return df


# =========================
# PLOT
# =========================
def create_plot(df, variable, title=""):
    # Handle potential duplicate column names and ensure numeric conversion
    data = df[variable]
    if isinstance(data, pd.DataFrame):
        data = data.iloc[:, 0]
    
    y_values = pd.to_numeric(data, errors='coerce').dropna()

    fig, ax = plt.subplots(figsize=(12, 6))

    if not y_values.empty:
        ax.plot(y_values.index, y_values.values, linewidth=1)

        # Calculate and plot median
        median_val = y_values.median()
        ax.axhline(median_val, color='red', linestyle='--', linewidth=1.5, alpha=0.7)
        ax.text(1.01, median_val, f"Median: {median_val:.4f}", color='red', va='center', ha='left', transform=ax.get_yaxis_transform())
    else:
        ax.text(0.5, 0.5, f"No numeric data available for: {variable}", 
                ha='center', va='center', transform=ax.transAxes)

    ax.set_title(title or variable)
    x_label = "Time" if isinstance(df.index, pd.DatetimeIndex) else "Sample Number"
    ax.set_xlabel(x_label)
    ax.set_ylabel(variable)

    ax.grid(True, linestyle="--", linewidth=0.5)
    ax.yaxis.set_major_locator(ticker.MaxNLocator(8))

    return fig


# =========================
# SAVE (CLEAN DESIGN)
# =========================
def save_plot(fig, plot_path: Path):
    plot_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(str(plot_path), dpi=300, bbox_inches='tight')
    plt.close(fig)

# =========================
# Previsualitza plot
# =========================
def plot_preview_plot(csv_path, variable: str):
    csv_path = Path(csv_path)

    df = load_csv(csv_path)
    if df is None:
        return None

    if variable not in df.columns:
        return None

    # Ensure numeric data and sorted index for correct line plotting
    df[variable] = pd.to_numeric(df[variable], errors='coerce')
    df_clean = df[[variable]].dropna().sort_index()

    if df_clean.empty:
        return None

    fig = create_plot(df_clean, variable, title=csv_path.stem)

    return fig

# =========================
# BATCH PROCESS
# =========================
def batch_plot(folder, output_folder, variables, filter_str=None):
    folder = Path(folder)
    output_folder = Path(output_folder)

    if filter_str:
        filters = [filter_str] if isinstance(filter_str, str) else filter_str
        csv_files = []
        for s in filters:
            csv_files.extend(folder.glob(f"*{s}*.csv"))
        csv_files = sorted(list(set(csv_files)))
    else:
        csv_files = list(folder.glob("*.csv"))

    print(f"CSV folder: {folder}")
    print(f"Files found: {len(csv_files)}")

    for csv_file in csv_files:
        print(f"\nProcessing: {csv_file.name}")

        df = load_csv(csv_file)
        if df is None:
            continue

        for var in variables:

            if var not in df.columns:
                print(f"Missing variable: {var}")
                continue

            # Ensure numeric data and sorted index for correct line plotting
            df[var] = pd.to_numeric(df[var], errors='coerce')
            df_clean = df[[var]].dropna().sort_index()

            if df_clean.empty:
                print(f"No data: {var}")
                continue
            filename = f"{csv_file.stem}_{safe_filename(var)}.png"
            plot_path = output_folder / filename

            if plot_path.exists():
                print(f"Skipping (already exists): {filename}")
                continue

            fig = create_plot(df_clean, var, title=csv_file.stem)
            save_plot(fig, plot_path)

            print(f"Saved: {filename}")


# =========================
# MAIN (CLI)
# =========================
def main(variables=None, filter_str=None):
    if variables is None:
        variables = ["MEASURE"]

    batch_plot(
        AT_RAW, # o STE_RAW
        OUTPUT_PLOTS,
        variables,
        filter_str=filter_str
    )


if __name__ == "__main__":
    main()
