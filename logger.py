
"""CSV data logging for SPECTRE."""

import csv
from pathlib import Path

from sensors import SensorReading
from settings import load_settings


CSV_FIELDS = [
    "timestamp",
    "sensor",
    "measurement",
    "value",
    "unit",
    "simulated",
]


def log_readings(readings: list[SensorReading]) -> Path | None:
    """Append sensor readings to the configured CSV log."""
    settings = load_settings()
    logging_settings = settings["logging"]

    if not logging_settings["enabled"]:
        return None

    data_dir = Path(__file__).parent / logging_settings["directory"]
    log_file = data_dir / logging_settings["filename"]

    data_dir.mkdir(parents=True, exist_ok=True)

    needs_header = not log_file.exists() or log_file.stat().st_size == 0

    with log_file.open("a", newline="", encoding="utf-8") as file:
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

    return log_file


if __name__ == "__main__":
    from simulator import generate_readings

    readings = generate_readings()
    saved_path = log_readings(readings)

    if saved_path is None:
        print("SPECTRE: logging is disabled in config.json.")
    else:
        print(f"SPECTRE: logged {len(readings)} simulated readings.")
        print(f"File: {saved_path.resolve()}")
