import os
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
from config import at_raw as AT_RAW, ste_raw as STE_RAW, at_boxplots as OUTPUT_BOXPLOTS
from create_plots import load_csv, safe_filename

def create_boxplot(df, variable, title=""):
    """Creates a boxplot for a specific variable."""
    # Handle potential duplicate column names and ensure numeric conversion
    raw_data = df[variable]
    if isinstance(raw_data, pd.DataFrame):
        raw_data = raw_data.iloc[:, 0]
    
    data = pd.to_numeric(raw_data, errors='coerce').dropna()

    fig, ax = plt.subplots(figsize=(8, 6))

    if not data.empty:
        ax.boxplot(data, patch_artist=True, 
                boxprops=dict(facecolor='lightblue', color='blue'),
                medianprops=dict(color='red', linewidth=2))

        ax.set_ylabel(variable)
        ax.set_xticks([1])
        ax.set_xticklabels([variable])
        ax.grid(True, linestyle="--", linewidth=0.5, axis='y', alpha=0.7)
    else:
        ax.text(0.5, 0.5, f"No numeric data for {variable}", 
                ha='center', va='center', transform=ax.transAxes)

    ax.set_title(title or f"Boxplot: {variable}")

    return fig

def save_plot(fig, plot_path: Path):
    """Saves the figure to the specified path."""
    plot_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(str(plot_path), dpi=300, bbox_inches='tight')
    plt.close(fig)

def plot_preview_boxplot(csv_path, variable: str):
    """Generates a boxplot figure for a single variable from a CSV file."""
    csv_path = Path(csv_path)

    df = load_csv(csv_path)
    if df is None:
        return None

    if variable not in df.columns:
        return None

    # Ensure numeric data
    df[variable] = pd.to_numeric(df[variable], errors='coerce')
    df_clean = df[[variable]].dropna()

    if df_clean.empty:
        return None

    fig = create_boxplot(df_clean, variable, title=csv_path.stem)

    return fig

def batch_boxplot(folder, output_folder, variables, filter_str=None):
    """Iterates over CSV files and generates boxplots for the selected variables."""
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
    print(f"Output folder: {output_folder}")

    for csv_file in csv_files:
        print(f"\nProcessing Boxplots for: {csv_file.name}")

        df = load_csv(csv_file)
        if df is None:
            continue

        for var in variables:
            if var not in df.columns:
                # Skip variables not found in the current file
                continue

            # Ensure numeric data
            df[var] = pd.to_numeric(df[var], errors='coerce')
            df_clean = df[[var]].dropna()

            if df_clean.empty:
                print(f"No data for: {var}")
                continue

            filename = f"{csv_file.stem}_boxplot_{safe_filename(var)}.png"
            plot_path = output_folder / filename

            if plot_path.exists():
                print(f"Skipping (already exists): {filename}")
                continue

            fig = create_boxplot(df_clean, var, title=f"Boxplot: {csv_file.stem}")
            if fig:
                save_plot(fig, plot_path)
                print(f"Saved: {filename}")

def main(variables=None, filter_str=None):
    # Example variables based on existing project usage
    if variables is None:
        variables = ["A Flow velocity [m/s]", "MEASURE", "SSPEED"]

    batch_boxplot(
        AT_RAW, # o STE_RAW
        OUTPUT_BOXPLOTS,
        variables,
        filter_str=filter_str
    )

if __name__ == "__main__":
    main()