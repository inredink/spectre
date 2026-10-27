
"""SPECTRE — retro CRT environmental monitoring console."""

import math
import time
import tkinter as tk
from collections import deque
from datetime import datetime

from simulator import generate_readings

try:
    from logger import log_readings
except ImportError:
    log_readings = None


# ============================================================
# CLASSIC CRT PALETTE
# ============================================================

BG = "#030704"
PANEL = "#08110b"
PANEL_DARK = "#040a06"
PANEL_LIGHT = "#0b190f"

GREEN = "#73ff91"
GREEN_BRIGHT = "#a0ffae"
GREEN_MID = "#31864a"
GREEN_DIM = "#194629"
GRID = "#102b19"
TEXT = "#b4d6b8"
MUTED = "#64876a"

AMBER = "#ffbf56"
ORANGE = "#ff874d"
RED = "#ff4f52"
CYAN = "#75e5d1"
MAGENTA = "#f08bdd"

FONT = "Consolas"
FONT_SMALL = (FONT, 8)
FONT_NORMAL = (FONT, 10)
FONT_BOLD = (FONT, 10, "bold")
FONT_TITLE = (FONT, 13, "bold")
FONT_LARGE = (FONT, 19, "bold")

FRAME_COLOR = GREEN_DIM
UPDATE_MS = 50
SAMPLE_MS = 100
HISTORY_LENGTH = 80


def clamp(value, low, high):
    return max(low, min(high, value))


def get_value(values, key, default=0.0):
    try:
        return float(values.get(key, default))
    except (TypeError, ValueError):
        return float(default)


# ============================================================
# REUSABLE CRT PANEL
# ============================================================

class CRTPanel(tk.Frame):
    def __init__(self, parent, title, subtitle=None, **kwargs):
        super().__init__(
            parent,
            bg=PANEL,
            highlightthickness=1,
            highlightbackground=FRAME_COLOR,
            **kwargs,
        )

        header = tk.Frame(self, bg=PANEL_DARK)
        header.pack(fill="x")

        tk.Label(
            header,
            text=title.upper(),
            bg=PANEL_DARK,
            fg=GREEN,
            font=FONT_BOLD,
            anchor="w",
        ).pack(side="left", padx=9, pady=6)

        if subtitle:
            tk.Label(
                header,
                text=subtitle.upper(),
                bg=PANEL_DARK,
                fg=MUTED,
                font=FONT_SMALL,
                anchor="e",
            ).pack(side="right", padx=9)

        tk.Frame(self, bg=GREEN_DIM, height=1).pack(fill="x")

        self.body = tk.Frame(self, bg=PANEL)
        self.body.pack(fill="both", expand=True)


# ============================================================
# ANALOG GAUGE
# ============================================================

class Gauge(tk.Canvas):
    def __init__(
        self, parent, title, unit, color=GREEN,
        minimum=0, maximum=100, **kwargs
    ):
        super().__init__(
            parent,
            bg=PANEL,
            highlightthickness=0,
            height=150,
            **kwargs,
        )
        self.title = title
        self.unit = unit
        self.color = color
        self.minimum = minimum
        self.maximum = maximum
        self.value = minimum
        self.bind("<Configure>", self._draw)

    def set_value(self, value):
        self.value = value
        self._draw()

    def _draw(self, _event=None):
        self.delete("all")
        w = max(self.winfo_width(), 100)
        h = max(self.winfo_height(), 120)

        self.create_text(
            w / 2, 13, text=self.title,
            fill=TEXT, font=FONT_BOLD,
        )
        self.create_text(
            w / 2, 27, text=self.unit,
            fill=MUTED, font=FONT_SMALL,
        )

        cx = w / 2
        cy = h * 0.59
        radius = min(w * 0.37, h * 0.32)
        start = 225
        sweep = 270

        self.create_arc(
            cx - radius, cy - radius,
            cx + radius, cy + radius,
            start=start, extent=-sweep,
            style="arc", outline=GREEN_DIM, width=5,
        )

        for i in range(21):
            fraction = i / 20
            angle = math.radians(start - sweep * fraction)
            outer = radius - 2
            inner = radius - (12 if i % 5 == 0 else 6)

            x1 = cx + inner * math.cos(angle)
            y1 = cy - inner * math.sin(angle)
            x2 = cx + outer * math.cos(angle)
            y2 = cy - outer * math.sin(angle)

            self.create_line(
                x1, y1, x2, y2,
                fill=self.color if i % 5 == 0 else MUTED,
                width=2 if i % 5 == 0 else 1,
            )

        fraction = clamp(
            (self.value - self.minimum)
            / max(self.maximum - self.minimum, 0.0001),
            0, 1,
        )
        angle = math.radians(start - sweep * fraction)
        nx = cx + (radius - 17) * math.cos(angle)
        ny = cy - (radius - 17) * math.sin(angle)

        self.create_line(
            cx, cy, nx, ny,
            fill=self.color, width=2,
        )
        self.create_oval(
            cx - 3, cy - 3, cx + 3, cy + 3,
            fill=AMBER, outline=AMBER,
        )

        box_y = h - 29
        self.create_rectangle(
            w * 0.20, box_y - 9,
            w * 0.80, h - 3,
            fill=PANEL_DARK, outline=GREEN_DIM,
        )
        self.create_text(
            w / 2, box_y,
            text=f"{self.value:.1f}",
            fill=self.color, font=FONT_TITLE,
        )


