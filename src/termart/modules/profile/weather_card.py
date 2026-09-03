"""
Mezzold TermArt - Retro Terminal Weather Forecast Card Module
Renders an authentic, zero-token, rate-limit-free ASCII weather forecast card
with animated weather icons, temperature trends, moon phases, and atmospheric telemetry.
Inspired by chubin/wttr.in.
"""
import os
import html
from typing import Dict, Any
from ...core.plugin import BasePlugin
from ...core.registry import registry

WEATHER_PRESETS = {
    "sunny": {
        "condition": "Sunny / Clear Sky", "temp": "+24 °C", "icon_color": "#ffd700",
        "icon": [
            "    \\   /    ",
            "     .-.     ",
            "  ― (   ) ―  ",
            "     `-’     ",
            "    /   \\    "
        ],
        "rain": False
    },
    "rainy": {
        "condition": "Light Cyberpunk Rain", "temp": "+17 °C", "icon_color": "#00e5ff",
        "icon": [
            "     .-.     ",
            "    (   ).   ",
            "   (___(__)  ",
            "   ‘ ‘ ‘ ‘   ",
            "  ‘ ‘ ‘ ‘    "
        ],
        "rain": True
    },
    "thunder": {
        "condition": "Severe Thunderstorm", "temp": "+19 °C", "icon_color": "#ff007f",
        "icon": [
            "     .-.     ",
            "    (   ).   ",
            "   (___(__)  ",
            "    ⚡ / ⚡   ",
            "     /   /   "
        ],
        "rain": True
    },
    "snow": {
        "condition": "Gentle Snowfall", "temp": "-2 °C", "icon_color": "#e0f7fa",
        "icon": [
            "     .-.     ",
            "    (   ).   ",
            "   (___(__)  ",
            "    *  *  *  ",
            "   *  *  *   "
        ],
        "rain": False
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
        out_svg: str = "weather_card.svg",
        username: str = "meteorologist",
        **kwargs
    ) -> Dict[str, Any]:
        preset = WEATHER_PRESETS.get(condition.lower(), WEATHER_PRESETS["sunny"])

        canvas_w = 680
        canvas_h = 320
        titlebar_h = 34
        clip_pfx = "wttr_" + str(abs(hash(out_svg)) % 100000)

        parts = [
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{canvas_w}" height="{canvas_h}" '
            f'viewBox="0 0 {canvas_w} {canvas_h}" font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace">',
            f'<rect width="{canvas_w}" height="{canvas_h}" rx="12" fill="#0c1017"/>',
            f'<rect x="0.5" y="0.5" width="{canvas_w-1}" height="{canvas_h-1}" rx="12" fill="none" stroke="#253045" stroke-width="1"/>',
            f'<line x1="0" y1="{titlebar_h}" x2="{canvas_w}" y2="{titlebar_h}" stroke="#253045"/>'
        ]

        for i, c in enumerate(["#ff5f56", "#ffbd2e", "#27c93f"]):
            parts.append(f'<circle cx="{18 + i*16}" cy="{titlebar_h/2}" r="5" fill="{c}"/>')

        parts.append(
            f'<text x="{canvas_w/2}" y="{titlebar_h/2 + 4}" fill="#7d8590" font-size="12" '
            f'text-anchor="middle">{username}@terminal: ~$ curl wttr.in/{html.escape(city.split(",")[0].strip())}</text>'
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
        parts.append(f'<text x="180" y="{icon_y + 24}" fill="#ffffff" font-size="28" font-weight="bold">{preset["temp"]}</text>')
        parts.append(f'<text x="180" y="{icon_y + 50}" fill="#a0aec0" font-size="13">{preset["condition"]}</text>')

        # Telemetry Block
        tx = 360
        ty = icon_y + 10
        telemetry = [
            ("Wind", "↗ 14 km/h (Gentle Breeze)", "#38bdf8"),
            ("Humidity", "68%", "#34d399"),
            ("Pressure", "1016 hPa", "#fbbf24"),
            ("Precipitation", "0.0 mm", "#a78bfa"),
            ("Moon Phase", "🌔 Waxing Gibbous", "#f472b6")
        ]

        for label, val, c_val in telemetry:
            parts.append(f'<text x="{tx}" y="{ty:.1f}" fill="#7d8590" font-size="12">{label}: <tspan fill="{c_val}" font-weight="bold">{html.escape(val)}</tspan></text>')
            ty += 20

        # Forecast Bar Divider
        div_y = canvas_h - 68
        parts.append(f'<line x1="32" y1="{div_y}" x2="{canvas_w - 32}" y2="{div_y}" stroke="#212836"/>')

        # 3-Day Forecast Cards
        days = [
            ("TODAY", "+24 °C", "☀ Clear"),
            ("TOMORROW", "+22 °C", "⛅ Part Cloud"),
            ("WEDNESDAY", "+19 °C", "🌧 Light Rain")
        ]
        day_w = (canvas_w - 64) / 3
        for d_idx, (d_name, d_temp, d_cond) in enumerate(days):
            dx = 32 + d_idx * day_w
            parts.append(f'<text x="{dx + 12}" y="{div_y + 24}" fill="#7d8590" font-size="11" font-weight="bold">{d_name}</text>')
            parts.append(f'<text x="{dx + 12}" y="{div_y + 44}" fill="#ffffff" font-size="13" font-weight="bold">{d_temp} <tspan fill="#a0aec0" font-size="11" font-weight="normal">({d_cond})</tspan></text>')

        parts.append('</svg>')
        svg_content = "".join(parts)

        if out_svg:
            os.makedirs(os.path.dirname(os.path.abspath(out_svg)), exist_ok=True)
            with open(out_svg, "w", encoding="utf-8") as f:
                f.write(svg_content)

        return {"status": "success", "output_path": out_svg, "city": city}
