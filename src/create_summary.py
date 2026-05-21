import matplotlib.pyplot as plt
import pandas as pd
import os
from pathlib import Path
from config import DATA_TIMESERIES, OUTPUT_SUMMARY

# 1. Load your data
timeseries_csv_path = DATA_TIMESERIES / "timeseries_normalized_1.csv"
df = pd.read_csv(timeseries_csv_path, sep=";")
count = 0


# 2. Create an output directory for the plots if it doesn't exist
output_folder = OUTPUT_SUMMARY
os.makedirs(output_folder, exist_ok=True)

# 3. Get a list of all unique measurement points (ignoring missing ones)
unique_points = df["POINTNAME"].dropna().unique()

# Helper to find the correct Median column (e.g. 'Median' or 'MEASURE_Median')
def find_median_col(columns):
    return next((c for c in columns if "Median" in c), None)

median_col = find_median_col(df.columns)
if not median_col:
    print("Error: Could not find any column containing 'Median' in the CSV.")
    exit()

print(f"Found {len(unique_points)} unique measurement points. Generating plots...")

# 4. Loop through every single measurement point
for target_point in unique_points:
    # Filter data for this specific point
    df_filtered = df[df["POINTNAME"] == target_point].copy()

    # Convert to numeric and drop NAs
    df_filtered[median_col] = pd.to_numeric(df_filtered[median_col], errors='coerce')
    df_filtered = df_filtered.dropna(subset=[median_col])

    # Skip if there's no actual numerical data to plot for this point
    if df_filtered.empty:
        print(f"Skipping {target_point} (No valid {median_col} values)")
        continue

    # Prepare labels and sort chronologically
    df_filtered["Time_Label"] = (
        df_filtered["DATE"].astype(str) + "\n" + df_filtered["TIME"].astype(str)
    )

    def robust_parse(row):
        dt_str = f"{str(row['DATE'])} {str(row['TIME'])}"
        # Try multiple formats: Standard, Filename-compact, and ISO
        for fmt in ["%d.%m.%Y %H:%M:%S", "%y%m%d %H%M", "%Y-%m-%d %H:%M:%S"]:
            try:
                return pd.to_datetime(dt_str, format=fmt)
            except ValueError:
                continue
        return pd.to_datetime(dt_str, errors='coerce')

    df_filtered["_datetime"] = df_filtered.apply(robust_parse, axis=1)
    df_filtered = df_filtered.dropna(subset=["_datetime"])
    df_filtered = df_filtered.sort_values("_datetime")

    # Generate the column plot
    plt.figure(figsize=(10, 6))
    bars = plt.bar(
        df_filtered["Time_Label"],
        df_filtered[median_col],
        color="teal",
        edgecolor="black",
        width=0.5,
    )

    # Titles and formatting
    plt.title(
        f"Average Flow Measurements for Node {target_point}",
        fontsize=14,
        fontweight="bold",
        pad=15,
    )
    plt.xlabel("Measurement Date & Time", fontsize=12, labelpad=10)

    # Get the type for the label (taking the first available entry for this point)
    target_type = df_filtered["Type"].iloc[0] if "Type" in df_filtered.columns and not df_filtered.empty else ""
    plt.ylabel(f"{median_col} (flow) {target_type}", fontsize=12)
    plt.grid(axis="y", linestyle="--", alpha=0.5)

    # Add numeric tags above bars
    max_val = df_filtered[median_col].max()
    for bar in bars:
        yval = bar.get_height()
        plt.text(
            bar.get_x() + bar.get_width() / 2,
            yval + (max_val * 0.01),
            f"{yval:.4f}",
            ha="center",
            va="bottom",
            fontsize=9,
        )

    plt.tight_layout()

    # Sanitize the name so it can be saved as a safe filename without weird characters
    safe_filename = (
        "".join(
            c for c in str(target_point) if c.isalnum() or c in (" ", "_", "-")
        )
        .strip()
        .replace(" ", "_")
    )
    filepath = os.path.join(output_folder, f"summary_{safe_filename}.png")

    # Save the file and close the figure to free up system memory
    plt.savefig(filepath, dpi=150)
    plt.close()

    print(f"Saved: {filepath}")
    count += 1

print(f"All {count} plots generated successfully!")
