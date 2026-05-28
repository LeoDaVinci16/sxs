from pathlib import Path
import serial

ROOT = Path(__file__).resolve().parents[1]

# Data
DATA_RAW = ROOT / "data" / "raw"
OTHER_RAW = ROOT / "data" / "other_raw"
DATA_AT = ROOT / "data" / "at"
DATA_STE = ROOT / "data" / "ste"

# Data/at
at_raw = DATA_AT / "at_raw" 
at_network_data = DATA_AT / "at_network"
at_timeseries = DATA_AT / "at_timeseries.csv"

at_nodes_csv = at_network_data / "nodes.csv"
at_edges_csv = at_network_data / "edges.csv"
at_punts_data = DATA_AT / "punts"
at_sankey_data = DATA_AT / "sankey"
at_planol_data = DATA_AT / "planol"


# Data/ste
ste_raw = DATA_STE / "ste_raw"
ste_network_data = DATA_STE / "ste_network"
ste_timeseries = DATA_STE / "ste_timeseries.csv"

ste_nodes_csv = DATA_STE / "ste_network" / "nodes.csv"
ste_edges_csv = DATA_STE / "ste_network" / "edges.csv"
ste_punts_data = DATA_STE / "punts"
ste_sankey_data = DATA_STE / "sankey"
ste_planol_data = DATA_STE / "planol"


# Outputs
outputs_at = ROOT / "outputs" / "at"
outputs_ste = ROOT / "outputs" / "ste"

# Outputs/at
at_plots = ROOT / "outputs" / "at" / "at_plots"
at_boxplots = ROOT / "outputs" / "at" / "at_boxplots"
at_sankey_output = ROOT / "outputs" / "at" / "at_sankey"
at_mapa = ROOT / "outputs" / "at" / "at_mapa"
OUTPUT_MAPA_AT = at_mapa
at_network_output = ROOT / "outputs" / "at" / "at_network"

# Outputs/ste
ste_plots = ROOT / "outputs" / "ste" / "ste_plots"
ste_boxplots = ROOT / "outputs" / "ste" / "ste_boxplots"
ste_sankey_output = ROOT / "outputs" / "ste" / "ste_sankey"
ste_mapa = ROOT / "outputs" / "ste" / "ste_mapa"
OUTPUT_MAPA_STE = ste_mapa
ste_network_output = ROOT / "outputs" / "ste" / "ste_network"

# Document names
sankey_ste_html= ste_sankey_output / "sankey_ste.html"
sankey_at_html = at_sankey_output / "sankey_at.html"
ste_network_html = ste_network_output / "ste_network.html"
at_network_html = at_network_output / "at_network.html"

OUTPUT_REPORT = ROOT / "outputs" / "informe"

# Serial Configuration
SERIAL_PORT = "COM3"
SERIAL_BAUD = 9600
SERIAL_BYTESIZE = serial.EIGHTBITS
SERIAL_PARITY = serial.PARITY_EVEN
SERIAL_STOPBITS = serial.STOPBITS_TWO
SERIAL_TIMEOUT = 10  # Seconds to wait for data before deciding a block is finished
# CSV Export configuration: Use a specific char or "AUTO" to detect from stream
SERIAL_CSV_SEP = "AUTO" 
DEFAULT_SEP = ";" # Fallback if AUTO fails