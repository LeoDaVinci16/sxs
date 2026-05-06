import serial
import sys
from config import SERIAL_PORT, SERIAL_BAUD, SERIAL_PARITY, SERIAL_STOPBITS, SERIAL_BYTESIZE, SERIAL_TIMEOUT

try:
    ser = serial.Serial(
        port=SERIAL_PORT,
        baudrate=SERIAL_BAUD,
        bytesize=SERIAL_BYTESIZE,
        parity=SERIAL_PARITY,
        stopbits=SERIAL_STOPBITS,
        timeout=SERIAL_TIMEOUT
    )
except Exception as e:
    print(f"Error opening serial port {SERIAL_PORT}: {e}")
    sys.exit(1)

print(f"--- Listening on {SERIAL_PORT} ({SERIAL_BAUD}, {SERIAL_BYTESIZE}{SERIAL_PARITY}{SERIAL_STOPBITS}) ---")
print("--- Printing raw ASCII output. Press Ctrl+C to stop. ---\n")

data_received = False

try:
    while True:
        line = ser.readline()
        if line:
            data_received = True
            sys.stdout.write(line.decode(errors="replace"))
            sys.stdout.flush()
        else:
            # If we were receiving data and now we get a timeout (empty line)
            if data_received:
                print("\n--- Transmission finished (Timeout) ---")
                break

except KeyboardInterrupt:
    print("\n\n--- Stopped by user ---")
finally:
    ser.close()
