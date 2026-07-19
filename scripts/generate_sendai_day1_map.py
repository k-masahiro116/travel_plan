#!/usr/bin/env python3
"""Generate a zoomed-in walking route map for Sendai Day 1."""

from __future__ import annotations

import io
import math
from pathlib import Path

import requests
from PIL import Image, ImageDraw, ImageFont

OUTPUT = Path(__file__).resolve().parents[1] / "plans/sendai-aug2026/images/day1-walking-route.png"

STOPS = [
    (38.25962, 140.88389, "① 仙台駅東口\n（スタート）", "#1e5a7a"),
    (38.25910, 140.88250, "② エスパル仙台\n駅前", "#3d7a62"),
    (38.26180, 140.87600, "③ 定禅寺通\n（東二番丁側）", "#6aab8f"),
    (38.26890, 140.87040, "④ 定禅寺通\n（市役所前）", "#6aab8f"),
    (38.26830, 140.86970, "⑤ 勾当台公園", "#2a6f85"),
    (38.26450, 140.87150, "⑥ クリスロード\n（一番町）", "#3d7a62"),
    (38.26080, 140.88020, "⑦ 青葉通り\n→ 東口へ", "#3d7a62"),
    (38.25962, 140.88389, "⑧ 仙台駅東口\n（ゴール）", "#9b2d30"),
]

ZOOM = 17
TILE_SIZE = 256
USER_AGENT = "HukushimaTravelMap/1.0 (local static map generator)"
OSRM_URL = "https://router.project-osrm.org/route/v1/foot"
FONT_PATHS = [
    "/System/Library/Fonts/Hiragino Sans GB.ttc",
    "/Library/Fonts/Arial Unicode.ttf",
    "/System/Library/Fonts/Supplemental/Arial Unicode.ttf",
]


