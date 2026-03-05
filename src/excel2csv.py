# excel2csv.py

from pathlib import Path
import pandas as pd
import os


def convert_excel_to_csv(excel_path, output_folder):
    """
    Convert a single Excel file to CSV.
    """
    df = pd.read_excel(excel_path)

    csv_filename = Path(excel_path).stem + ".csv"
    csv_path = os.path.join(output_folder, csv_filename)

    df.to_csv(csv_path, index=False)

    print(f"Converted {Path(excel_path).name} -> {csv_filename}")


def process_folder(folder_path):
    """
    Convert all Excel files in a folder to CSV.
    """
    for filename in os.listdir(folder_path):

        if filename.endswith(".xlsx") or filename.endswith(".xls"):

            excel_path = os.path.join(folder_path, filename)

            convert_excel_to_csv(excel_path, folder_path)


def main():
    root_folder = Path(__file__).parents[1]
    docs_folder = os.path.join(root_folder, "docs")
    process_folder(docs_folder)
    print("All Excel files converted to CSV!")


if __name__ == "__main__":
    main()