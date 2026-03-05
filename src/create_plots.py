# main.py
import os
import pandas as pd
import matplotlib.pyplot as plt
from points_dict import points_dict
import re
import matplotlib.ticker as ticker

def get_numeric_columns(df):
    """Return list of numeric columns in a dataframe."""
    return df.select_dtypes(include='number').columns.tolist()

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

def create_plot(df, variable, csv_path, points_dict=None, show_date=True):

    filename = os.path.basename(csv_path)
    name_no_ext = filename.rsplit(".csv", 1)[0]
    parts = name_no_ext.split("_")
    point_id = "_".join(parts[2:])  # everything after second underscore

    if points_dict and point_id in points_dict:
        point_name = points_dict[point_id]
    else:
        point_name = point_id  # fallback to raw ID

    fig, ax = plt.subplots(figsize=(12, 6))
    ax.plot(df.index, df[variable], linewidth=1)

    # Main title
    ax.set_title(f"{variable}", fontsize=16, pad=20)

    # Subtitle: Punt de mesura
    fig.suptitle(f"Punt de mesura: {point_name}", fontsize=12, y=0.92)

    # Axes labels and formatting
    ax.set_xlabel("Time", fontsize=12)
    ax.set_ylabel(variable, fontsize=12)
    ax.grid(True, linestyle="--", linewidth=0.5)
    ax.yaxis.set_major_locator(ticker.MaxNLocator(8))

    # Format x-axis
    ax.xaxis.set_major_formatter(plt.matplotlib.dates.DateFormatter('%H:%M'))
    fig.autofmt_xdate()
    fig.tight_layout(rect=[0, 0.05, 1, 0.95])

    # Show date of last point below x-axis
    if show_date and not df.empty:
        last_day_str = df.index[-1].strftime("%d %b %Y")
        fig.text(0.99, 0.01, last_day_str, ha="right", va="bottom", fontsize=10, color="gray")

    return fig, ax

def save_plot(fig, plot_folder, csv_file, variable):
    os.makedirs(plot_folder, exist_ok=True)
    csv_name_only = os.path.splitext(os.path.basename(csv_file))[0]
    variable_clean = re.sub(r"[^\w\-_\. ]", "", variable).replace(" ", "_")
    plot_name = f"{csv_name_only}_{variable_clean}.png"
    plot_path = os.path.join(plot_folder, plot_name)
    fig.savefig(plot_path, dpi=300)
    plt.close(fig)  # Free memory
    return plot_path

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