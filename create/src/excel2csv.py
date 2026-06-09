# update_docs.py

from pathlib import Path
import os
import pandas as pd


# ==============================
# 1️⃣ LIST FILES
# ==============================
def list_excel_files(folder):
    files = [f for f in os.listdir(folder) if f.lower().endswith((".xls", ".xlsx")) and not f.startswith("~$")]
    return files

# ==============================
# 2️⃣ LOAD AND CLEAN EXCEL
# ==============================
def load_excel(file_path):
    try:
        df = pd.read_excel(file_path)
        df = df.dropna(how="all")           # Optional: drop completely empty rows
        df = df.dropna(axis=1, how="all")   # Optional: drop completely empty columns
        return df
    except Exception as e:
        print(f"⚠️ Error llegint {file_path}: {e}")
        return None 

# ==============================
# 3️⃣ SAVE AS CSV
# ==============================
def save_csv(df, csv_path):
    df.to_csv(csv_path, index=False)
    print(f"CSVs actualitzats: {csv_path}")

# ==============================
# 4️⃣ UPDATE ALL FILES
# ==============================
def update_docs(docs_folder):
    excel_files = list_excel_files(docs_folder)
    if not excel_files:
        print("No s'han trobat documents d'excel (xlsx)")  
        return
    
    for excel_file in excel_files:
        excel_path = os.path.join(docs_folder, excel_file)
        df = load_excel(excel_path)
        if df is None:
            continue
        csv_name = os.path.splitext(excel_file)[0] + ".csv"
        csv_path = os.path.join(docs_folder, csv_name)
        save_csv(df, csv_path)



# ==============================
# 5️⃣ MAIN default
# ==============================
def main(docs_folder_path):
    print(f"📂 Convertint arxius de la carpeta: {docs_folder_path}")
    update_docs(docs_folder_path)
    print("✅ Tots els CSV s'han actualitzat!\n")


if __name__ == "__main__":
    # Default behavior if run directly
    base_path = Path(__file__).resolve().parents[1] / "data"
    main(docs_folder_path=str(base_path))
