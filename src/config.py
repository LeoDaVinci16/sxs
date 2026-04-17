from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# Data
DATA_RAW = ROOT / "data" / "raw"
DATA_PUNTS = ROOT / "data" / "punts"
DATA_SANKEY = ROOT / "data" / "sankey"
DATA_PLANOL = ROOT /    "data" / "planol"

# Outputs
OUTPUT_PLOTS = ROOT / "outputs" / "plots"
OUTPUT_REPORT = ROOT / "outputs" / "report"
OUTPUT_SANKEY = ROOT / "outputs" / "sankey"
OUTPUT_MAPA_AT = ROOT / "outputs" / "mapa-at"
OUTPUT_MAPA_STE = ROOT / "outputs" / "mapa-ste"

# Document names
sankey_ste = DATA_SANKEY / "sankey_nodes-ste.csv"
sankey_at = DATA_SANKEY / "sankey_nodes-at.csv"
punts_ste = DATA_PUNTS / "punts-mesura-ste.csv"
punts_at = DATA_PUNTS / "punts-mesura-at.csv"
planol_ste = DATA_PLANOL / "planol-ste.png"
planol_at = DATA_PLANOL / "planol-at.png"
