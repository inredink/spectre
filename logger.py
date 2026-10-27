
"""Buffered CSV data logging for SPECTRE."""

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


class SensorLogger:
    """Keep a CSV file open while collecting sensor readings."""

    def __init__(self) -> None:
        settings = load_settings()
        logging_settings = settings["logging"]

        self.enabled = logging_settings["enabled"]
        self.log_file = None
        self.writer = None
        self.path = None

        if not self.enabled:
            return

        self.path = (
            Path(__file__).parent
            / logging_settings["directory"]
            / logging_settings["filename"]
        )

        self.path.parent.mkdir(parents=True, exist_ok=True)

        needs_header = (
            not self.path.exists()
            or self.path.stat().st_size == 0
        )

        self.log_file = self.path.open(
            "a",
            newline="",
            encoding="utf-8",
            buffering=1024 * 1024,
        )

        self.writer = csv.DictWriter(
            self.log_file,
            fieldnames=CSV_FIELDS,
        )

        if needs_header:
            self.writer.writeheader()
            self.log_file.flush()

    def log_readings(
        self,
        readings: list[SensorReading],
    ) -> None:
        """Append a batch of readings without reopening the file."""
        if not self.enabled or self.writer is None:
            return

        self.writer.writerows(
            {
                "timestamp": reading.timestamp,
                "sensor": reading.sensor,
                "measurement": reading.measurement,
                "value": reading.value,
                "unit": reading.unit,
                "simulated": reading.simulated,
            }
            for reading in readings
        )

    def flush(self) -> None:
        """Write buffered data to the operating system."""
        if self.log_file is not None:
            self.log_file.flush()

    def close(self) -> None:
        """Flush and close the CSV file."""
        if self.log_file is not None:
            self.log_file.flush()
            self.log_file.close()
            self.log_file = None
            self.writer = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()


def log_readings(
    readings: list[SensorReading],
) -> Path | None:
    """Compatibility helper for logging a single batch."""
    with SensorLogger() as logger:
        logger.log_readings(readings)
        return logger.path


if __name__ == "__main__":
    from simulator import generate_readings

    readings = generate_readings()

    with SensorLogger() as logger:
        logger.log_readings(readings)
        logger.flush()

        if logger.enabled:
            print(f"SPECTRE: logged {len(readings)} simulated readings.")
            print(f"File: {logger.path.resolve()}")
        else:
            print("SPECTRE: logging is disabled in config.json.")
