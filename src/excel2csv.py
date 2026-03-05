# excel2csv.py
from pathlib import Path
import pandas as pd
import os

root_folder = Path(__file__).parents[1]
docs_folder = os.path.join(root_folder, "docs")

# Loop through all files in input_folder
for filename in os.listdir(docs_folder):
    if filename.endswith(".xlsx") or filename.endswith(".xls"):
        excel_path = os.path.join(docs_folder, filename)
        # Read Excel file
        df = pd.read_excel(excel_path)
        # Create CSV file path
        csv_filename = os.path.splitext(filename)[0] + ".csv"
        csv_path = os.path.join(docs_folder, csv_filename)
        # Save to CSV
        df.to_csv(csv_path, index=False)
        print(f"Converted {filename} -> {csv_filename}")

print("All Excel files converted to CSV!")