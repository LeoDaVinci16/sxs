import re
import config
import pandas as pd
from pathlib import Path

def extract_file_info(csv_path):
    """
    Extracts metadata and statistics from the commented header of a CSV.
    Returns a flat dictionary for CSV row generation.
    """
    info = {"Filename": csv_path.name}  
    try:
        with open(csv_path, 'r', encoding='utf-8', errors='replace') as f:
            for line in f:
                clean_line = line.strip()
                if clean_line.startswith("#"):
                    # Remove '#' and leading/trailing whitespace
                    content = clean_line.lstrip("#").strip()
                    
                    if "Stats ->" in content:
                        # Parse statistics lines
                        # Example: "MEASURE Stats -> Avg: 0.1 | Median: 0.1..."
                        parts = content.split("->")
                        label = parts[0].replace("Stats", "").strip()
                        metrics = parts[1].split("|")
                        for m in metrics:
                            if ":" in m:
                                k, v = m.split(":", 1)
                                info[f"{label}_{k.strip()}"] = v.strip()
                    elif ":" in content:
                        # Parse standard metadata lines
                        # Example: "\DEVICE : G 608ST..."
                        k, v = content.split(":", 1)
                        # Clean key: remove leading backslashes, colons and whitespace
                        clean_key = re.sub(r"^[\\:\s]+", "", k).strip()
                        info[clean_key] = v.strip()
                elif not clean_line:
                    continue
                else:
                    # End of header metadata
                    break
    except Exception as e:
        print(f"Error reading {csv_path.name}: {e}")
        
    return info

def main():
    """
    Iterates through all CSV files in the raw data folder and aggregates 
    their metadata and stats into a single summary CSV file.
    """
    # 1. Select all CSV files in the raw folder
    summary_csv_path = config.DATA_TIMESERIES / "timeseries.csv"
    
    # Load existing summary data if it exists
    existing_df = pd.DataFrame()
    if summary_csv_path.exists():
        try:
            # Use sep=None with engine='python' to auto-detect separator (comma vs semicolon)
            existing_df = pd.read_csv(summary_csv_path, sep=None, engine='python')
            # Remove potential whitespace from column names to prevent KeyErrors
            existing_df.columns = existing_df.columns.str.strip()
            print(f"Loaded existing summary with {len(existing_df)} entries from {summary_csv_path}")
        except Exception as e:
            print(f"[WARNING] Could not load existing summary CSV: {e}. Starting fresh.")
            existing_df = pd.DataFrame()

    # Get filenames already processed
    processed_filenames = set()
    if not existing_df.empty:
        if 'Filename' in existing_df.columns:
            processed_filenames = set(existing_df['Filename'].tolist())
        else:
            print(f"[WARNING] 'Filename' column missing in {summary_csv_path}. Re-processing all files.")
            existing_df = pd.DataFrame()

    # Get all raw CSV files
    all_raw_files = sorted(list(config.DATA_RAW.glob("*.csv")))
    
    if not all_raw_files and existing_df.empty:
        print(f"No files found in {config.DATA_RAW} and no existing summary. Nothing to do.")
        return
    
    # Identify new files that haven't been processed yet
    new_raw_files = [f for f in all_raw_files if f.name not in processed_filenames]

    if not new_raw_files:
        print("No new files found in DATA_RAW to add to the summary.")
        if existing_df.empty: # If no new files and no existing data, still nothing to do
            return
        else: # If no new files but existing data, just confirm
            print(f"Summary remains unchanged at {summary_csv_path}.")
            return

    print(f"Found {len(new_raw_files)} new files. Extracting metadata...")
    
    new_data = []
    for csv_file in new_raw_files:
        file_info = extract_file_info(csv_file)
        new_data.append(file_info)
        
    # Convert new collected data to a DataFrame
    # Pandas handles different keys across files by filling missing ones with NaN
    new_df = pd.DataFrame(new_data)
    
    # Combine existing and new data
    if existing_df.empty:
        final_df = new_df
    else:
        final_df = pd.concat([existing_df, new_df], ignore_index=True)
    
    # Ensure output directory exists
    config.DATA_TIMESERIES.mkdir(parents=True, exist_ok=True)
    
    # Save to CSV
    final_df.to_csv(summary_csv_path, index=False, sep=";")
    
    print("-" * 30)
    print(f"Success! Summary report updated with {len(new_df)} new entries. Total entries: {len(final_df)}.")
    print(f"Location: {summary_csv_path}")

if __name__ == "__main__":
    main()