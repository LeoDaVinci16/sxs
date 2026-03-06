# files opener

from pathlib import Path
import pandas as pd
import sys

DATA_FOLDER = Path(__file__).parents[1] / "data"


def get_input_path(default_name):
    """
    Returns the path provided by the user or the default inside /data
    """

    if len(sys.argv) > 1:
        return Path(sys.argv[1])

    return DATA_FOLDER / default_name


def load_file(default_file):
    """
    Load CSV or Excel file
    """

    path = get_input_path(default_file)

    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")

    print(f"Loading file: {path}")

    if path.suffix == ".csv":
        return pd.read_csv(path)

    elif path.suffix in [".xlsx", ".xls"]:
        return pd.read_excel(path)

    else:
        raise ValueError("File must be CSV or Excel")


def load_folder(default_folder):
    """
    Load all CSV/XLSX files inside a folder
    """

    folder = get_input_path(default_folder)

    if not folder.exists():
        raise FileNotFoundError(f"Folder not found: {folder}")

    print(f"Loading folder: {folder}")

    dfs = []

    for file in folder.iterdir():

        if file.suffix == ".csv":
            dfs.append((file.name, pd.read_csv(file)))

        elif file.suffix in [".xlsx", ".xls"]:
            dfs.append((file.name, pd.read_excel(file)))

    if not dfs:
        raise ValueError("No CSV/XLSX files found")

    return dfs