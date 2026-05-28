import csv
import os
import re
from datetime import datetime, timedelta
import statistics
from config import DATA_RAW, at_raw, ste_raw

def calculate_stats(vals):
    """Computes basic statistics for a list of numeric values."""
    if not vals:
        return {k: "N/A" for k in ["avg", "median", "mode", "max", "min"]}
    
    try:
        mode_val = statistics.mode(vals)
    except Exception:
        mode_val = "N/A"
        
    return {
        "avg": sum(vals) / len(vals),
        "median": statistics.median(vals),
        "mode": mode_val,
        "max": max(vals),
        "min": min(vals)
    }

def detect_delimiter(filepath):
    """Sniffs the delimiter by checking a non-comment line."""
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

def post_process_file(filepath):
    print(f"Processing: {filepath}...")
    filepath = os.path.abspath(filepath)
    
    if not os.path.exists(filepath):
        return

    sep = detect_delimiter(filepath)
    
    metadata_lines = []
    headers = []
    data_rows = []
    
    # 1. Read the raw, unfiltered CSV file
    with open(filepath, "r", newline="", encoding='utf-8', errors='replace') as f:
        reader = csv.reader(f, delimiter=sep)
        for row in reader:
            if not row:
                continue
            
            # Identify metadata lines (they start with "#")
            if row[0].startswith("#"):
                # Avoid doubling up stats if the script is run twice
                if not any(s in row[0] for s in ["Stats", "Avg:", "Median:", "Mode:", "Max:", "Min:", "Average "]):
                    metadata_lines.append(row[0])
            # Identify column headers
            elif "CHANNEL" in row:
                headers = row
            # Identify data rows
            else:
                data_rows.append(row)

    if not headers or not data_rows:
        print(f"Skipping {filepath}: No data rows or headers found.")
        return

    # --- Generate TIME column from metadata ---
    start_time_str = None
    storage_rate_str = None
    for meta in metadata_lines:
        if "# TIME" in meta:
            m = re.search(r"(\d{2}:\d{2}:\d{2})", meta)
            if m: start_time_str = m.group(1)
        if "Storage Rate" in meta:
            m = re.search(r"(\d{2}:\d{2}:\d{2})", meta)
            if m: storage_rate_str = m.group(1)

    if start_time_str and storage_rate_str and "TIME" not in headers: 
        try:
            t = datetime.strptime(start_time_str, "%H:%M:%S")
            h, m, s = map(int, storage_rate_str.split(":"))
            delta = timedelta(hours=h, minutes=m, seconds=s)
            headers.insert(0, "TIME") # Insert at the beginning
            for row in data_rows:
                row.insert(0, t.strftime("%H:%M:%S")) # Insert at the beginning
                t += delta
        except Exception as e:
            print(f"Error generating TIME column for {filepath}: {e}")

    # 2. Dynamically locate the column indices
    measure_idx = None
    for idx, col in enumerate(headers):
        clean_col = col.upper()
        if "MEASURE" in clean_col:
            measure_idx = idx

    measure_vals = []

    # 3. Extract values for averaging
    for row in data_rows:
        if measure_idx is not None and len(row) > measure_idx:
            try:
                measure_vals.append(float(row[measure_idx]))
            except ValueError:
                pass  # Safely bypass non-numeric values like "???"

    m_stats = calculate_stats(measure_vals)

    # 4. Overwrite the file with the final polished format
    with open(filepath, "w", newline="", encoding='utf-8') as f:
        w = csv.writer(f, delimiter=sep)

        # Write clean metadata
        for meta in metadata_lines:
            w.writerow([meta])
        # Write headers and data rows
        w.writerow(headers)
        w.writerows(data_rows)
            
        # Write computed stats
        if m_stats["avg"] != "N/A":
            fmt = lambda x: f"{x:.4f}" if isinstance(x, (int, float)) else str(x)
            w.writerow(["# MEASURE Stats"])
            w.writerow([f"# Avg: {fmt(m_stats['avg'])}"])
            w.writerow([f"# Median: {fmt(m_stats['median'])}"])
            w.writerow([f"# Mode: {fmt(m_stats['mode'])}"])
            w.writerow([f"# Max: {fmt(m_stats['max'])}"])
            w.writerow([f"# Min: {fmt(m_stats['min'])}"])
        w.writerow([])  # Blank spacer

        # Write clean metadata
        for meta in metadata_lines:
            w.writerow([meta])
        # Write headers and data rows
        w.writerow(headers)
        w.writerows(data_rows)

    print(f"Successfully processed! Stats -> Average: {m_stats['avg']} | Median: {m_stats['median']} | Mode: {m_stats['mode']} | Max: {m_stats['max']} | Min: {m_stats['min']}")
    print("\n")


# --- Main Execution ---
if __name__ == "__main__":
    # Find all CSV files in the current folder
    csv_files = [os.path.join(DATA_RAW, f) for f in os.listdir(DATA_RAW) if f.endswith(".csv")]
    
    if not csv_files:
        print(f"No CSV files found in {DATA_RAW} to process.")
    else:
        for filepath in csv_files:
            post_process_file(filepath)