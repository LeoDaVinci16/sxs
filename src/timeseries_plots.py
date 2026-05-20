import matplotlib.pyplot as plt
import pandas as pd
import os
from pathlib import Path
from config import DATA_TIMESERIES, OUTPUT_SUMMARY

# 1. Load your data
timeseries_csv_path = DATA_TIMESERIES / "timeseries_5.csv"
df = pd.read_csv(timeseries_csv_path, sep=";")
variable = "MEASURE_Median"


# 2. Create an output directory for the plots if it doesn't exist
output_folder = OUTPUT_SUMMARY
os.makedirs(output_folder, exist_ok=True)

# 3. Get a list of all unique measurement points (ignoring missing ones)
unique_points = df["Meas. Point No."].dropna().unique()

print(f"Found {len(unique_points)} unique measurement points. Generating plots...")

# 4. Loop through every single measurement point
for target_point in unique_points:
    print(target_point)
    # Filter data for this specific point
    df_filtered = df[df["Meas. Point No."] == target_point].dropna(
        subset=["MEASURE_Avg"]
    )

    # Skip if there's no actual numerical data to plot for this point
    if df_filtered.empty:
        #print(f"Skipping {target_point} (No valid MEASURE_Avg values)")
        continue

    # Prepare labels and sort chronologically
    df_filtered["Time_Label"] = (
        df_filtered["DATE"] + "\n" + df_filtered["TIME"]
    )
    df_filtered["_datetime"] = pd.to_datetime(
        df_filtered["DATE"] + " " + df_filtered["TIME"],
        format="%d.%m.%Y %H:%M:%S",
    )
    df_filtered = df_filtered.sort_values("_datetime")

    # Generate the column plot
    plt.figure(figsize=(10, 6))
    bars = plt.bar(
        df_filtered["Time_Label"],
        df_filtered["MEASURE_Avg"],
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
    plt.ylabel("MEASURE_Avg (Volume Flow)", fontsize=12)
    plt.grid(axis="y", linestyle="--", alpha=0.5)

    # Add numeric tags above bars
    max_val = df_filtered["MEASURE_Avg"].max()
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
    filepath = os.path.join(output_folder, f"plot_{safe_filename}.png")

    # Save the file and close the figure to free up system memory
    plt.savefig(filepath, dpi=150)
    plt.close()

    #print(f"Saved: {filepath}")

print("All plots generated successfully!")