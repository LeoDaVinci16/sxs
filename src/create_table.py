import os
import pandas as pd

def load_excel(file_path):
    """
    Load an Excel file from a full path.
    Returns dataframe + validated full path.
    """

    # --- 1️⃣ Check path exists ---
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

    # --- 2️⃣ Load dataframe ---
    df = pd.read_excel(file_path)

    # --- 3️⃣ Validate numeric columns ---
    numeric_cols = df.select_dtypes(include="number").columns.tolist()
    if not numeric_cols:
        raise RuntimeError(f"No numeric columns found in Excel: {file_path}")

    return df, file_path
