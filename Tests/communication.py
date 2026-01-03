import serial

# UART auf dem Pi Zero
ser = serial.Serial(
    port='/dev/serial0',
    baudrate=115200,
    timeout=1
)

print("Warte auf Daten vom ESP32...")

while True:
    line = ser.readline().decode('utf-8').strip()
    if not line:
        continue

    try:
        b1, b2 = map(int, line.split())
        print(f"Sensor1: {b1}, Sensor2: {b2}")

    except ValueError:
        pass  # ungültige Zeile ignorieren