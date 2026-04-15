from pathlib import Path
import pandas as pd
from pandas import to_datetime
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import re
from config import DATA_RAW, OUTPUT_PLOTS



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
        ]
    for fmt in known_formats:
        try:
            parsed = to_datetime(series, format=fmt, errors="raise")
            return parsed
        except Exception:
            continue
    # fallback (slower but flexible)
    return to_datetime(series, errors="coerce", infer_datetime_format=True)


# =========================
# LOAD DATA
# =========================
def load_csv(csv_path: Path):
    df = pd.read_csv(csv_path, sep=None, engine="python")
    date_col = next(
        (c for c in df.columns if any(x in c.lower() for x in ["date", "data", "fecha"])),
        None
    )

    if date_col is None:
        print(f"[SKIP] No date column in {csv_path.name}")
        return None

    #df[date_col] = pd.to_datetime(df[date_col], errors="coerce") #old way
    df[date_col] = parse_datetime_series(df[date_col])
    df = df.dropna(subset=[date_col])

    if df.empty:
        print(f"[SKIP] No valid dates in {csv_path.name}")
        return None

    df = df.set_index(date_col)
    return df


# =========================
# PLOT
# =========================
def create_plot(df, variable, title=""):
    fig, ax = plt.subplots(figsize=(12, 6))

    ax.plot(df.index, df[variable], linewidth=1)

    ax.set_title(title or variable)
    ax.set_xlabel("Time")
    ax.set_ylabel(variable)

    ax.grid(True, linestyle="--", linewidth=0.5)
    ax.yaxis.set_major_locator(ticker.MaxNLocator(8))

    return fig


# =========================
# SAVE (CLEAN DESIGN)
# =========================
def save_plot(fig, plot_path: Path):
    plot_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(plot_path, dpi=300)
    plt.close(fig)


# =========================
# BATCH PROCESS
# =========================
def batch_plot(folder, output_folder, variables):
    folder = Path(folder)
    output_folder = Path(output_folder)

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

            df_clean = df[[var]].dropna()
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
def main(variables=None):
    variables = ["A Flow velocity [m/s]"]

    batch_plot(
        DATA_RAW,
        OUTPUT_PLOTS,
        variables
    )


if __name__ == "__main__":
    main()
