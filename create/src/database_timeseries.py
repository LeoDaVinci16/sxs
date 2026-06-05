import os
from glob import glob
import pandas as pd


base_dir = r"c:\Users\ArnauCoronado\Documents_local\euromed\sxs\database"
edges_path = os.path.join(base_dir, "at_edges.csv")
database_path = os.path.join(base_dir, "raw")
output_path = os.path.join(base_dir, "records.csv")
records = []

all_csv_files = glob(os.path.join(database_path, "**", "*.csv"), recursive=True)


for file_path in all_csv_files:

    filename = os.path.basename(file_path)

    try:
        date, hour, point_id = os.path.splitext(filename)[0].split("_")
    except ValueError:
        continue

    df_csv = pd.read_csv(file_path)

    values = (
        df_csv
        .select_dtypes(include="number")
        .stack()
        .dropna()
    )

    if len(values) == 0:
        continue

    mode_values = values.mode()

    records.append({
        "timestamp": f"{date}_{hour}",
        "date": date,
        "hour": hour,
        "point_id": point_id,
        "count": values.count(),
        "min": values.min(),
        "max": values.max(),
        "mean": values.mean(),
        "median": values.median(),
        "mode": mode_values.iloc[0] if not mode_values.empty else None
    })

df_summary = pd.DataFrame(records)
df_summary.to_csv(output_path, index=False)
