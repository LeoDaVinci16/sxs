import os
import pandas as pd
import re
from pathlib import Path

ROOT_FOLDER = Path(__file__).parents[1]  # go up 2 levels total from script file
RAW_FOLDER = os.path.join(ROOT_FOLDER, "data", "raw")

DRY_RUN = True

# Regex to detect if filename is already in the correct format
# Example: 20260303_143015_AT-123.csv or 20260303_143015_123.csv
pattern_correct_name = re.compile(r"^\d{8}_\d{6}_.+\.csv$")

for file in os.listdir(RAW_FOLDER):
    if not file.endswith(".csv"):
        continue

    # Skip if filename is already in correct format
    if pattern_correct_name.match(file):
        print(f"Skipping {file}, already in correct format")
        continue

    path = os.path.join(RAW_FOLDER, file)

    try:
        df = pd.read_csv(path, sep="\t")
    except Exception as e:
        print(f"Failed to read {file}: {e}")
        continue

    # Robust date column detection
    date_col = next((c for c in df.columns if any(p in c.lower() for p in ["date", "data", "fecha"])), None)
    if date_col is None or df[date_col].dropna().empty:
        print(f"No valid Date column in {file}")
        continue

    first_date = pd.to_datetime(df[date_col].dropna().iloc[0])
    date_str = first_date.strftime("%Y%m%d")
    time_str = first_date.strftime("%H%M%S")

    # Point ID extraction using regex
    match = re.search(r"AT-(.+)\.csv", file)
    point_id = match.group(1) if match else file.rsplit(".csv", 1)[0]

    new_name = f"{date_str}_{time_str}_{point_id}.csv"
    new_path = os.path.join(RAW_FOLDER, new_name)

    if DRY_RUN:
        print(f"{file} -> {new_name}")
    else:
        if os.path.exists(new_path):
            print(f"Skipping {file}, {new_name} already exists")
            continue
        os.rename(path, new_path)
        print(f"Renamed {file} -> {new_name}")