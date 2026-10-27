# SPECTRE

**Sensor Platform for Environmental Collection, Telemetry, Reconnaissance, & Evaluation**

SPECTRE is a cross-platform desktop application for monitoring, recording, and evaluating environmental sensor data collected by VEIL.

## VEIL

**Variable Environmental Intercept Logger**

VEIL is a USB-connected sensor pod designed to collect environmental measurements and provide them to a host computer.

### Planned sensors

- **BME280** — temperature, relative humidity, and barometric pressure
- **TSL2591** — ambient light intensity
- **LSM303AGR** — acceleration and magnetic field measurements
- **FDC1004** — capacitive sensing

### Software goals

- Cross-platform support for Windows and Linux
- Live sensor readings and connection status
- Timestamped CSV data logging
- Sensor diagnostics and error reporting
- Environmental trend analysis and anomaly detection

## Technology

- Python 3
- PySide6 / Qt for the desktop interface
- Adafruit Blinka and compatible sensor libraries for hardware access
- Git and GitHub for version control
