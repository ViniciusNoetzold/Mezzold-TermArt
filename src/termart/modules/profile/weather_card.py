"""
Mezzold TermArt - Retro Terminal Weather Forecast Card Module
Renders an authentic, zero-token, rate-limit-free ASCII weather forecast card
with high-fidelity Unicode weather art, temperature trends, moon phases, and atmospheric telemetry.
Inspired by chubin/wttr.in.
"""
import os
import html
from typing import Dict, Any
from ...core.plugin import BasePlugin
from ...core.registry import registry

WEATHER_PRESETS = {
    "sunny": {
        "condition": "Sunny / Clear Sky", "temp_c": 24, "icon_color": "#ffd700",
        "icon": [
            "    \\   |   /    ",
            "  -  .·´¯`·.  -  ",
            " --(   ☀️   )-- ",
            "  -  `·.¸.·´  -  ",
            "    /   |   \\    "
        ],
        "sub_icon": "☀️",
        "telemetry": [
            ("Wind", "↗ 14 km/h (Gentle Breeze)", "#38bdf8"),
            ("Humidity", "54%", "#34d399"),
            ("Pressure", "1018 hPa", "#fbbf24"),
            ("UV Index", "7.2 (High)", "#f59e0b"),
            ("Moon Phase", "🌔 Waxing Gibbous", "#f472b6")
        ],
        "forecast": [
            ("TODAY", 24, "☀️ Sunny"),
            ("TOMORROW", 26, "🌤️ Warm & Clear"),
            ("NEXT DAY", 23, "⛅ Few Clouds")
        ]
    },
    "rainy": {
        "condition": "Cyberpunk Neon Rain", "temp_c": 17, "icon_color": "#00e5ff",
        "icon": [
            "      .---.      ",
            "    .-(     )·.  ",
            "   (___.__.__.__)",
            "     /   /   /   ",
            "    /   /   /    "
        ],
        "sub_icon": "🌧️",
        "telemetry": [
            ("Wind", "↘ 22 km/h (Breezy)", "#38bdf8"),
            ("Humidity", "88%", "#34d399"),
            ("Pressure", "1008 hPa", "#fbbf24"),
            ("Precipitation", "6.4 mm", "#00e5ff"),
            ("Moon Phase", "🌧️ Cloud Cover", "#94a3b8")
        ],
        "forecast": [
            ("TODAY", 17, "🌧️ Showers"),
            ("TOMORROW", 16, "🌦️ Light Rain"),
            ("NEXT DAY", 19, "⛅ Overcast")
        ]
    },
    "thunder": {
        "condition": "Severe Thunderstorm", "temp_c": 19, "icon_color": "#ff007f",
        "icon": [
            "      .---.      ",
            "    .-(  ⚡ )·.  ",
            "   (___.__.__.__)",
            "     ⚡ /   ⚡ /  ",
            "       /   ⚡ /   "
        ],
        "sub_icon": "⛈️",
        "telemetry": [
            ("Wind", "⇉ 45 km/h (Gale Force)", "#f43f5e"),
            ("Humidity", "94%", "#34d399"),
            ("Pressure", "998 hPa", "#ef4444"),
            ("Lightning Strikes", "⚡ Frequent", "#ff007f"),
            ("Moon Phase", "⛈️ Storm Obscured", "#94a3b8")
        ],
        "forecast": [
            ("TODAY", 19, "⛈️ Thunder"),
            ("TOMORROW", 18, "🌧️ Heavy Rain"),
            ("NEXT DAY", 21, "⛅ Clearing")
        ]
    },
    "snow": {
        "condition": "Gentle Snowfall", "temp_c": -2, "icon_color": "#e0f7fa",
        "icon": [
            "      .---.      ",
            "    .-(  ❄  )·.  ",
            "   (___.__.__.__)",
            "     *   ❄   *   ",
            "    ❄   *   ❄    "
        ],
        "sub_icon": "❄️",
        "telemetry": [
            ("Wind", "↗ 11 km/h (Light Air)", "#38bdf8"),
            ("Humidity", "76%", "#34d399"),
            ("Pressure", "1024 hPa (High)", "#fbbf24"),
            ("Snow Accum.", "3.5 cm", "#e0f7fa"),
            ("Moon Phase", "❄️ Frost Haze", "#cbd5e1")
        ],
        "forecast": [
            ("TODAY", -2, "❄️ Snowing"),
            ("TOMORROW", -4, "🌨️ Blizzard"),
            ("NEXT DAY", 0, "⛅ Icy Clouds")
        ]
    },
    "cloudy": {
        "condition": "Partly Cloudy & Mild", "temp_c": 21, "icon_color": "#94a3b8",
        "icon": [
            "   \\ /   .---.   ",
            " -( ☀️ )-(     )·.",
            "   / \\ (___.__.__)",
            "          ' ' '  ",
            "         ' ' '   "
        ],
        "sub_icon": "⛅",
        "telemetry": [
            ("Wind", "↗ 16 km/h (Moderate)", "#38bdf8"),
            ("Humidity", "62%", "#34d399"),
            ("Pressure", "1015 hPa", "#fbbf24"),
            ("Cloud Cover", "48%", "#94a3b8"),
            ("Moon Phase", "🌓 First Quarter", "#f472b6")
        ],
        "forecast": [
            ("TODAY", 21, "⛅ Part Cloud"),
            ("TOMORROW", 23, "🌤️ Mostly Sunny"),
            ("NEXT DAY", 20, "🌦️ Passing Rain")
        ]
    },
    "night": {
        "condition": "Starry Night & Crescent Moon", "temp_c": 16, "icon_color": "#c084fc",
        "icon": [
            "      .   *   ✦  ",
            "    *   🌙.·´¯`·.",
            "       (   ✦   ) ",
            "     .   `·.¸.·´ ",
            "       *    .    "
        ],
        "sub_icon": "🌙",
        "telemetry": [
            ("Wind", "↘ 8 km/h (Calm Breeze)", "#38bdf8"),
            ("Humidity", "72%", "#34d399"),
            ("Pressure", "1019 hPa", "#fbbf24"),
            ("Visibility", "10.0 km", "#c084fc"),
            ("Moon Phase", "🌙 Waxing Crescent (28%)", "#ffd700")
        ],
        "forecast": [
            ("TONIGHT", 16, "🌙 Clear Sky"),
            ("TOMORROW", 25, "☀️ Sunny Day"),
            ("NEXT DAY", 22, "🌤️ Warm")
        ]
    },
    "windy": {
        "condition": "High Wind & Atmospheric Vortex", "temp_c": 18, "icon_color": "#38bdf8",
        "icon": [
            "    ༄ ༅ 〰️ 〰️ 〰️  ",
            "  〰️ 〰️ ༄ ༅ 〰️ 〰️ ",
            " ༄ ༅ 〰️ 〰️ 〰️ ༄  ",
            "    〰️ 〰️ ༄ ༅ 〰️  ",
            "  ༄ ༅ 〰️ 〰️ 〰️   "
        ],
        "sub_icon": "💨",
        "telemetry": [
            ("Wind", "⇉ 58 km/h (High Gusts)", "#f59e0b"),
            ("Humidity", "45%", "#34d399"),
            ("Pressure", "1011 hPa", "#fbbf24"),
            ("Air Quality", "AQI 18 (Good)", "#10b981"),
            ("Moon Phase", "🌔 Waxing Gibbous", "#f472b6")
        ],
        "forecast": [
            ("TODAY", 18, "💨 Gusty Wind"),
            ("TOMORROW", 19, "🌬️ Breezy"),
            ("NEXT DAY", 21, "☀️ Calm & Sunny")
        ]
    }
}

