from pathlib import Path
import serial

ROOT = Path(__file__).resolve().parents[1]

# --- Data Folders ---
DATA = ROOT / "data"
DATA_RAW = DATA / "raw"
OTHER_RAW = DATA / "other_raw"

DATA_AT = DATA / "at"
at_raw = DATA_AT / "at_raw"
at_network_data = DATA_AT / "at_network"
at_timeseries = DATA_AT / "at_timeseries.csv"
at_punts_data = DATA_AT / "punts"
at_sankey_data = DATA_AT / "sankey"
at_planol_data = DATA_AT / "planol"

DATA_STE = DATA / "ste"
ste_raw = DATA_STE / "ste_raw"
ste_network_data = DATA_STE / "ste_network"
ste_timeseries = DATA_STE / "ste_timeseries.csv"
ste_punts_data = DATA_STE / "punts"
ste_sankey_data = DATA_STE / "sankey"
ste_planol_data = DATA_STE / "planol"

# --- Specific Files ---
at_edges_csv = at_network_data / "edges.csv"
at_nodes_csv = at_network_data / "nodes.csv"
ste_edges_csv = ste_network_data / "edges.csv"
ste_nodes_csv = ste_network_data / "nodes.csv"

# --- Output Folders ---
OUTPUTS = ROOT / "outputs"
OUTPUT_REPORT = ROOT / "outputs" / "informe"

OUTPUT_AT = OUTPUTS / "at"
at_sankey_output = OUTPUT_AT / "sankey"
at_network_output = OUTPUT_AT / "network"
at_mapa_output = OUTPUT_AT / "map"
at_plots = OUTPUT_AT / "plots"
at_boxplots = OUTPUT_AT / "boxplots"

OUTPUT_STE = OUTPUTS / "ste"
ste_sankey_output = OUTPUT_STE / "sankey"
ste_network_output = OUTPUT_STE / "network"
ste_mapa_output = OUTPUT_STE / "map"
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