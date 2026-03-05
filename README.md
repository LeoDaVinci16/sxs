# 📊 CSV Plotting Tool

This Python project allows you to generate plots from CSV files. It supports both **batch plotting** of all CSVs in a folder and **previewing individual files** before saving plots.

The plotting logic is centralized in `plot_helper.py`, and a points dictionary is provided in `points_dict.py` for user-friendly plot titles.

---

## Folder Structure

```
supersonic-at/
│
├─ data/          	    	# Carpeta amb les dades del flexim
    ├─ raw/          		# Carpeta amb els arxius CSV
    ├─ plots/          		# Carpeta on es guarden les gràfiques quan s'executa el programa
    └─ configurations.zip       # Carpeta ZIP que conté els arxius originals de flexim
├─ src/     			# Programes de python
    ├─ main.py         		# Programa principal
    ├─ plot_helper.py           # Funcions per fer els gràfics
    └─ points_dict.py           # Diccionari per guardar els noms dels punts de mesura
├─ outputs     			# Carpeta en construcció
├─ .gitignore          		# Documents que no es guarden amb git.
└─ README.md           		# El document que esteu llegint
```

---

## Requirements

- Python 3.8+
- Libraries: `pandas`, `matplotlib`

Install dependencies with:

```
pip install pandas matplotlib
```

---

## Usage

Run the main program:

```
python main.py
```

You will be prompted to choose an option:

```
1: Batch plot all CSVs
2: Preview and plot one CSV
```

### 1️⃣ Batch Plot

- Generates plots for all CSV files in the folder.
- Only numeric columns specified in `variables_to_plot` will be plotted.
- Plots are automatically saved in the `plots` folder.

### 2️⃣ Preview Plot

- Choose a CSV file by index.
- Select a numeric variable to plot.
- View the plot interactively.
- Optionally save the plot.

---

## Configuration

You can customize the following in `main.py`:

```
folder_path = r"path\to\csv\folder"
plot_folder = r"path\to\save\plots"
variables_to_plot = [
    'A Volumetric flow rate [m³/h]',
    'A Flow velocity [m/s]',
    'A Mass flow rate [kg/h]',
]
```

- **folder_path**: Location of CSV files.  
- **plot_folder**: Where plots will be saved.  
- **variables_to_plot**: Numeric columns to include in batch plots.

---

## Points Dictionary

- Friendly names for codes are stored in `points_dict.py`.
- Used to generate descriptive titles for plots.
- Example entry:

```
points_dict = {
    "PM-V-1": "E800",
    "PM-V-2": "Secadores",
    "PM-V-3": "PEC",
    # ...
}
```

You can update or extend the dictionary to include your own codes.

---

## CSV Requirements

- CSV files must have a header row with column names.
- A `Date` column is recommended for time-based plots.
- Delimiter should be a tab (`\t`).
- Numeric columns will be automatically converted and cleaned.

---

## Output

- PNG plots saved in the `plots` folder.
- Filename format: `{csv_filename}_{variable_name}.png`.
- Last date of the data is displayed in the plot footer.

---

## Example

```
Found 3 CSV files:
0: PM-V-7_P400.csv
1: PM-V-8_Atomitzador.csv
2: PM-V-10_S600.csv

Enter file number: 0
Available numeric columns:
0: A Volumetric flow rate [m³/h]
1: A Flow velocity [m/s]
2: A Mass flow rate [kg/h]
Enter variable number: 0
✅ Selected variable: A Volumetric flow rate [m³/h]
```

---

## License

This project is open-source and free to use.# sxs-impulsio
