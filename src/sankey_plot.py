# sankey_plot.py
import sys
from file_loader import load_excel
from create_sankey import create_sankey

if len(sys.argv) < 2:
    print("Usage: python sankey_plot.py <full_file_path>")
    sys.exit(1)

file_path = sys.argv[1]
magnitude_column = "cabal"
main_title = "Estudi dels cabals E-900/E-1000"

df, file_path = load_excel(file_path)
fig = create_sankey(df, magnitude_column, title=main_title, file_path=file_path)
fig.show()
