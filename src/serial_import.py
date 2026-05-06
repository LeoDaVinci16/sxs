import serial
import csv
import re
import time
import sys
from config import DATA_RAW, SERIAL_PORT, SERIAL_BAUD, SERIAL_PARITY, SERIAL_STOPBITS, SERIAL_BYTESIZE, SERIAL_TIMEOUT, SERIAL_CSV_SEP, DEFAULT_SEP
from serial_update import post_process_file

ser = serial.Serial(
    port=SERIAL_PORT,
    baudrate=SERIAL_BAUD,
    bytesize=SERIAL_BYTESIZE,
    parity=SERIAL_PARITY,
    stopbits=SERIAL_STOPBITS,
    timeout=SERIAL_TIMEOUT
)

metadata_lines = []
collecting_metadata = True
fname = None

def safe(s):
    return re.sub(r"[^A-Za-z0-9_.-]", "_", s)

def extract_filename(meta):
    meas_point = "NA"
    diameter = "NA"
    date = "NA"
    time = "NA"

    for l in meta:
        if "Meas. Point No." in l:
            meas_point = l.split(":")[-1].strip()
        if "Outer Diameter" in l:
            diameter = l.split(":")[-1].strip().replace(" ", "")
        if "DATE" in l:
            date = l.split(":")[-1].strip().replace(".", "-")
        if "TIME" in l:
            time = l.split(":")[-1].strip().replace(":", "-")

    filename = safe(f"{meas_point}_{diameter}_{date}_{time}.csv")
    return DATA_RAW / filename

def detect_line_sep(line):
    """Detects if a line uses tabs or semicolons."""
    if SERIAL_CSV_SEP != "AUTO":
        return SERIAL_CSV_SEP
    
    # Sniff the line
    if "\t" in line:
        return "\t"
    if ";" in line:
        return ";"
    return DEFAULT_SEP


print(f"Listening on {SERIAL_PORT}...")
import_active = False
data_received_in_session = False

while True:
    try:
        line = ser.readline().decode(errors="ignore").strip()
    except (serial.SerialException, OSError) as e:
        print(f"\nConnection lost: {e}")
        print("Attempting to reconnect in 5 seconds...")
        ser.close()
        time.sleep(5)
        try:
            ser.open()
            print("Reconnected!")
        except Exception:
            pass
        continue
    
    # If we were importing and suddenly stop receiving lines (timeout), 
    # it means the transmission finished.
    if not line:
        if import_active and data_received_in_session:
            print("\nTransmission finished. Running post-processing...")
            post_process_file(fname)
            print("Done. Exiting program.")
            ser.close()
            sys.exit(0) # Automatic exit
        continue

    # Reset state if a new device header is detected (start of a new transfer)
    if line.startswith("\\DEVICE"):
        if not DATA_RAW.exists():
            DATA_RAW.mkdir(parents=True, exist_ok=True)
        import_active = True
        collecting_metadata = True
        metadata_lines = []
        fname = None

    # ---------------------------
    # NEW DATA BLOCK START
    # ---------------------------
    if "\\DATA" in line:

        fname = extract_filename(metadata_lines)

        with open(fname, "w", newline="") as f:
            w = csv.writer(f)

            # write full metadata
            for m in metadata_lines:
                w.writerow([f"# {m}"])

            w.writerow([])

        print(f"Started logging to: {fname}")
        collecting_metadata = False
        continue

    # ---------------------------
    # METADATA PHASE
    # ---------------------------
    if collecting_metadata:
        metadata_lines.append(line)
        continue

    # ---------------------------
    # DATA PHASE (NO ASSUMPTIONS)
    # ---------------------------
    if fname and re.match(r"^[A-Z]:", line):
        # Robustly split Channel Prefix from Content (handles B:;??? and similar)
        match = re.match(r"^([A-Z]):\s*[;]?\s*(.*)", line)
        if not match:
            continue

        channel = match.group(1)
        content = match.group(2)
        if not content:
            continue

        sep = detect_line_sep(content)
        parts = [p.strip() for p in content.split(sep)] # Preserve empty fields

        if "*MEASURE" in content or "*CHANNEL" in content:
            header_parts = [p.replace("\\*", "").replace("*", "").strip() for p in parts]
            columns = ["CHANNEL"] + header_parts
            with open(fname, "a", newline="") as f:
                csv.writer(f, delimiter=sep).writerow(columns)
        else:
            data_received_in_session = True
            cleaned = [channel]
            for p in parts:
                p = p.replace(",", ".")
                try:
                    cleaned.append(float(p))
                except ValueError:
                    cleaned.append(p)

            with open(fname, "a", newline="") as f:
                csv.writer(f, delimiter=sep).writerow(cleaned)
            print(cleaned)