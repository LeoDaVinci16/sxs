# add_date.py

import os
import pandas as pd
import re
from pathlib import Path

ROOT_FOLDER = Path(__file__).parents[1]  # go up 2 levels from script
RAW_FOLDER = os.path.join(ROOT_FOLDER, "data", "raw")
DRY_RUN = True  # set False to actually rename files

# Regex to detect if filename is already in the correct format
pattern_correct_name = re.compile(r"^\d{8}_\d{6}_.+\.csv$")

def list_csv_files(folder):
    """List all CSV files in a folder."""
    return [f for f in os.listdir(folder) if f.endswith(".csv")]


def is_correct_format(filename):
    """Check if the filename matches the correct pattern."""
    return pattern_correct_name.match(filename)


def read_csv_safe(filepath):
    """Read CSV with tab separator, return None on error."""
    try:
        return pd.read_csv(filepath, sep="\t")
    except Exception as e:
        print(f"Failed to read {os.path.basename(filepath)}: {e}")
        return None


def detect_date_column(df):
    """Find a column that looks like a date, return None if not found."""
    for c in df.columns:
        if any(p in c.lower() for p in ["date", "data", "fecha"]):
            if not df[c].dropna().empty:
                return c
    return None


def extract_datetime(df, date_col):
    """Get the first datetime from the date column and return date_str and time_str."""
    first_date = pd.to_datetime(df[date_col].dropna().iloc[0])
    return first_date.strftime("%Y%m%d"), first_date.strftime("%H%M%S")


def extract_point_id(filename):
    """Extract the point ID from the filename using regex or fallback to basename."""
    match = re.search(r"AT-(.+)\.csv", filename)
    return match.group(1) if match else filename.rsplit(".csv", 1)[0]


def build_new_filename(date_str, time_str, point_id):
    """Build new filename in the format: YYYYMMDD_HHMMSS_pointID.csv"""
    return f"{date_str}_{time_str}_{point_id}.csv"


def rename_file(old_path, new_path):
    """Rename a file if it doesn’t exist yet."""
    if os.path.exists(new_path):
        print(f"Skipping {os.path.basename(old_path)}, {os.path.basename(new_path)} already exists")
        return
    os.rename(old_path, new_path)
    print(f"Renamed {os.path.basename(old_path)} -> {os.path.basename(new_path)}")


def process_csv_file(folder, filename, dry_run=True):
    """Process a single CSV file: read, detect date, generate new name, rename."""
    if is_correct_format(filename):
        print(f"Skipping {filename}, already in correct format")
        return

    path = os.path.join(folder, filename)
    df = read_csv_safe(path)
    if df is None:
        return

    date_col = detect_date_column(df)
    if date_col is None:
        print(f"No valid Date column in {filename}")
        return

    date_str, time_str = extract_datetime(df, date_col)
    point_id = extract_point_id(filename)
    new_name = build_new_filename(date_str, time_str, point_id)
    new_path = os.path.join(folder, new_name)

    if dry_run:
        print(f"{filename} -> {new_name}")
    else:
        rename_file(path, new_path)


def main():
    csv_files = list_csv_files(RAW_FOLDER)
    for f in csv_files:
        process_csv_file(RAW_FOLDER, f, dry_run=DRY_RUN)


if __name__ == "__main__":
    main()