# main.py
import os
import pandas as pd
import matplotlib.pyplot as plt
from plot_helper import get_numeric_columns, create_plot, save_plot
from points_dict import points_dict
    
def load_csv(csv_path):
    df = pd.read_csv(csv_path, sep="\t")
    # ---- Robust date column detection ----
    date_col = next(
        (c for c in df.columns
         if any(p in c.lower() for p in ["date", "data", "fecha"])),
        None
    )
    if date_col is None:
        print(f"[WARNING] No date column found in {csv_path}")
        return None
    # Convert to datetime
    df[date_col] = pd.to_datetime(df[date_col], format="%m/%d/%Y %I:%M:%S %p", errors="coerce")
    # Drop invalid dates
    df = df.dropna(subset=[date_col])
    if df.empty:
        print(f"[WARNING] No valid dates in {csv_path}")
        return None
    df.set_index(date_col, inplace=True)
    return df

def batch_plot(folder_path, plot_folder, variables_to_plot):
    os.makedirs(plot_folder, exist_ok=True)
    csv_files = [f for f in os.listdir(folder_path) if f.lower().endswith(".csv")]
    print(f"Found {len(csv_files)} CSV files.")
    
    for csv_file in csv_files:
        csv_path = os.path.join(folder_path, csv_file)
        print(f"\n📂 Processing: {csv_file}")
        df = load_csv(csv_path)
        numeric_cols = get_numeric_columns(df)
        if not numeric_cols:
            print("⚠️ No numeric columns. Skipping.")
            continue
        for variable in numeric_cols:
            if variable not in variables_to_plot:
                continue
            df[variable] = pd.to_numeric(df[variable], errors="coerce").abs()
            df_clean = df.dropna(subset=[variable])
            fig, ax = create_plot(df_clean, variable, csv_path, points_dict)
            path = save_plot(fig, plot_folder, csv_path, variable)
            plt.close(fig)
            print(f"✅ Saved: {path}")
    print("\n🎉 Batch plotting finished!")

def preview_plot(folder_path, plot_folder):
    csv_files = [f for f in os.listdir(folder_path) if f.lower().endswith(".csv")]
    for i, f in enumerate(csv_files):
        print(f"{i}: {f}")
    file_number = int(input("\nEnter file number: "))
    csv_path = os.path.join(folder_path, csv_files[file_number])
    df = load_csv(csv_path)
    numeric_cols = get_numeric_columns(df)
    for i, col in enumerate(numeric_cols):
        print(f"{i}: {col}")
    var_number = int(input("\nEnter variable number: "))
    variable = numeric_cols[var_number]
    df[variable] = pd.to_numeric(df[variable], errors="coerce").abs()
    fig, ax = create_plot(df, variable, csv_path, points_dict)
    plt.show()
    save = input("Save plot? (y/n): ").lower()
    if save == "y":
        path = save_plot(fig, plot_folder, csv_path, variable)
        print(f"✅ Plot saved: {path}")

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    folder_path = os.path.abspath(os.path.join(script_dir, "..", "data", "raw"))
    plot_folder = os.path.abspath(os.path.join(script_dir, "..", "outputs", "plots"))
    os.makedirs(plot_folder, exist_ok=True)

    # folder_path = r"C:\Users\ArnauCoronado\Documents_local\supersonic-at\data\raw" original path on creator computer
    # plot_folder = r"C:\Users\ArnauCoronado\Documents_local\supersonic-at\data\plots"

    variables_to_plot = [
        #'A Volumetric flow rate [m³/h]',
        'A Flow velocity [m/s]',
        #'A Mass flow rate [kg/h]',
    ]
    print("1: Batch plot all CSVs")
    print("2: Preview and plot one CSV")
    choice = input("Choose an option: ")
    if choice == "1":
        batch_plot(folder_path, plot_folder, variables_to_plot)
    elif choice == "2":
        preview_plot(folder_path, plot_folder)
    else:
        print("Invalid choice.")

if __name__ == "__main__":
    main()