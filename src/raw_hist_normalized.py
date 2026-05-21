import os
import csv
import statistics
import math
from pathlib import Path
import config
from config import DATA_RAW_HIST

# Output directory
TARGET_DIR = DATA_RAW_HIST.parent / "raw_hist_normalized"

def detect_delimiter(filepath):
    with open(filepath, "r", encoding='utf-8', errors='replace') as f:
        for line in f:
            clean_line = line.strip()
            if clean_line.startswith("#") or not clean_line:
                continue
            if "\t" in line: return "\t"
            if ";" in line: return ";"
            return ","
    return ","

def get_normalized_stats(headers, data_rows):
    """
    Finds the measurement column, normalizes values to m3/h, 
    and calculates new statistics.
    """
    # Priority mapping for columns
    targets = [
        "A Volumetric flow rate [m³/h]",
        "A Mass flow rate [kg/s]",
        "A Mass flow rate [kg/h]",
        "MEASURE"
    ]
    
    col_idx = None
    found_unit = "m3/h"

    for t in targets:
        try:
            col_idx = headers.index(t)
            found_unit = t
            break
        except ValueError:
            continue
            
    if col_idx is None:
        # Fallback: look for keywords
        for i, h in enumerate(headers):
            h_up = h.upper()
            if "FLOW RATE" in h_up or "MEASURE" in h_up:
                col_idx = i
                found_unit = h
                break

    if col_idx is None:
        return None, {k: "nan" for k in ["avg", "median", "mode", "max", "min"]}

    # Extract and normalize values
    norm_vals = []
    for row in data_rows:
        if len(row) <= col_idx: continue
        try:
            val_str = str(row[col_idx]).replace(',', '.')
            val = float(val_str)
            if not math.isfinite(val): continue
            
            # Conversion Logic to m3/h
            if "[kg/s]" in found_unit:
                val = val * 3.6
            elif "[kg/h]" in found_unit:
                val = val * 0.001
            
            norm_vals.append(val)
        except (ValueError, TypeError):
            continue

    if not norm_vals:
        return found_unit, {k: "nan" for k in ["avg", "median", "mode", "max", "min"]}

    try:
        mode_val = statistics.mode(norm_vals)
    except:
        mode_val = "nan"

    stats = {
        "avg": sum(norm_vals) / len(norm_vals),
        "median": statistics.median(norm_vals),
        "mode": mode_val,
        "max": max(norm_vals),
        "min": min(norm_vals)
    }
    return found_unit, stats

def process_file(filepath):
    print(f"Normalizing: {filepath.name}...")
    sep = detect_delimiter(filepath)
    
    metadata_lines = []
    headers = []
    data_rows = []
    
    # 1. Read
    with open(filepath, "r", encoding='utf-8', errors='replace', newline="") as f:
        reader = csv.reader(f, delimiter=sep)
        for row in reader:
            if not row: continue
            if row[0].startswith("#"):
                # Skip existing stats lines
                if any(x in row[0].upper() for x in ["STATS ->", "AVG:", "MEDIAN:", "MODE:", "MAX:", "MIN:"]):
                    continue
                metadata_lines.append(row[0])
            elif not headers and ("INDEX" in row[0].upper() or "DATE" in row[0].upper()):
                headers = row
            else:
                data_rows.append(row)

    if not headers:
        print(f"  [SKIPPED] No headers found.")
        return

    # 2. Normalize and Calc Stats
    _, m_stats = get_normalized_stats(headers, data_rows)

    # 3. Format new header
    fmt = lambda x: f"{x:.4f}" if isinstance(x, (int, float)) else str(x)
    new_stat_line = f"# A Volumetric flow rate [m3/h] Stats -> Avg: {fmt(m_stats['avg'])} | Median: {fmt(m_stats['median'])} | Mode: {fmt(m_stats['mode'])} | Max: {fmt(m_stats['max'])} | Min: {fmt(m_stats['min'])}"

    # 4. Write to new folder
    target_path = TARGET_DIR / filepath.name
    with open(target_path, "w", encoding='utf-8', newline="") as f:
        writer = csv.writer(f, delimiter=sep)
        writer.writerow([new_stat_line])
        for meta in metadata_lines:
            writer.writerow([meta])
        writer.writerow([]) # Spacer
        writer.writerow(headers)
        writer.writerows(data_rows)

    print(f"  [DONE] Saved to raw_hist_normalized")

def main():
    if not DATA_RAW_HIST.exists():
        print(f"Source path not found: {DATA_RAW_HIST}")
        return

    TARGET_DIR.mkdir(parents=True, exist_ok=True)

    for csv_file in sorted(DATA_RAW_HIST.glob("*.csv")):
        process_file(csv_file)

if __name__ == "__main__":
    main()