@registry.register
class WeatherCardPlugin(BasePlugin):
    name = "weather_card"
    category = "profile"
    description = "Authentic wttr.in style retro ASCII weather card with moon phases and telemetry in SVG"

    def run(
        self,
        city: str = "Curitiba, Brazil",
        condition: str = "sunny",
        unit: str = "C",
        out_svg: str = "weather_card.svg",
        username: str = "meteorologist",
        **kwargs
    ) -> Dict[str, Any]:
        cond_key = condition.lower()
        preset = WEATHER_PRESETS.get(cond_key, WEATHER_PRESETS["sunny"])

        canvas_w = 680
        canvas_h = 330
        titlebar_h = 34
        clip_pfx = "wttr_" + str(abs(hash(out_svg)) % 100000)

        is_f = (unit.upper() == "F")
        def format_temp(c_val: int) -> str:
            if is_f:
                f_val = int(c_val * 9 / 5 + 32)
                return f"{'+' if f_val > 0 else ''}{f_val} °F"
            return f"{'+' if c_val > 0 else ''}{c_val} °C"

        main_temp = format_temp(preset["temp_c"])

        parts = [
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{canvas_w}" height="{canvas_h}" '
            f'viewBox="0 0 {canvas_w} {canvas_h}" font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace">',
            f'<rect width="{canvas_w}" height="{canvas_h}" rx="12" fill="#0c1017"/>',
            f'<rect x="0.5" y="0.5" width="{canvas_w-1}" height="{canvas_h-1}" rx="12" fill="none" stroke="#253045" stroke-width="1"/>',
            f'<line x1="0" y1="{titlebar_h}" x2="{canvas_w}" y2="{titlebar_h}" stroke="#253045"/>'
        ]

        for i, c in enumerate(["#ff5f56", "#ffbd2e", "#27c93f"]):
            parts.append(f'<circle cx="{18 + i*16}" cy="{titlebar_h/2}" r="5" fill="{c}"/>')

        city_clean = city.split(",")[0].strip()
        unit_flag = "?u" if is_f else "?m"
        parts.append(
            f'<text x="{canvas_w/2}" y="{titlebar_h/2 + 4}" fill="#7d8590" font-size="12" '
            f'text-anchor="middle">{username}@terminal: ~$ curl wttr.in/{html.escape(city_clean)}{unit_flag}</text>'
        )

        content_y = titlebar_h + 24
        # Header: City
        parts.append(f'<text x="32" y="{content_y + 12}" fill="#58a6ff" font-size="16" font-weight="bold">Weather report: {html.escape(city)}</text>')

        # Weather Icon Box
        icon_x = 36
        icon_y = content_y + 36
        icon_lines = preset["icon"]
        col = preset["icon_color"]

        for idx, iline in enumerate(icon_lines):
            iy = icon_y + idx * 18
            parts.append(
                f'<text xml:space="preserve" x="{icon_x}" y="{iy:.1f}" fill="{col}" font-size="14" font-weight="bold">{html.escape(iline)}</text>'
            )

        # Main Temp & Status
        parts.append(f'<text x="200" y="{icon_y + 24}" fill="#ffffff" font-size="28" font-weight="bold">{main_temp}</text>')
        parts.append(f'<text x="200" y="{icon_y + 50}" fill="#a0aec0" font-size="13">{preset["condition"]}</text>')

        # Telemetry Block
        tx = 370
        ty = icon_y + 10
        telemetry = preset.get("telemetry", [
            ("Wind", "↗ 14 km/h (Gentle Breeze)", "#38bdf8"),
            ("Humidity", "68%", "#34d399"),
            ("Pressure", "1016 hPa", "#fbbf24"),
            ("Precipitation", "0.0 mm", "#a78bfa"),
            ("Moon Phase", "🌔 Waxing Gibbous", "#f472b6")
        ])

        for label, val, c_val in telemetry:
            parts.append(f'<text x="{tx}" y="{ty:.1f}" fill="#7d8590" font-size="12">{label}: <tspan fill="{c_val}" font-weight="bold">{html.escape(val)}</tspan></text>')
            ty += 20

        # Forecast Bar Divider
        div_y = canvas_h - 68
        parts.append(f'<line x1="32" y1="{div_y}" x2="{canvas_w - 32}" y2="{div_y}" stroke="#212836"/>')

        # 3-Day Forecast Cards
        forecast_items = preset.get("forecast", [
            ("TODAY", preset["temp_c"], "Clear"),
            ("TOMORROW", preset["temp_c"] + 1, "Part Cloud"),
            ("NEXT DAY", preset["temp_c"] - 2, "Rain")
        ])
        day_w = (canvas_w - 64) / 3
        for d_idx, (d_name, d_c, d_cond) in enumerate(forecast_items):
            dx = 32 + d_idx * day_w
            d_temp_str = format_temp(d_c)
            parts.append(f'<text x="{dx + 12}" y="{div_y + 24}" fill="#7d8590" font-size="11" font-weight="bold">{d_name}</text>')
            parts.append(f'<text x="{dx + 12}" y="{div_y + 44}" fill="#ffffff" font-size="13" font-weight="bold">{d_temp_str} <tspan fill="#a0aec0" font-size="11" font-weight="normal">({html.escape(d_cond)})</tspan></text>')

        parts.append('</svg>')
        svg_content = "".join(parts)

        if out_svg:
            os.makedirs(os.path.dirname(os.path.abspath(out_svg)), exist_ok=True)
            with open(out_svg, "w", encoding="utf-8") as f:
                f.write(svg_content)

        return {"status": "success", "output_path": out_svg, "city": city, "unit": unit, "condition": cond_key}

