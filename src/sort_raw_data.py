import os
import csv
import statistics
import math
import pandas as pd
from pathlib import Path
from config import DATA_RAW, at_raw, ste_raw, OTHER_RAW, at_edges_csv, ste_edges_csv

# Mapping of filename Type to the actual column header representing the measurement
TYPE_COLUMN_MAP = {
    "Type1": "MEASURE",
    "Type2": "A Mass flow rate [kg/s]",
    "Type3": "A Mass flow rate [kg/h]",
    "Type4": "A Volumetric flow rate [m³/h]",
    "Type5": "A Mass flow rate [kg/h]",
    "Type6": "A Mass flow rate [kg/h]",
    "Type7": "A Mass flow rate [kg/h]",
    "Type8": "A Mass flow rate [kg/h]",
    "Type9": "MEASURE",
}

def normalize_id(id_val):
    """Ensures node IDs are compared consistently (e.g., '1.0' vs '1')."""
    try:
        f = float(id_val)
        if f == int(f):
            return str(int(f))
        return str(f)
    except (ValueError, TypeError):
        return str(id_val).strip()

def get_file_info(filename):
    """Extracts point name and type from filename."""
    parts = Path(filename).stem.split("_")
    point_name = parts[2] if len(parts) >= 3 else Path(filename).stem
    file_type = parts[-1] if parts[-1].startswith("Type") else "Type1"
    return normalize_id(point_name), file_type

def detect_delimiter(filepath):
    """Sniffs the delimiter by checking the first non-comment, non-empty line."""
    with open(filepath, "r", encoding='utf-8', errors='replace') as f:
        sample = ""
        for line in f:
            if line.startswith("#") or not line.strip():
                continue
            sample += line
            if sample.count('\n') >= 5:
                break

        if not sample:
            return ";"

        try:
            dialect = csv.Sniffer().sniff(sample, delimiters=",\t; ")
            return dialect.delimiter
        except Exception:
            return ";"  # Fallback to semicolon

def calculate_normalized_stats(vals, unit_context=""):
    """Computes statistics for values normalized to m3/h."""
    clean_vals = []
    for v in vals:
        try:
            f_val = float(str(v).replace(',', '.'))
            if not math.isfinite(f_val): continue
            
            # Normalization to m3/h
            if "[kg/s]" in unit_context:
                f_val = f_val * 3.6
            elif "[kg/h]" in unit_context:
                f_val = f_val * 0.001
            
            clean_vals.append(f_val)
        except (ValueError, TypeError):
            continue

    if not clean_vals:
        return {k: "nan" for k in ["avg", "median", "mode", "max", "min"]}
    
    try:
        mode_val = statistics.mode(clean_vals)
    except Exception:
        mode_val = "nan"
        
    return {
        "avg": sum(clean_vals) / len(clean_vals),
        "median": statistics.median(clean_vals),
        "mode": mode_val,
        "max": max(clean_vals),
        "min": min(clean_vals)
    }

count_processed = 0
def process_file(filepath, at_set, ste_set):
    global count_processed
    count_processed += 1
    point_id, file_type = get_file_info(filepath.name)
    
    # Determine Destination folder based on the node definitions
    if point_id in at_set:
        dest_dir = at_raw
    elif point_id in ste_set:
        dest_dir = ste_raw
    else:
        dest_dir = OTHER_RAW

    dest_dir.mkdir(parents=True, exist_ok=True)
    target_path = dest_dir / filepath.name
    
    sep = detect_delimiter(filepath)
    target_col = TYPE_COLUMN_MAP.get(file_type, "MEASURE")
    
    metadata_lines, headers, data_rows = [], [], []
    with open(filepath, "r", encoding='utf-8', errors='replace', newline="") as f:
        reader = csv.reader(f, delimiter=sep)
        for row in reader:
            if not row: continue
            if row[0].startswith("#"):
                # Skip old stats to avoid doubling up
                if any(x in row[0].upper() for x in ["STATS", "FLOW RATE:", "AVG:", "MEDIAN:", "MODE:", "MAX:", "MIN:"]): continue
                metadata_lines.append(row[0])
            elif not headers and (target_col in row or "MEASURE" in row or "INDEX" in row[0].upper()):
                headers = row
            else:
                data_rows.append(row)

    if not headers: 
        print(f"{count_processed}: Skipped {filepath.name} - Header not found (expected '{target_col}' or 'MEASURE')")
        return

    print(f"{count_processed}: Saving {filepath.name} to {dest_dir.name}...")

    # Calculate Stats (normalized to m3/h)
    measure_idx = headers.index(target_col) if target_col in headers else None
    vals = [row[measure_idx] for row in data_rows if measure_idx is not None and len(row) > measure_idx]
    stats = calculate_normalized_stats(vals, unit_context=target_col)

    # Write to target location
    with open(target_path, "w", encoding='utf-8', newline="") as f:
        writer = csv.writer(f, delimiter=sep)
        
        # Write stats as separate rows to avoid quoting
        if stats['avg'] != "nan":
            fmt = lambda x: f"{x:.4f}" if isinstance(x, (int, float)) else str(x)
            writer.writerow([f"# {target_col} Stats"])
            writer.writerow([f"# Avg: {fmt(stats['avg'])}"])
            writer.writerow([f"# Median: {fmt(stats['median'])}"])
            writer.writerow([f"# Mode: {fmt(stats['mode'])}"])
            writer.writerow([f"# Max: {fmt(stats['max'])}"])
            writer.writerow([f"# Min: {fmt(stats['min'])}"])

        for meta in metadata_lines: writer.writerow([meta])
        writer.writerow([])
        writer.writerow(headers)
        writer.writerows(data_rows)

def main():
    at_set = set(pd.read_csv(at_edges_csv)["nom"].apply(normalize_id)) if at_edges_csv.exists() else set()
    ste_set = set(pd.read_csv(ste_edges_csv)["nom"].apply(normalize_id)) if ste_edges_csv.exists() else set()
    for csv_file in sorted(DATA_RAW.glob("*.csv")):
        process_file(csv_file, at_set, ste_set)

if __name__ == "__main__":
    main()