from pathlib import Path
import serial

ROOT = Path(__file__).resolve().parents[1]

# Data
DATA_RAW = ROOT / "data" / "raw"
DATA_RAW_HIST = ROOT / "data" / "raw_hist" 
DATA_PUNTS = ROOT / "data" / "punts" # Legacy
DATA_SANKEY = ROOT / "data" / "sankey" # Legacy
DATA_PLANOL = ROOT /    "data" / "planol" 
DATA_TIMESERIES = ROOT / "data" / "timeseries"
DATA_NETWORK = ROOT / "data" / "network"


# Outputs
OUTPUT_PLOTS = ROOT / "outputs" / "plots"
OUTPUT_BOXPLOTS = ROOT / "outputs" / "boxplots"
OUTPUT_REPORT = ROOT / "outputs" / "report"
OUTPUT_SANKEY = ROOT / "outputs" / "sankey" # Legacy
OUTPUT_MAPA_AT = ROOT / "outputs" / "mapa-at" # Legacy
OUTPUT_MAPA_STE = ROOT / "outputs" / "mapa-ste" # Legacy
OUTPUT_NETWORK = ROOT / "outputs" / "network"
OUTPUT_SUMMARY = ROOT / "outputs" / "summary"

# Document names
sankey_ste = DATA_SANKEY / "sankey_nodes-ste.csv"
sankey_at = DATA_SANKEY / "sankey_nodes-at.csv"
punts_ste = DATA_PUNTS / "punts-mesura-ste.csv"
punts_at = DATA_PUNTS / "punts-mesura-at.csv"
planol_ste = DATA_PLANOL / "planol-ste.png"
planol_at = DATA_PLANOL / "planol-at.png"
edges_csv = DATA_NETWORK / "edges.csv"
nodes_csv = DATA_NETWORK / "nodes.csv"

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