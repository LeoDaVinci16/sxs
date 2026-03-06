# update_docs.py

from pathlib import Path
import os
import pandas as pd

# ==============================
# 0️⃣ CONFIG
# ==============================
ROOT_FOLDER = Path(__file__).parents[1]
DOCS_FOLDER = os.path.join(ROOT_FOLDER, "docs")
CSV_FOLDER = os.path.join(ROOT_FOLDER, "data", "csv")  # CSVs updated here

# Make sure CSV_FOLDER exists
os.makedirs(CSV_FOLDER, exist_ok=True)

# ==============================
# 1️⃣ LIST FILES
# ==============================
def list_excel_files(folder):
    files = [f for f in os.listdir(folder) if f.lower().endswith((".xls", ".xlsx"))]
    return files

# ==============================
# 2️⃣ LOAD AND CLEAN EXCEL
# ==============================
def load_excel(file_path):
    """Load Excel file into DataFrame"""
    df = pd.read_excel(file_path)
    # Optional: drop completely empty rows
    df = df.dropna(how="all")
    # Optional: drop completely empty columns
    df = df.dropna(axis=1, how="all")
    return df

# ==============================
# 3️⃣ SAVE AS CSV
# ==============================
def save_csv(df, csv_path):
    df.to_csv(csv_path, index=False)
    print(f"✅ Updated CSV: {csv_path}")

# ==============================
# 4️⃣ UPDATE ALL FILES
# ==============================
def update_docs():
    excel_files = list_excel_files(DOCS_FOLDER)
    if not excel_files:
        print("No Excel files found in docs/")
        return

    for excel_file in excel_files:
        excel_path = os.path.join(DOCS_FOLDER, excel_file)
        df = load_excel(excel_path)
        csv_name = os.path.splitext(excel_file)[0] + ".csv"
        csv_path = os.path.join(CSV_FOLDER, csv_name)
        save_csv(df, csv_path)

# ==============================
# 5️⃣ MAIN
# ==============================
def main():
    print("Updating CSV files from Excel docs...")
    update_docs()
    print("All CSVs are updated!")

if __name__ == "__main__":
    main()