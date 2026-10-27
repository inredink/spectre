
"""Sensor data structures for SPECTRE."""

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Optional


@dataclass
class SensorReading:
    """A single sensor measurement."""

    sensor: str
    measurement: str
    value: Optional[float]
    unit: str
    timestamp: str
    simulated: bool = True


def make_reading(
    sensor: str,
    measurement: str,
    value: Optional[float],
    unit: str,
    simulated: bool = True,
) -> SensorReading:
    """Create a timestamped sensor reading."""
    return SensorReading(
        sensor=sensor,
        measurement=measurement,
        value=value,
        unit=unit,
        timestamp=datetime.now(timezone.utc).isoformat(),
        simulated=simulated,
    )
