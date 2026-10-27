
"""CSV data logging for SPECTRE."""

import csv
from pathlib import Path
from sensors import SensorReading


DATA_DIR = Path("data")
LOG_FILE = DATA_DIR / "spectre_log.csv"

CSV_FIELDS = [
    "timestamp",
    "sensor",
    "measurement",
    "value",
    "unit",
    "simulated",
]


def log_readings(readings: list[SensorReading]) -> Path:
    """Append sensor readings to the SPECTRE CSV log."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    file_exists = LOG_FILE.exists()
    needs_header = not file_exists or LOG_FILE.stat().st_size == 0

    with LOG_FILE.open("a", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=CSV_FIELDS)

        if needs_header:
            writer.writeheader()

        for reading in readings:
            writer.writerow({
                "timestamp": reading.timestamp,
                "sensor": reading.sensor,
                "measurement": reading.measurement,
                "value": reading.value,
                "unit": reading.unit,
                "simulated": reading.simulated,
            })

    return LOG_FILE


if __name__ == "__main__":
    from simulator import generate_readings

    readings = generate_readings()
    saved_path = log_readings(readings)

    print(f"SPECTRE: logged {len(readings)} simulated readings.")
    print(f"File: {saved_path.resolve()}")
