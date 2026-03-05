# file_loader.py
import os
import pandas as pd

def load_excel(file_path):
    """Load an Excel file from full path, validate numeric columns."""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

    df = pd.read_excel(file_path)

    numeric_cols = df.select_dtypes(include="number").columns.tolist()
    if not numeric_cols:
        raise RuntimeError(f"No numeric columns found in Excel: {file_path}")

    return df, file_path