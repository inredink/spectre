
"""SPECTRE — Sensor Platform for Environmental Collection,
Telemetry, Reconnaissance, & Evaluation.
"""

from datetime import datetime, timezone


APP_NAME = "SPECTRE"
APP_VERSION = "0.1.0"


def get_status() -> dict:
    """Return basic application status without accessing hardware."""
    return {
        "application": APP_NAME,
        "version": APP_VERSION,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "hardware_connected": False,
        "mode": "simulation",
    }


def main() -> None:
    status = get_status()

    print("=" * 48)
    print(f" {status['application']} v{status['version']}")
    print(" Sensor Platform Status")
    print("=" * 48)
    print(f"Timestamp: {status['timestamp']}")
    print(f"Mode:      {status['mode']}")
    print(f"VEIL:      {'Connected' if status['hardware_connected'] else 'Not connected'}")
    print("\nSPECTRE core initialized successfully.")


if __name__ == "__main__":
    main()
