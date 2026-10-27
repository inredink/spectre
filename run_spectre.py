
"""High-speed simulated data collection for SPECTRE."""

import time
from datetime import datetime

from logger import log_readings
from settings import load_settings
from simulator import generate_readings


def main() -> None:
    settings = load_settings()
    logging_enabled = settings["logging"]["enabled"]

    total_readings = 0
    total_cycles = 0
    last_report = time.monotonic()
    started = last_report

    print("=" * 52)
    print(" SPECTRE | HIGH-SPEED DATA COLLECTION")
    print("=" * 52)
    print(f"Mode: {settings['hardware']['mode'].upper()}")
    print(f"Logging: {'Enabled' if logging_enabled else 'Disabled'}")
    print("Press Ctrl+C to stop.")
    print()

    try:
        while True:
            readings = generate_readings()
            total_cycles += 1
            total_readings += len(readings)

            if logging_enabled:
                log_readings(readings)

            now = time.monotonic()

            if now - last_report >= 1.0:
                elapsed = now - started
                rate = total_readings / elapsed if elapsed else 0

                print(
                    f"\rElapsed: {elapsed:7.1f}s | "
                    f"Cycles: {total_cycles:8,d} | "
                    f"Readings: {total_readings:10,d} | "
                    f"Rate: {rate:,.0f} readings/s",
                    end="",
                    flush=True,
                )
                last_report = now

    except KeyboardInterrupt:
        elapsed = time.monotonic() - started
        print("\n\nSPECTRE collection stopped.")
        print(f"Duration: {elapsed:.2f} seconds")
        print(f"Cycles: {total_cycles:,}")
        print(f"Readings generated: {total_readings:,}")

        if elapsed > 0:
            print(f"Average generation rate: {total_readings / elapsed:,.0f} readings/s")

        if logging_enabled:
            print("Logging was enabled; readings were appended to the CSV file.")
        else:
            print("Logging was disabled; readings were not saved.")


if __name__ == "__main__":
    main()