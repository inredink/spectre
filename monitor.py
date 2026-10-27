
"""Live simulated sensor monitor for SPECTRE."""

import os
import time
from datetime import datetime

from simulator import generate_readings
from settings import load_settings


def clear_screen() -> None:
    os.system("cls" if os.name == "nt" else "clear")


def display_readings(settings: dict) -> None:
    readings = generate_readings()
    display_unit = settings["display"]["temperature_unit"]

    clear_screen()
    print("=" * 72)
    print(" SPECTRE | VEIL ENVIRONMENTAL MONITOR")
    print("=" * 72)
    print(
        f"Mode: SIMULATION | "
        f"Updated: {datetime.now():%Y-%m-%d %H:%M:%S}"
    )
    print("-" * 72)
    print(f"{'SENSOR':12} {'MEASUREMENT':22} {'VALUE':>10} {'UNIT':6}")
    print("-" * 72)

    for reading in readings:
        # Show only the configured temperature unit.
        if reading.measurement in ("temperature_c", "temperature_f"):
            if display_unit == "C" and reading.measurement != "temperature_c":
                continue
            if display_unit == "F" and reading.measurement != "temperature_f":
                continue

            measurement = "temperature"
        else:
            measurement = reading.measurement

        print(
            f"{reading.sensor:12} "
            f"{measurement:22} "
            f"{reading.value:>10.2f} "
            f"{reading.unit:6}"
        )

    print("-" * 72)
    print(f"Temperature display: °{display_unit}")
    print("Simulated data only — no physical VEIL hardware is connected.")
    print(f"Refreshing every {settings['display']['refresh_seconds']:g} seconds.")
    print("Press Ctrl+C to stop.")


def main() -> None:
    settings = load_settings()
    refresh_seconds = settings["display"]["refresh_seconds"]

    print("Starting SPECTRE monitor. Press Ctrl+C to exit.")

    try:
        while True:
            display_readings(settings)
            time.sleep(refresh_seconds)
    except KeyboardInterrupt:
        print("\nSPECTRE monitor stopped.")


if __name__ == "__main__":
    main()
