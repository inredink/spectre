
"""Simulated VEIL sensor readings for SPECTRE development."""

import random

from sensors import SensorReading, make_reading


def generate_readings() -> list[SensorReading]:
    """Generate simulated readings for all planned VEIL sensors."""

    readings = []

    # BME280: temperature, humidity, and atmospheric pressure
    temp_c = round(random.uniform(20.0, 28.0), 2)
    temp_f = round((temp_c * 9 / 5) + 32, 2)

    readings.extend([
        make_reading(
            "BME280",
            "temperature_c",
            temp_c,
            "°C",
        ),
        make_reading(
            "BME280",
            "temperature_f",
            temp_f,
            "°F",
        ),
        make_reading(
            "BME280",
            "humidity",
            round(random.uniform(35.0, 65.0), 2),
            "%",
        ),
        make_reading(
            "BME280",
            "pressure",
            round(random.uniform(990.0, 1030.0), 2),
            "hPa",
        ),
    ])

    # TSL2591: ambient light
    readings.append(
        make_reading(
            "TSL2591",
            "light",
            round(random.uniform(10.0, 1500.0), 2),
            "lux",
        )
    )

    # LSM303AGR: acceleration on three axes
    for axis in ("x", "y", "z"):
        readings.append(
            make_reading(
                "LSM303AGR",
                f"acceleration_{axis}",
                round(random.uniform(-1.0, 1.0), 3),
                "g",
            )
        )

    # LSM303AGR: magnetic field strength
    readings.append(
        make_reading(
            "LSM303AGR",
            "magnetic_field",
            round(random.uniform(20.0, 70.0), 2),
            "µT",
        )
    )

    # FDC1004: illustrative capacitive sensing value.
    # This is a placeholder simulation until the sensor is installed.
    readings.append(
        make_reading(
            "FDC1004",
            "capacitance",
            round(random.uniform(1.0, 50.0), 2),
            "pF",
        )
    )

    return readings


if __name__ == "__main__":
    print("=" * 76)
    print(" SPECTRE | VEIL SIMULATED SENSOR DATA")
    print("=" * 76)

    for reading in generate_readings():
        print(
            f"{reading.sensor:10} | "
            f"{reading.measurement:18} | "
            f"{reading.value:8.2f} {reading.unit:4} | "
            f"{'SIMULATED' if reading.simulated else 'LIVE'}"
        )

    print("=" * 76)
    print("These are simulated values, not actual sensor measurements.")
