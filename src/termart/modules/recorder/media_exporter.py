"""
Mezzold TermArt Suite - Media Exporter Module
Renders animated SVGs or terminal graphics into high-quality GIF and MP4 using headless Chromium and ffmpeg.
"""
import os
import re
import shutil
import tempfile
import subprocess
from typing import Dict, Any, Optional, Tuple
from ...core.plugin import BasePlugin
from ...core.registry import registry

HERE = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
DEFAULT_FFMPEG = os.path.join(PROJECT_ROOT, "bin", "ffmpeg.exe" if os.name == "nt" else "ffmpeg")

def get_ffmpeg_bin() -> Optional[str]:
    if os.path.exists(DEFAULT_FFMPEG):
        return DEFAULT_FFMPEG
    found = shutil.which("ffmpeg")
    if found:
        return found
    return None

def extract_svg_dimensions(svg_content: str, fallback_w: int = 800, fallback_h: int = 500) -> Tuple[int, int]:
    w, h = fallback_w, fallback_h
    m_w = re.search(r'\bwidth=["\']([0-9.]+)(?:px)?["\']', svg_content)
    m_h = re.search(r'\bheight=["\']([0-9.]+)(?:px)?["\']', svg_content)
    if m_w and m_h:
        try:
            w = int(float(m_w.group(1)))
            h = int(float(m_h.group(1)))
        except (ValueError, TypeError):
            pass
    elif not (m_w and m_h):
        m_vb = re.search(r'\bviewBox=["\']([0-9.\s,-]+)["\']', svg_content)
        if m_vb:
            parts = [float(p) for p in re.split(r'[\s,]+', m_vb.group(1).strip()) if p]
            if len(parts) >= 4:
                w = int(parts[2])
                h = int(parts[3])
    if w % 2 != 0:
        w += 1
    if h % 2 != 0:
        h += 1
    return max(100, min(3840, w)), max(100, min(2160, h))

def render_svg_frames(
    svg_file_or_content: str,
    output_dir: str,
    duration: float = 3.0,
    fps: int = 20,
    width: Optional[int] = None,
    height: Optional[int] = None
) -> Tuple[int, int, int]:
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        raise RuntimeError("Playwright is required for SVG frame rendering. Install with: pip install playwright && playwright install chromium")

    temp_svg_path = None
    if os.path.isfile(svg_file_or_content):
        svg_path = os.path.abspath(svg_file_or_content)
        with open(svg_path, "r", encoding="utf-8", errors="replace") as f:
            content = f.read()
    else:
        content = svg_file_or_content
        tmp_fd, temp_svg_path = tempfile.mkstemp(suffix=".svg")
        with os.fdopen(tmp_fd, "w", encoding="utf-8") as f:
            f.write(content)
        svg_path = temp_svg_path

    detected_w, detected_h = extract_svg_dimensions(content)
    final_w = width if width and width > 0 else detected_w
    final_h = height if height and height > 0 else detected_h
    if final_w % 2 != 0:
        final_w += 1
    if final_h % 2 != 0:
        final_h += 1

    total_frames = max(1, int(round(duration * fps)))
    interval_ms = 1000.0 / fps

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page(viewport={"width": final_w, "height": final_h})
            file_url = "file:///" + svg_path.replace("\\", "/")
            page.goto(file_url, wait_until="load")
            page.wait_for_timeout(100)

            for i in range(total_frames):
                frame_file = os.path.join(output_dir, f"frame_{i:05d}.png")
                page.screenshot(path=frame_file)
                page.wait_for_timeout(int(interval_ms))

            browser.close()
    finally:
        if temp_svg_path and os.path.exists(temp_svg_path):
            try:
                os.remove(temp_svg_path)
            except OSError:
                pass

    return total_frames, final_w, final_h

def export_svg_to_media(
    svg_source: str,
    output_path: str,
    fmt: str = "gif",
    duration: float = 3.0,
    fps: Optional[int] = None,
    width: Optional[int] = None,
    height: Optional[int] = None
) -> Dict[str, Any]:
    ffmpeg_bin = get_ffmpeg_bin()
    if not ffmpeg_bin:
        raise RuntimeError("ffmpeg binary not found in bin/ffmpeg.exe or system PATH")

    fmt = fmt.lower().strip().replace(".", "")
    if fmt not in ("gif", "mp4"):
        raise ValueError(f"Unsupported format '{fmt}'. Choose 'gif' or 'mp4'")

    if fps is None:
        fps = 16 if fmt == "gif" else 24

    with tempfile.TemporaryDirectory() as frame_dir:
        total_frames, w, h = render_svg_frames(
            svg_source,
            frame_dir,
            duration=duration,
            fps=fps,
            width=width,
            height=height
        )

        frame_pattern = os.path.join(frame_dir, "frame_%05d.png")
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)

        if fmt == "gif":
            cmd = [
                ffmpeg_bin, "-y",
                "-framerate", str(fps),
                "-i", frame_pattern,
                "-vf", "split[s0][s1];[s0]palettegen=stats_mode=diff[p];[s1][p]paletteuse=dither=bayer:bayer_scale=3",
                output_path
            ]
        else:
            cmd = [
                ffmpeg_bin, "-y",
                "-framerate", str(fps),
                "-i", frame_pattern,
                "-c:v", "libx264",
                "-preset", "fast",
                "-crf", "22",
                "-pix_fmt", "yuv420p",
                "-vf", "pad=ceil(iw/2)*2:ceil(ih/2)*2",
                output_path
            ]

        res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if res.returncode != 0:
            err_msg = res.stderr.decode("utf-8", errors="replace")
            raise RuntimeError(f"ffmpeg conversion failed: {err_msg}")

    size_bytes = os.path.getsize(output_path) if os.path.exists(output_path) else 0
    return {
        "status": "success",
        "output_path": output_path,
        "format": fmt,
        "frames": total_frames,
        "width": w,
        "height": h,
        "fps": fps,
        "duration": duration,
        "size_bytes": size_bytes
    }

@registry.register
class MediaExporterPlugin(BasePlugin):
    name = "media_exporter"
    category = "recorder"
    description = "Export animated SVGs to high-fidelity GIF and MP4 using headless Chromium & ffmpeg"

    def run(self, svg_source: str, output_path: str, fmt: str = "gif", duration: float = 3.0, fps: Optional[int] = None, **kwargs) -> Dict[str, Any]:
        try:
            return export_svg_to_media(
                svg_source=svg_source,
                output_path=output_path,
                fmt=fmt,
                duration=duration,
                fps=fps,
                width=kwargs.get("width"),
                height=kwargs.get("height")
            )
        except Exception as e:
            return {
                "status": "error",
                "message": str(e)
            }