def load_font(size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    for path in FONT_PATHS:
        try:
            return ImageFont.truetype(path, size)
        except OSError:
            continue
    return ImageFont.load_default()


def latlon_to_pixel(lat: float, lon: float, zoom: int) -> tuple[float, float]:
    sin_lat = math.sin(math.radians(lat))
    scale = TILE_SIZE * (2**zoom)
    x = (lon + 180.0) / 360.0 * scale
    y = (0.5 - math.log((1 + sin_lat) / (1 - sin_lat)) / (4 * math.pi)) * scale
    return x, y


def fetch_road_route(stops: list[tuple]) -> tuple[list[tuple[float, float]], float]:
    """Fetch walking path along roads via OSRM. Returns points and distance in meters."""
    coords = ";".join(f"{lon},{lat}" for lat, lon, *_ in stops)
    response = requests.get(
        f"{OSRM_URL}/{coords}",
        params={"overview": "full", "geometries": "geojson", "steps": "false"},
        headers={"User-Agent": USER_AGENT},
        timeout=30,
    )
    response.raise_for_status()
    data = response.json()
    if data.get("code") != "Ok" or not data.get("routes"):
        raise RuntimeError(f"OSRM routing failed: {data.get('code')}")

    route = data["routes"][0]
    geometry = route["geometry"]["coordinates"]
    points = [(lat, lon) for lon, lat in geometry]
    return points, float(route["distance"])


def fetch_road_route_with_fallback(stops: list[tuple]) -> tuple[list[tuple[float, float]], float | None]:
    try:
        points, distance = fetch_road_route(stops)
        print(f"Road route: {len(points)} points, {distance:.0f} m")
        return points, distance
    except Exception as exc:
        print(f"Warning: road routing unavailable ({exc}); using straight segments.")
        return [(lat, lon) for lat, lon, *_ in stops], None


def fetch_tile(z: int, x: int, y: int) -> Image.Image:
    url = f"https://tile.openstreetmap.org/{z}/{x}/{y}.png"
    response = requests.get(url, headers={"User-Agent": USER_AGENT}, timeout=20)
    response.raise_for_status()
    return Image.open(io.BytesIO(response.content)).convert("RGBA")


def draw_labels(
    draw: ImageDraw.ImageDraw,
    stops: list[tuple],
    to_xy,
    font: ImageFont.ImageFont,
    scale: float = 1.0,
) -> None:
    for idx, (lat, lon, label, color) in enumerate(stops):
        sx, sy = to_xy(lat, lon)
        r = int(16 * scale) if idx in (0, len(stops) - 1) else int(12 * scale)
        draw.ellipse((sx - r, sy - r, sx + r, sy + r), fill=color, outline=(255, 255, 255, 255), width=3)
        tx, ty = sx + int(18 * scale), sy - int(20 * scale)
        for line in label.split("\n"):
            draw.text((tx + 1, ty + 1), line, fill=(255, 255, 255, 230), font=font)
            draw.text((tx, ty), line, fill=(30, 37, 32, 255), font=font)
            ty += int(19 * scale)


def build_map() -> Image.Image:
    road_route, distance_m = fetch_road_route_with_fallback(STOPS)

    lats = [p[0] for p in road_route]
    lons = [p[1] for p in road_route]
    pad = 0.0014
    min_lat, max_lat = min(lats) - pad, max(lats) + pad
    min_lon, max_lon = min(lons) - pad, max(lons) + pad

    x1, y2 = latlon_to_pixel(min_lat, min_lon, ZOOM)
    x2, y1 = latlon_to_pixel(max_lat, max_lon, ZOOM)

    tile_x_min = int(x1 // TILE_SIZE)
    tile_y_min = int(y1 // TILE_SIZE)
    tile_x_max = int(x2 // TILE_SIZE)
    tile_y_max = int(y2 // TILE_SIZE)

    canvas = Image.new(
        "RGBA",
        ((tile_x_max - tile_x_min + 1) * TILE_SIZE, (tile_y_max - tile_y_min + 1) * TILE_SIZE),
    )

    for ty in range(tile_y_min, tile_y_max + 1):
        for tx in range(tile_x_min, tile_x_max + 1):
            tile = fetch_tile(ZOOM, tx, ty)
            ox = (tx - tile_x_min) * TILE_SIZE
            oy = (ty - tile_y_min) * TILE_SIZE
            canvas.paste(tile, (ox, oy))

    origin_x = tile_x_min * TILE_SIZE
    origin_y = tile_y_min * TILE_SIZE

    def to_local(lat: float, lon: float) -> tuple[int, int]:
        px, py = latlon_to_pixel(lat, lon, ZOOM)
        return int(px - origin_x), int(py - origin_y)

    route_points = [to_local(lat, lon) for lat, lon in road_route]

    xs = [p[0] for p in route_points]
    ys = [p[1] for p in route_points]
    margin = 70
    left = max(0, min(xs) - margin)
    top = max(0, min(ys) - margin)
    right = min(canvas.width, max(xs) + margin)
    bottom = min(canvas.height, max(ys) + margin)
    cropped = canvas.crop((left, top, right, bottom))

    out_w = min(1600, max(1000, cropped.width))
    scale = out_w / cropped.width
    cropped = cropped.resize((out_w, int(cropped.height * scale)), Image.Resampling.LANCZOS)

    scaled_points = [
        (int((x - left) * scale), int((y - top) * scale)) for x, y in route_points
    ]

    draw = ImageDraw.Draw(cropped, "RGBA")
    draw.line(scaled_points, fill=(30, 90, 122, 230), width=max(6, int(8 * scale)), joint="curve")
    draw.line(scaled_points, fill=(106, 171, 143, 220), width=max(3, int(4 * scale)), joint="curve")

    label_font = load_font(max(14, int(15 * scale)))
    title_font = load_font(max(20, int(22 * scale)))
    note_font = load_font(max(12, int(13 * scale)))

    def to_scaled(lat: float, lon: float) -> tuple[int, int]:
        x, y = to_local(lat, lon)
        return int((x - left) * scale), int((y - top) * scale)

    draw_labels(draw, STOPS, to_scaled, label_font, scale)

    distance_note = f" · 徒歩約 {distance_m / 1000:.1f} km" if distance_m else ""
    banner_h = 58
    banner = Image.new("RGBA", (cropped.width, banner_h), (255, 255, 255, 240))
    bdraw = ImageDraw.Draw(banner)
    bdraw.text((14, 12), "仙台駅周辺 徒歩観光ルート（1日目 10:00–12:00）", fill=(30, 90, 122, 255), font=title_font)
    bdraw.text(
        (14, 36),
        f"© OpenStreetMap · 道のり表示（OSRM） · zoom {ZOOM}{distance_note}",
        fill=(107, 99, 90, 255),
        font=note_font,
    )

    final_img = Image.new("RGB", (cropped.width, cropped.height + banner_h), (250, 247, 242))
    final_img.paste(banner, (0, 0))
    final_img.paste(cropped.convert("RGB"), (0, banner_h))
    return final_img


def main() -> None:
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    image = build_map()
    image.save(OUTPUT, format="PNG", optimize=True)
    print(f"Saved: {OUTPUT} ({image.width}x{image.height})")


if __name__ == "__main__":
    main()
