# The script i used to initialize the new id sistem

import os
import pandas as pd

# =========================
# CONFIG
# =========================
data_folder = "raw"        # <-- change if needed
mapping_file = "id_mapping.csv"
dry_run = False   # 🔥 CHANGE TO False TO EXECUTE
# =========================

# Load mapping
df = pd.read_csv(mapping_file)

# Sort longest IDs first (CRITICAL to avoid partial replacements)
df = df.sort_values(by="old", key=lambda x: x.str.len(), ascending=False)

mapping = dict(zip(df["old"], df["new"]))

print("\n==============================")
print("DRY RUN MODE" if dry_run else "EXECUTION MODE")
print("==============================\n")

changes_count = 0

for filename in os.listdir(data_folder):
    if not filename.endswith(".csv"):
        continue

    new_filename = filename

    for old_id, new_id in mapping.items():
        if old_id in new_filename:
            new_filename = new_filename.replace(old_id, str(new_id))
            break  # stop after first match

    if new_filename != filename:
        print(f"{filename}")
        print(f"   → {new_filename}\n")
        changes_count += 1

        if not dry_run:
            old_path = os.path.join(data_folder, filename)
            new_path = os.path.join(data_folder, new_filename)
            os.rename(old_path, new_path)

print(f"\nTotal files affected: {changes_count}")
print("Done.\n")