# ============================================================
# OSCILLOSCOPE
# ============================================================

class Scope(tk.Frame):
    def __init__(
        self, parent, title, channels,
        height=200, **kwargs
    ):
        super().__init__(
            parent, bg=PANEL,
            highlightthickness=1,
            highlightbackground=FRAME_COLOR,
            **kwargs,
        )

        self.channels = channels
        self.history = {
            name: deque(maxlen=HISTORY_LENGTH)
            for name, _color in channels
        }
        self.latest = {name: 0.0 for name, _color in channels}
        self.canvas_height = height

        header = tk.Frame(self, bg=PANEL_DARK)
        header.pack(fill="x")

        tk.Label(
            header, text=title.upper(),
            bg=PANEL_DARK, fg=GREEN,
            font=FONT_BOLD, anchor="w",
        ).pack(side="left", padx=8, pady=5)

        legend = tk.Frame(self, bg=PANEL_DARK)
        legend.pack(side="right", padx=7)

        for name, color in channels:
            tk.Label(
                legend, text=f"━ {name}",
                bg=PANEL_DARK, fg=color,
                font=FONT_SMALL,
            ).pack(side="left", padx=4)

        tk.Frame(self, bg=GREEN_DIM, height=1).pack(fill="x")

        self.canvas = tk.Canvas(
            self, bg=PANEL_DARK,
            height=height, highlightthickness=0,
        )
        self.canvas.pack(fill="both", expand=True, padx=4, pady=4)
        self.canvas.bind("<Configure>", self._draw)

    def add_values(self, values):
        for name, _color in self.channels:
            value = values.get(name)
            if value is None:
                continue
            try:
                value = float(value)
            except (ValueError, TypeError):
                continue

            self.latest[name] = value
            self.history[name].append(value)

        self._draw()

    def _draw(self, _event=None):
        c = self.canvas
        c.delete("all")
        w = max(c.winfo_width(), 100)
        h = max(c.winfo_height(), 60)

        # CRT graticule
        for i in range(11):
            x = 2 + (w - 4) * i / 10
            c.create_line(x, 2, x, h - 2, fill=GRID)

        for i in range(5):
            y = 2 + (h - 4) * i / 4
            c.create_line(2, y, w - 2, y, fill=GRID)

        # Center reference line
        c.create_line(
            2, h / 2, w - 2, h / 2,
            fill=GREEN_DIM, dash=(2, 5),
        )

        for name, color in self.channels:
            values = list(self.history[name])
            if len(values) < 2:
                continue

            low = min(values)
            high = max(values)
            span = max(high - low, 0.0001)

            # Independent channel scaling keeps small changes visible.
            low -= span * 0.18
            high += span * 0.18
            span = max(high - low, 0.0001)

            points = []
            for i, value in enumerate(values):
                x = 3 + (w - 6) * i / (len(values) - 1)
                y = h - 4 - (value - low) / span * (h - 8)
                points.extend((x, y))

            if len(points) >= 4:
                c.create_line(
                    *points, fill=color,
                    width=1.5, smooth=True,
                    splinesteps=10,
                )

        # Live cursor at the right edge
        c.create_line(
            w - 4, 2, w - 4, h - 2,
            fill=GREEN_DIM, dash=(3, 4),
        )


# ============================================================
# MAIN APPLICATION
# ============================================================

