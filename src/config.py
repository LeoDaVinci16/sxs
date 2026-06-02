from pathlib import Path
import serial

ROOT = Path(__file__).resolve().parents[1]

# --- Data Folders ---
DATA = ROOT / "data"
DATA_RAW = DATA
OTHER_RAW = DATA

at_network_data = DATA
at_punts_data = DATA
at_sankey_data = DATA
at_planol_data = DATA
DATA_TIMESERIES = DATA
DATA_NETWORK = DATA

ste_network_data = DATA
ste_punts_data = DATA
ste_sankey_data = DATA
ste_planol_data = DATA

# --- Specific Files ---
at_edges_csv = DATA / "at_edges.csv"
at_nodes_csv = DATA / "at_nodes.csv"
ste_edges_csv = DATA / "ste_edges.csv"
ste_nodes_csv = DATA / "ste_nodes.csv"

nodes_csv = at_nodes_csv
edges_csv = at_edges_csv

at_timeseries = DATA / "at_timeseries.csv"
ste_timeseries = DATA / "ste_timeseries.csv"
timeseries_normalized = DATA / "timeseries_normalized_1.csv"

planol_at = DATA / "planol-at.png"
punts_at = DATA / "punts-mesura-at.csv"
punts_at_xlsx = DATA / "punts-mesura-at.xlsx"

planol_ste = DATA / "planol-ste.png"
punts_ste = DATA / "punts-mesura-ste.csv"
punts_ste_xlsx = DATA / "punts-mesura-ste.xlsx"

sankey_at = at_edges_csv
sankey_ste = ste_edges_csv

# --- Output Folders ---
OUTPUTS = ROOT / "outputs"
OUTPUT_REPORT = ROOT / "outputs" / "informe"
OUTPUT_SUMMARY = ROOT / "outputs" / "summary"

OUTPUT_AT = OUTPUTS / "at"
at_sankey_output = OUTPUT_AT / "sankey"
at_network_output = OUTPUT_AT / "network"
at_mapa_output = OUTPUT_AT / "map"
OUTPUT_MAPA_AT = at_mapa_output
at_plots = OUTPUT_AT / "plots"
at_boxplots = OUTPUT_AT / "boxplots"

OUTPUT_STE = OUTPUTS / "ste"
ste_sankey_output = OUTPUT_STE / "sankey"
ste_network_output = OUTPUT_STE / "network"
ste_mapa_output = OUTPUT_STE / "map"
OUTPUT_MAPA_STE = ste_mapa_output
ste_plots = OUTPUT_STE / "plots"
ste_boxplots = OUTPUT_STE / "boxplots"

at_network_html = at_network_output / "network_at.html"
ste_network_html = ste_network_output / "network_ste.html"

# --- Serial Configuration ---
SERIAL_PORT = "COM3"
SERIAL_BAUD = 9600
SERIAL_BYTESIZE = serial.EIGHTBITS
SERIAL_PARITY = serial.PARITY_EVEN
SERIAL_STOPBITS = serial.STOPBITS_TWO
SERIAL_TIMEOUT = 10
SERIAL_CSV_SEP = "AUTO" 
DEFAULT_SEP = ";"