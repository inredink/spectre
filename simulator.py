
"""SPECTRE / VEIL sensor simulator.

Simulated readings for development before the VEIL hardware is assembled.
"""

import math
import random
import time
from datetime import datetime, timezone

from sensors import make_reading


_start_time = time.monotonic()


def generate_readings():
    """Return one simulated reading for each sensor measurement."""
    t = time.monotonic() - _start_time
    noise = random.uniform

    # Environmental sensor
    temperature_c = 22.4 + 0.35 * math.sin(t / 18) + noise(-0.04, 0.04)
    humidity = 45.0 + 2.2 * math.sin(t / 23) + noise(-0.25, 0.25)
    pressure = 1012.6 + 1.8 * math.sin(t / 45) + noise(-0.08, 0.08)

    # TSL2591 channels. Counts are illustrative simulated raw values.
    # Infrared and full-spectrum are separate sensor-channel readings.
    infrared = max(0, int(680 + 65 * math.sin(t / 4.8)
                           + 22 * math.sin(t / 1.7) + noise(-12, 12)))
    visible = max(0, int(1800 + 180 * math.sin(t / 6.5)
                          + 55 * math.sin(t / 1.9) + noise(-25, 25)))
    full_spectrum = visible + infrared

    # Simulated lux estimate, not a calibrated conversion of the counts.
    light_lux = max(0.0, visible * 0.135 + noise(-1.0, 1.0))

    # LSM303AGR accelerometer: values in g
    acceleration_x = 0.018 * math.sin(t * 1.4) + noise(-0.008, 0.008)
    acceleration_y = 0.026 * math.sin(t * 0.9 + 1.2) + noise(-0.008, 0.008)
    acceleration_z = 1.0 + 0.018 * math.sin(t * 0.7) + noise(-0.008, 0.008)

    # Illustrative magnetic field magnitude in microtesla.
    magnetic_field = 36.8 + 1.8 * math.sin(t / 3.8) + noise(-0.35, 0.35)

    # Placeholder capacitive value for the future FDC1004.
    capacitance = 12.6 + 0.75 * math.sin(t / 2.6) + noise(-0.12, 0.12)

    timestamp = datetime.now(timezone.utc).isoformat()

    measurements = [
        ("temperature_c", temperature_c, "°C"),
        ("temperature_f", temperature_c * 9 / 5 + 32, "°F"),
        ("humidity", humidity, "%"),
        ("pressure", pressure, "hPa"),
        ("light", light_lux, "lux"),
        ("visible", visible, "counts"),
        ("infrared", infrared, "counts"),
        ("full_spectrum", full_spectrum, "counts"),
        ("acceleration_x", acceleration_x, "g"),
        ("acceleration_y", acceleration_y, "g"),
        ("acceleration_z", acceleration_z, "g"),
        ("magnetic_field", magnetic_field, "µT"),
        ("capacitance", capacitance, "pF"),
    ]

    readings = []
    for measurement, value, unit in measurements:
        reading = make_reading(
            sensor=(
                "TSL2591" if measurement in
                ("light", "visible", "infrared", "full_spectrum")
                else "BME280" if measurement in
                ("temperature_c", "temperature_f", "humidity", "pressure")
                else "LSM303AGR" if measurement.startswith("acceleration_")
                or measurement == "magnetic_field"
                else "FDC1004"
            ),
            measurement=measurement,
            value=value,
            unit=unit,
        )

        # Preserve compatibility with SensorReading implementations
        # that assign timestamps internally.
        readings.append(reading)

    return readings