class SpectreDesktop:
    def __init__(self, root):
        self.root = root
        self.root.title(
            "SPECTRE // VEIL Environmental Telemetry"
        )
        self.root.configure(bg=BG)
        self.root.geometry("1440x900")
        self.root.minsize(1050, 700)

        self.hold = False
        self.slow_sweep = False
        self.recording = False
        self.last_sample = 0.0
        self.last_log = 0.0

        self._build()
        self._tick()

    def _build(self):
        # ----------------------------------------------------
        # HEADER: equipment identity and system status
        # ----------------------------------------------------
        header = tk.Frame(
            self.root, bg=PANEL_DARK,
            highlightthickness=1,
            highlightbackground=GREEN_DIM,
        )
        header.pack(fill="x", padx=8, pady=(8, 4))

        tk.Label(
            header, text="SPECTRE",
            bg=PANEL_DARK, fg=GREEN_BRIGHT,
            font=(FONT, 25, "bold"),
        ).pack(side="left", padx=(14, 7), pady=8)

        tk.Label(
            header, text="// VEIL SENSOR SYSTEM",
            bg=PANEL_DARK, fg=TEXT,
            font=FONT_BOLD,
        ).pack(side="left", padx=7)

        tk.Label(
            header,
            text="ENVIRONMENTAL COLLECTION / TELEMETRY / RECONNAISSANCE",
            bg=PANEL_DARK, fg=MUTED,
            font=FONT_SMALL,
        ).pack(side="left", padx=15)

        self.clock = tk.Label(
            header, text="",
            bg=PANEL_DARK, fg=AMBER,
            font=FONT_BOLD,
        )
        self.clock.pack(side="right", padx=12)

        self.status_light = tk.Label(
            header, text="● SIM",
            bg=PANEL_DARK, fg=GREEN,
            font=FONT_BOLD,
        )
        self.status_light.pack(side="right", padx=12)

        # ----------------------------------------------------
        # MAIN BODY: left instrumentation, central scope,
        # right-side primary sensor displays.
        # ----------------------------------------------------
        body = tk.Frame(self.root, bg=BG)
        body.pack(fill="both", expand=True, padx=8, pady=4)

        body.columnconfigure(0, weight=2, minsize=220)
        body.columnconfigure(1, weight=5, minsize=400)
        body.columnconfigure(2, weight=3, minsize=280)
        body.rowconfigure(0, weight=1)

        # LEFT COLUMN: environmental gauges + compact motion
        left = tk.Frame(body, bg=BG)
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 4))
        left.rowconfigure(0, weight=1)
        left.rowconfigure(1, weight=1)
        left.rowconfigure(2, weight=1)
        left.columnconfigure(0, weight=1)

        env = CRTPanel(left, "ATMOSPHERIC CONDITIONS")
        env.grid(row=0, column=0, sticky="nsew", pady=(0, 4))
        env.body.columnconfigure(0, weight=1)
        env.body.columnconfigure(1, weight=1)

        self.gauges = {}
        gauge_specs = [
            ("TEMP", "°F", ORANGE, 0, 120),
            ("HUMIDITY", "% RH", GREEN, 0, 100),
            ("PRESSURE", "hPa", AMBER, 950, 1050),
            ("MAG FIELD", "µT", CYAN, 0, 100),
        ]

        for i, (name, unit, color, low, high) in enumerate(gauge_specs):
            gauge = Gauge(
                env.body, name, unit, color, low, high
            )
            gauge.grid(
                row=i // 2, column=i % 2,
                sticky="nsew", padx=2, pady=2,
            )
            self.gauges[name] = gauge

        # Smaller motion graph: important, but secondary.
        self.motion_scope = Scope(
            left, "INERTIAL / ACCELEROMETER",
            [("X", ORANGE), ("Y", CYAN), ("Z", GREEN)],
            height=90,
        )
        self.motion_scope.grid(
            row=1, column=0, sticky="nsew", pady=4
        )

        motion_info = CRTPanel(
            left, "MOTION STATUS", "LSM303AGR"
        )
        motion_info.grid(
            row=2, column=0, sticky="nsew", pady=(4, 0)
        )
        self.motion_value = tk.Label(
            motion_info.body,
            text="X  0.000 g\nY  0.000 g\nZ  1.000 g",
            bg=PANEL, fg=TEXT,
            font=FONT_NORMAL, justify="left",
        )
        self.motion_value.pack(
            anchor="w", padx=12, pady=8
        )

        # CENTER COLUMN: large signal display.
        center = tk.Frame(body, bg=BG)
        center.grid(row=0, column=1, sticky="nsew", padx=4)
        center.columnconfigure(0, weight=1)
        center.rowconfigure(0, weight=3)
        center.rowconfigure(1, weight=2)
        center.rowconfigure(2, weight=1)

        self.ir_scope = Scope(
            center,
            "OPTICAL TELEMETRY / TSL2591",
            [
                ("VISIBLE", GREEN),
                ("INFRARED", MAGENTA),
                ("FULL SPECTRUM", AMBER),
            ],
            height=270,
        )
        self.ir_scope.grid(
            row=0, column=0, sticky="nsew", pady=(0, 4)
        )

        self.cap_scope = Scope(
            center,
            "CAPACITIVE FIELD / FDC1004",
            [("CAPACITANCE", AMBER)],
            height=155,
        )
        self.cap_scope.grid(
            row=1, column=0, sticky="nsew", pady=4
        )

        self.mag_scope = Scope(
            center,
            "MAGNETIC FIELD / LSM303AGR",
            [("FIELD", CYAN)],
            height=90,
        )
        self.mag_scope.grid(
            row=2, column=0, sticky="nsew", pady=(4, 0)
        )

        # RIGHT COLUMN: primary optical instrument and live values.
        right = tk.Frame(body, bg=BG)
        right.grid(row=0, column=2, sticky="nsew", padx=(4, 0))
        right.columnconfigure(0, weight=1)
        right.rowconfigure(0, weight=1)
        right.rowconfigure(1, weight=1)
        right.rowconfigure(2, weight=1)

        optical = CRTPanel(
            right, "OPTICAL SENSOR", "TSL2591"
        )
        optical.grid(
            row=0, column=0, sticky="nsew", pady=(0, 4)
        )

        self.lux_gauge = Gauge(
            optical.body, "ILLUMINANCE", "lux",
            AMBER, 0, 1000,
        )
        self.lux_gauge.pack(
            fill="both", expand=True, padx=4, pady=4
        )

        channels = CRTPanel(
            right, "CHANNEL MONITOR", "LIVE"
        )
        channels.grid(
            row=1, column=0, sticky="nsew", pady=4
        )
        channels.body.columnconfigure(1, weight=1)

        self.channel_values = {}

        channel_specs = [
            ("VISIBLE", "visible", GREEN),
            ("NEAR-IR", "infrared", MAGENTA),
            ("FULL SPECTRUM", "full_spectrum", AMBER),
            ("CALCULATED LUX", "light", TEXT),
        ]

        for row, (label, key, color) in enumerate(channel_specs):
            tk.Label(
                channels.body, text=label,
                bg=PANEL, fg=MUTED,
                font=FONT_SMALL, anchor="w",
            ).grid(
                row=row, column=0, sticky="w",
                padx=8, pady=7,
            )

            value = tk.Label(
                channels.body, text="---",
                bg=PANEL_DARK, fg=color,
                font=FONT_BOLD, anchor="e",
                padx=8,
            )
            value.grid(
                row=row, column=1, sticky="ew",
                padx=7, pady=4,
            )
            self.channel_values[key] = value

        # Signal legend / interpretation panel
        signal = CRTPanel(
            right, "SIGNAL REFERENCE", "VEIL"
        )
        signal.grid(
            row=2, column=0, sticky="nsew", pady=(4, 0)
        )

        signal_lines = [
            ("GREEN", "Visible channel", GREEN),
            ("MAGENTA", "IR-sensitive channel", MAGENTA),
            ("AMBER", "Full-spectrum channel", AMBER),
            ("CYAN", "Magnetic field", CYAN),
        ]
        for label, description, color in signal_lines:
            line = tk.Frame(signal.body, bg=PANEL)
            line.pack(fill="x", padx=8, pady=5)

            tk.Label(
                line, text="■ " + label,
                bg=PANEL, fg=color, font=FONT_SMALL,
                width=12, anchor="w",
            ).pack(side="left")

            tk.Label(
                line, text=description,
                bg=PANEL, fg=TEXT, font=FONT_SMALL,
                anchor="w",
            ).pack(side="left")

        # ----------------------------------------------------
        # BOTTOM STRIP: controls only, no redundant count boxes
        # ----------------------------------------------------
        footer = tk.Frame(
            self.root, bg=PANEL_DARK,
            highlightthickness=1,
            highlightbackground=GREEN_DIM,
        )
        footer.pack(fill="x", padx=8, pady=(4, 8))

        self.hold_button = self._make_button(
            footer, "HOLD / OFF", self.toggle_hold, GREEN
        )
        self.hold_button.pack(side="left", padx=6, pady=6)

        self.sweep_button = self._make_button(
            footer, "SWEEP / NORMAL", self.toggle_sweep, AMBER
        )
        self.sweep_button.pack(side="left", padx=6, pady=6)

        self.record_button = self._make_button(
            footer, "RECORD / OFF", self.toggle_record, ORANGE
        )
        self.record_button.pack(side="left", padx=6, pady=6)

        self.footer_status = tk.Label(
            footer,
            text="SYSTEM READY  //  SIMULATED TELEMETRY",
            bg=PANEL_DARK, fg=GREEN,
            font=FONT_BOLD,
        )
        self.footer_status.pack(side="right", padx=12)

    def _make_button(self, parent, label, command, color):
        return tk.Button(
            parent,
            text=label,
            command=command,
            bg=PANEL,
            fg=color,
            activebackground=GREEN_DIM,
            activeforeground=GREEN_BRIGHT,
            relief="flat",
            highlightthickness=1,
            highlightbackground=FRAME_COLOR,
            font=FONT_BOLD,
            padx=12,
            pady=5,
            cursor="hand2",
        )

    def toggle_hold(self):
        self.hold = not self.hold
        self.hold_button.configure(
            text="HOLD / ON" if self.hold else "HOLD / OFF",
            fg=AMBER if self.hold else GREEN,
        )
        self.footer_status.configure(
            text=(
                "DISPLAY FROZEN  //  COLLECTION CONTINUES"
                if self.hold
                else "DISPLAY LIVE  //  SYSTEM READY"
            )
        )

    def toggle_sweep(self):
        self.slow_sweep = not self.slow_sweep
        self.sweep_button.configure(
            text=(
                "SWEEP / SLOW"
                if self.slow_sweep
                else "SWEEP / NORMAL"
            )
        )

    def toggle_record(self):
        self.recording = not self.recording
        self.record_button.configure(
            text=(
                "RECORD / ON"
                if self.recording
                else "RECORD / OFF"
            ),
            fg=RED if self.recording else ORANGE,
        )
        self.footer_status.configure(
            text=(
                "RECORDING ENABLED"
                if self.recording
                else "RECORDING DISABLED"
            )
        )

    @staticmethod
    def _map_readings(readings):
        values = {}
        for reading in readings:
            measurement = getattr(reading, "measurement", None)
            value = getattr(reading, "value", None)
            if measurement is not None and value is not None:
                values[measurement] = value
        return values

    def _update(self, values):
        temperature = values.get("temperature_f")
        if temperature is None and "temperature_c" in values:
            temperature = (
                get_value(values, "temperature_c") * 9 / 5 + 32
            )

        gauge_values = {
            "TEMP": temperature,
            "HUMIDITY": values.get("humidity"),
            "PRESSURE": values.get("pressure"),
            "MAG FIELD": values.get("magnetic_field"),
        }

        for name, value in gauge_values.items():
            if value is not None:
                self.gauges[name].set_value(float(value))

        light = values.get("light")
        if light is not None:
            self.lux_gauge.set_value(float(light))

        for key, label in self.channel_values.items():
            value = values.get(key)
            if value is None:
                continue

            if key == "light":
                label.configure(text=f"{float(value):.1f} lx")
            else:
                label.configure(text=f"{float(value):,.0f}")

        self.ir_scope.add_values({
            "VISIBLE": values.get("visible"),
            "INFRARED": values.get("infrared"),
            "FULL SPECTRUM": values.get("full_spectrum"),
        })

        self.cap_scope.add_values({
            "CAPACITANCE": values.get("capacitance"),
        })

        self.mag_scope.add_values({
            "FIELD": values.get("magnetic_field"),
        })

        self.motion_scope.add_values({
            "X": values.get("acceleration_x"),
            "Y": values.get("acceleration_y"),
            "Z": values.get("acceleration_z"),
        })

        self.motion_value.configure(
            text=(
                f"X  {get_value(values, 'acceleration_x'):+.3f} g\n"
                f"Y  {get_value(values, 'acceleration_y'):+.3f} g\n"
                f"Z  {get_value(values, 'acceleration_z', 1.0):+.3f} g"
            )
        )

    def _tick(self):
        self.clock.configure(
            text=datetime.now().strftime("%Y-%m-%d  %H:%M:%S")
        )

        try:
            readings = generate_readings()
            values = self._map_readings(readings)
            now = time.monotonic()

            # Keep collection active even while display is held.
            if self.recording and log_readings is not None:
                if now - self.last_log >= 1.0:
                    log_readings(readings)
                    self.last_log = now

            sample_interval = 0.25 if self.slow_sweep else SAMPLE_MS / 1000

            if not self.hold and now - self.last_sample >= sample_interval:
                self._update(values)
                self.last_sample = now

        except Exception as exc:
            self.footer_status.configure(
                text=f"SYSTEM ERROR  //  {exc}"
            )

        self.root.after(UPDATE_MS, self._tick)


def main():
    root = tk.Tk()
    SpectreDesktop(root)
    root.mainloop()


if __name__ == "__main__":
    main()
