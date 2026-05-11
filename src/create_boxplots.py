import os
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
from config import DATA_RAW, OUTPUT_BOXPLOTS
from create_plots import load_csv, safe_filename

def create_boxplot(df, variable, title=""):
    """Creates a boxplot for a specific variable."""
    fig, ax = plt.subplots(figsize=(8, 6))

    # Create the boxplot
    # We ensure we are plotting numeric data without NaNs
    data = df[variable].dropna()
    
    if data.empty:
        plt.close(fig)
        return None

    ax.boxplot(data, patch_artist=True, 
               boxprops=dict(facecolor='lightblue', color='blue'),
               medianprops=dict(color='red', linewidth=2))

    ax.set_title(title or f"Boxplot: {variable}")
    ax.set_ylabel(variable)
    ax.set_xticklabels([variable])
    ax.grid(True, linestyle="--", linewidth=0.5, axis='y', alpha=0.7)

    return fig

def save_plot(fig, plot_path: Path):
    """Saves the figure to the specified path."""
    plot_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(plot_path, dpi=300, bbox_inches='tight')
    plt.close(fig)

def batch_boxplot(folder, output_folder, variables):
    """Iterates over CSV files and generates boxplots for the selected variables."""
    folder = Path(folder)
    output_folder = Path(output_folder)

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

def main():
    # Example variables based on existing project usage
    variables = ["A Flow velocity [m/s]", "MEASURE", "SSPEED"]

    batch_boxplot(
        DATA_RAW,
        OUTPUT_BOXPLOTS,
        variables
    )

if __name__ == "__main__":
    main()