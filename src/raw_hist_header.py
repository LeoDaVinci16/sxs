import os
import re
import csv
import statistics
import math
from pathlib import Path
from config import DATA_RAW_HIST

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
    "Type9": "MEASURE", # Fallback for 'other'
}

def get_type_from_filename(filename):
    """Extracts 'TypeX' from filename. Defaults to Type1."""
    parts = Path(filename).stem.split("_")
    return parts[-1] if parts[-1].startswith("Type") else "Type1"

def detect_delimiter(filepath):
    """Sniffs the delimiter by checking the first non-comment, non-empty line."""
    with open(filepath, "r", encoding='utf-8', errors='replace') as f:
        for line in f:
            clean_line = line.strip()
            if clean_line.startswith("#") or not clean_line:
                continue
            if "\t" in line: return "\t"
            if ";" in line: return ";"
            return ","
    return ","

def calculate_stats(vals):
    """Computes statistics for a list of values, filtering out non-numeric entries."""
    # Filter out None, NaN, or Inf
    clean_vals = []
    for v in vals:
        try:
            f_val = float(str(v).replace(',', '.'))
            if math.isfinite(f_val): 
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

def process_hist_file(filepath):
    print(f"Updating header for: {filepath.name}...")
    
    sep = detect_delimiter(filepath)
    file_type = get_type_from_filename(filepath.name)
    target_col = TYPE_COLUMN_MAP.get(file_type, "MEASURE")

    metadata_lines = []
    headers = []
    data_rows = []
    
    # 1. Read existing content carefully
    try:
        with open(filepath, "r", encoding='utf-8', errors='replace', newline="") as f:
            reader = csv.reader(f, delimiter=sep)
            for row in reader:
                if not row:
                    continue
                # Capture metadata, but skip old stats lines we want to override
                if row[0].startswith("#"):
                    content_upper = row[0].upper()
                    if "STATS ->" in content_upper or "AVERAGE" in content_upper:
                        continue
                    metadata_lines.append(row[0])
                # Identify column headers
                elif not headers and (target_col in row or "INDEX" in row[0].upper() or "DATE" in row[0].upper()):
                    headers = row
                # Data rows
                else:
                    data_rows.append(row)
    except Exception as e:
        print(f"  [ERROR] Failed to read {filepath.name}: {e}")
        return

    if not headers:
        print(f"  [SKIPPED] Could not find headers in {filepath.name}")
        return

    # 2. Identify the column index for measurement
    try:
        measure_idx = headers.index(target_col)
    except ValueError:
        measure_idx = next((i for i, h in enumerate(headers) if any(x in h.upper() for x in ["MEASURE", "FLOW RATE", "MASS FLOW"])), None)

    if measure_idx is not None:
        vals = [row[measure_idx] for row in data_rows if len(row) > measure_idx]
        m_stats = calculate_stats(vals)
    else:
        print(f"  [WARNING] Target column '{target_col}' not found. Stats will be nan.")
        m_stats = calculate_stats([])

    # 4. Write back with the new standard header
    fmt = lambda x: f"{x:.4f}" if isinstance(x, (int, float)) else str(x)
    new_stat_line = (
        f"# {target_col} \n"
        f"# Avg: {fmt(m_stats['avg'])}\n"
        f"# Median: {fmt(m_stats['median'])}\n"
        f"# Mode: {fmt(m_stats['mode'])}\n"
        f"# Max: {fmt(m_stats['max'])}\n"
        f"# Min: {fmt(m_stats['min'])}\n"
    )
    try:
        with open(filepath, "w", encoding='utf-8', newline="") as f:
            
            # Write the new stats header
            f.write(new_stat_line)
            
            # Write preserved metadata (like DEVICE, DATE, etc)
            for meta in metadata_lines:
                f.write(f"{meta}\n")

            writer = csv.writer(f, delimiter=sep)
                
            # Write data rows
            writer.writerow([]) # Blank spacer
            writer.writerow(headers)
            writer.writerows(data_rows)
    except Exception as e:
        print(f"  [ERROR] Failed to write {filepath.name}: {e}")
        return
        
    print(f"  [DONE] Median: {fmt(m_stats['median'])}")

def main():
    if not DATA_RAW_HIST.exists():
        print(f"Path not found: {DATA_RAW_HIST}")
        return

    for csv_file in sorted(DATA_RAW_HIST.glob("*.csv")):
        process_hist_file(csv_file)

if __name__ == "__main__":
    main()