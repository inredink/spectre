
"""Configuration loading for SPECTRE."""

import json
from pathlib import Path


CONFIG_FILE = Path(__file__).parent / "config.json"

DEFAULT_CONFIG = {
    "application": {
        "name": "SPECTRE",
        "version": "0.1.0",
    },
    "display": {
        "temperature_unit": "C",
        "refresh_seconds": 2,
    },
    "logging": {
        "enabled": True,
        "directory": "data",
        "filename": "spectre_log.csv",
    },
    "hardware": {
        "mode": "simulation",
    },
}


def load_settings() -> dict:
    """Load settings from config.json, falling back to defaults."""
    if not CONFIG_FILE.exists():
        return DEFAULT_CONFIG.copy()

    try:
        with CONFIG_FILE.open("r", encoding="utf-8") as file:
            settings = json.load(file)
    except (json.JSONDecodeError, OSError) as exc:
        raise ValueError(
            f"Could not load {CONFIG_FILE.name}: {exc}"
        ) from exc

    if not isinstance(settings, dict):
        raise ValueError("Configuration must be a JSON object.")

    # Fill missing top-level sections and keys with defaults.
    merged = {
        section: {
            **defaults,
            **(settings.get(section, {}) if isinstance(settings.get(section, {}), dict) else {}),
        }
        for section, defaults in DEFAULT_CONFIG.items()
    }

    unit = merged["display"]["temperature_unit"]
    if unit not in ("C", "F"):
        raise ValueError("temperature_unit must be 'C' or 'F'.")

    refresh = merged["display"]["refresh_seconds"]
    if not isinstance(refresh, (int, float)) or isinstance(refresh, bool) or refresh <= 0:
        raise ValueError("refresh_seconds must be a positive number.")

    if merged["hardware"]["mode"] not in ("simulation", "live"):
        raise ValueError("hardware.mode must be 'simulation' or 'live'.")

    if not isinstance(merged["logging"]["enabled"], bool):
        raise ValueError("logging.enabled must be true or false.")

    return merged


if __name__ == "__main__":
    settings = load_settings()
    print(f"Application: {settings['application']['name']}")
    print(f"Temperature unit: °{settings['display']['temperature_unit']}")
    print(f"Refresh interval: {settings['display']['refresh_seconds']} seconds")
    print(f"Logging enabled: {settings['logging']['enabled']}")
    print(f"Hardware mode: {settings['hardware']['mode']}")
