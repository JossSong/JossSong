#!/usr/bin/env python3
"""Generate a dot-matrix world map + journey route SVG for the intro page.

Compliance notes:
- No national borders are drawn (dot matrix only) -> sidesteps border disputes.
- Taiwan and South China Sea islands are included as land dots (part of China).
"""
import math

W, H = 1600, 632
LAT_TOP, LAT_BOT = 76.0, -66.0  # 142 deg span

def X(lon): return (lon + 180.0) / 360.0 * W
def Y(lat): return (LAT_TOP - lat) / (LAT_TOP - LAT_BOT) * H

# ---- Land blobs: (lon, lat, radius_deg). Author by continent. ----
blobs = [
    # ---- North America ----
    (-150, 64, 9), (-160, 66, 6), (-145, 60, 6),          # Alaska
    (-125, 55, 7), (-120, 60, 8), (-110, 60, 8), (-100, 58, 8),
    (-95, 52, 7), (-85, 50, 7), (-78, 52, 7), (-75, 58, 6),
    (-80, 62, 6), (-90, 63, 6), (-105, 68, 8), (-120, 68, 8),
    (-135, 68, 7), (-75, 68, 6), (-85, 72, 6), (-100, 73, 6),
    (-115, 73, 6), (-68, 62, 5), (-73, 62, 4),             # E Canada / Quebec
    (-95, 40, 7), (-100, 38, 6), (-105, 40, 6), (-112, 40, 6),
    (-118, 37, 5), (-122, 42, 4), (-95, 33, 5), (-100, 30, 5),
    (-105, 32, 5), (-82, 35, 5), (-80, 38, 5), (-85, 40, 5),
    (-88, 33, 4), (-90, 30, 4), (-95, 28, 4), (-80, 26, 3),  # Florida
    (-82, 30, 3),
    (-102, 22, 5), (-100, 25, 4), (-95, 20, 4), (-92, 17, 3),
    (-88, 16, 3), (-86, 13, 3), (-90, 14, 2), (-96, 16, 2),
    (-105, 20, 3), (-108, 27, 3), (-110, 30, 2), (-113, 27, 2),  # Mexico + Baja
    # Greenland
    (-45, 72, 8), (-40, 76, 7), (-35, 72, 6), (-50, 68, 6),
    (-55, 72, 5), (-42, 70, 5), (-38, 66, 4),
    (-79, 22, 2),                                            # Cuba
    (-18, 65, 2),                                            # Iceland
    # ---- South America ----
    (-70, 10, 5), (-75, 5, 5), (-78, 0, 5), (-76, -8, 6), (-72, -16, 6),
    (-70, -24, 6), (-70, -32, 6), (-71, -40, 5), (-73, -46, 4), (-69, -52, 3),
    (-50, -5, 6), (-45, -10, 5), (-42, -18, 5), (-48, -22, 5),
    (-55, -28, 5), (-58, -33, 4), (-62, -38, 4), (-65, -42, 3),
    (-57, -30, 4), (-60, -8, 5), (-55, -2, 5), (-52, -28, 4),
    (-56, -20, 5), (-44, -3, 4), (-40, -7, 3), (-35, -6, 3),
    # ---- Africa ----
    (-6, 32, 5), (0, 34, 5), (8, 36, 5), (15, 32, 5), (20, 32, 5),
    (25, 32, 5), (32, 31, 4), (10, 30, 6), (20, 27, 6), (30, 27, 6),
    (35, 28, 3),
    (-5, 22, 5), (0, 20, 5), (-8, 15, 4), (-12, 12, 4), (5, 20, 6),
    (10, 20, 6), (15, 22, 5),
    (35, 15, 5), (42, 12, 4), (48, 8, 3), (40, 5, 4), (38, 0, 4),
    (20, 5, 5), (25, 5, 5), (30, 5, 5), (18, -5, 5), (24, -12, 5),
    (30, -15, 5), (25, -20, 5), (20, -25, 5), (28, -28, 4), (32, -25, 4),
    (18, -33, 3), (25, -33, 3), (12, -38, 3), (18, -34, 3),
    (47, -19, 3), (47, -15, 3), (45, -22, 2),               # Madagascar
    # ---- Europe ----
    (-4, 40, 4), (-6, 37, 3), (-2, 38, 2),                  # Iberia
    (2, 47, 4), (0, 45, 3),                                  # France
    (-2, 53, 3), (-1, 56, 2), (-4, 54, 2), (-3, 57, 2), (-8, 53, 2),  # UK/IE
    (10, 50, 5), (16, 50, 4), (20, 45, 4), (25, 45, 4), (30, 45, 4),
    (8, 45, 3), (12, 44, 3), (14, 48, 3), (20, 40, 3), (22, 42, 3),
    (10, 60, 4), (5, 58, 3), (15, 63, 4), (18, 67, 3), (12, 68, 3),
    (22, 66, 3), (25, 70, 3),                                # Scandinavia
    (13, 42, 2), (15, 39, 2), (12, 38, 2),                   # Italy
    (21, 41, 3), (23, 39, 2), (26, 41, 3),                   # Balkans/Greece
    # ---- Russia / Siberia ----
    (35, 52, 5), (40, 55, 5), (45, 55, 5), (50, 55, 5), (40, 48, 4),
    (48, 48, 4), (55, 52, 5), (60, 55, 5), (55, 58, 5), (60, 60, 5),
    (65, 60, 5), (70, 60, 5), (60, 65, 5), (70, 65, 5), (75, 65, 5),
    (80, 65, 5), (65, 70, 5), (75, 72, 5), (85, 70, 5), (95, 70, 5),
    (105, 72, 5), (115, 70, 5), (90, 60, 6), (100, 62, 6), (110, 62, 6),
    (120, 62, 6), (130, 62, 6), (140, 60, 6), (150, 60, 6), (160, 62, 5),
    (170, 62, 5), (105, 55, 5), (115, 50, 5), (125, 50, 5), (135, 48, 5),
    (145, 48, 5), (155, 50, 4), (120, 45, 5), (130, 45, 4), (140, 45, 4),
    (100, 50, 5), (90, 50, 5), (80, 50, 5), (70, 50, 5), (85, 55, 5),
    (95, 55, 5), (78, 60, 5), (105, 58, 5), (165, 58, 4), (172, 58, 3),
    # ---- Middle East ----
    (45, 35, 4), (50, 32, 4), (55, 28, 4), (58, 25, 3), (52, 38, 3),
    (45, 40, 3), (38, 38, 3), (43, 32, 3), (48, 28, 3), (35, 34, 3), (40, 36, 3),
    # ---- Central Asia ----
    (65, 45, 5), (70, 45, 5), (75, 45, 5), (80, 42, 4), (85, 45, 4),
    (55, 45, 4), (60, 42, 4), (70, 40, 4), (80, 38, 4), (88, 43, 3),
    # ---- India ----
    (75, 22, 5), (78, 15, 4), (80, 10, 4), (77, 25, 5), (72, 20, 4),
    (73, 28, 3), (80, 25, 4), (85, 25, 3), (88, 22, 3), (90, 27, 3),
    (93, 28, 2), (77, 8, 2), (72, 12, 2), (76, 10, 2), (81, 7, 1),  # Sri Lanka
    # ---- China (incl. Taiwan & South China Sea islands) ----
    (105, 35, 6), (110, 35, 6), (115, 35, 6), (120, 32, 5), (112, 30, 5),
    (105, 30, 5), (100, 30, 5), (95, 30, 4), (100, 38, 5), (108, 40, 4),
    (115, 40, 5), (120, 38, 5), (122, 42, 4), (127, 45, 4), (130, 47, 4),
    (120, 48, 5), (110, 45, 5), (95, 45, 5), (88, 45, 4), (85, 42, 3),
    (125, 40, 4), (118, 28, 4), (110, 25, 4), (105, 23, 3), (115, 23, 4),
    (110, 38, 4), (104, 38, 4), (97, 35, 4), (90, 33, 3), (95, 33, 3),
    (100, 26, 3), (108, 32, 4), (110, 19, 1),               # Hainan
    (121, 23.5, 1.2),                                       # Taiwan (part of China)
    # South China Sea islands (Xisha / Zhongsha / Nansha)
    (112, 16, 1), (114, 10, 1), (116, 8, 0.9), (110, 9, 0.9), (113, 5, 0.9),
    # ---- Korea ----
    (128, 36, 2.5), (127, 38, 2), (128, 41, 1.5),
    # ---- Japan ----
    (140, 38, 3), (139, 35, 3), (136, 34, 2), (133, 34, 2), (131, 33, 2),
    (141, 42, 2), (143, 43, 2), (140, 41, 2), (137, 37, 2), (132, 34, 2),
    (130, 31, 1.5), (135, 34, 2), (138, 36, 2), (140, 40, 2), (142, 44, 2),
    # ---- SE Asia ----
    (97, 20, 3), (99, 16, 3), (101, 14, 3), (100, 8, 2), (103, 10, 2),
    (105, 12, 2), (106, 20, 2), (107, 15, 2), (108, 11, 2), (106, 17, 2),
    (104, 15, 2), (105, 18, 2), (103, 13, 2),
    (102, 4, 2), (110, 3, 2), (103, 3, 2), (101, 4, 2),
    # Indonesia
    (110, -2, 4), (114, -4, 3), (118, -2, 3), (120, -4, 3), (105, -5, 3),
    (115, -7, 3), (120, -8, 3), (125, -4, 3), (130, -3, 3), (135, -3, 3),
    (140, -4, 3), (145, -5, 3), (130, -8, 2), (125, -8, 2), (140, -8, 2),
    (105, -2, 3), (100, -1, 3), (103, -3, 3), (98, 2, 2),
    (121, 15, 2), (122, 12, 2), (124, 11, 2), (121, 17, 2), (125, 8, 1.5),  # Philippines
    (145, -6, 4), (140, -7, 3), (150, -8, 3), (148, -9, 2), (143, -8, 3),  # PNG
    # ---- Australia ----
    (120, -25, 6), (125, -30, 5), (130, -28, 5), (135, -25, 5), (140, -25, 5),
    (145, -25, 5), (150, -28, 5), (148, -33, 4), (145, -37, 4), (140, -37, 4),
    (135, -35, 4), (130, -32, 4), (125, -33, 4), (118, -32, 3), (122, -34, 3),
    (115, -29, 3), (132, -20, 4), (140, -20, 4), (145, -20, 4), (150, -22, 4),
    (155, -27, 3), (152, -25, 3), (147, -42, 1.5),          # Tasmania
    (173, -42, 2), (175, -38, 2), (172, -44, 1.5), (176, -40, 1.5), (170, -45, 1.5),  # NZ
]

def is_land(lon, lat):
    for blon, blat, r in blobs:
        dlat = lat - blat
        if abs(dlat) > r:
            continue
        dlon = (lon - blon)
        if abs(dlon) > 180:
            dlon = dlon - 360 if dlon > 0 else dlon + 360
        dlon *= math.cos(math.radians(blat))
        if dlon * dlon + dlat * dlat <= r * r:
            return True
    return False

# ---- Sample the dot grid ----
STEP = 2.2
dots = []
lon = -180 + STEP / 2
while lon < 180:
    lat = LAT_TOP - STEP / 2
    while lat > LAT_BOT:
        if is_land(lon, lat):
            dots.append((X(lon), Y(lat)))
        lat -= STEP
    lon += STEP

path_d = " ".join(f"M{x:.1f},{y:.1f}l0,0" for x, y in dots)
print(f"land dots: {len(dots)}, path len: {len(path_d)} chars")

# ---- Journey nodes (chronological order) ----
# (lon, lat, key, label-placement: (dx, dy, anchor), year-key, delay)
nodes = [
    (115.5, 35.2, "c1",  (0, 20, "middle"),  "1998 · 出生", .0),
    (117.0, 36.7, "c2",  (-13, 4, "end"),    None,          .4),
    (117.2, 39.1, "c3",  (0, -14, "middle"), "2024 · 深造", .8),
    (121.5, 31.2, "c4",  (14, 4, "start"),   "2026 · 事业", 1.2),
    (114.2, 22.3, "c5",  (0, 22, "middle"),  "2028 · 挂牌", 1.6),
    (103.8, 1.35, "c6",  (0, 22, "middle"),  "2029 · 远航", 2.0),
    (139.7, 35.7, "c7",  (0, -16, "middle"), "2030 · 东渡", 2.4),
    (-0.13, 51.5, "c8",  (0, -16, "middle"), "2031 · 讲学", 2.8),
    (2.35, 48.85, "c9",  (10, 18, "start"),  None,          3.2),
    (-74.0, 40.7, "c10", (0, -16, "middle"), "2033 · 时代", 3.6),
    (-122.4, 37.8, "c11", (0, 22, "middle"), "2034 · 硅谷", 4.0),
]

# future node: out in the Pacific
FUT_LON, FUT_LAT = -154.0, 26.0

# ---- Catmull-Rom -> cubic bezier path through node points ----
pts = [(X(l), Y(t)) for l, t, *_ in nodes]
fut = (X(FUT_LON), Y(FUT_LAT))

def catmull_rom(points, tension=0.5):
    if len(points) < 3:
        return ""
    d = f"M{points[0][0]:.1f},{points[0][1]:.1f}"
    n = len(points)
    for i in range(n - 1):
        p0 = points[max(i - 1, 0)]
        p1 = points[i]
        p2 = points[i + 1]
        p3 = points[min(i + 2, n - 1)]
        c1 = (p1[0] + (p2[0] - p0[0]) / 6 * tension * 2,
              p1[1] + (p2[1] - p0[1]) / 6 * tension * 2)
        c2 = (p2[0] - (p3[0] - p1[0]) / 6 * tension * 2,
              p2[1] - (p3[1] - p1[1]) / 6 * tension * 2)
        d += f" C{c1[0]:.1f},{c1[1]:.1f} {c2[0]:.1f},{c2[1]:.1f} {p2[0]:.1f},{p2[1]:.1f}"
    return d

route_d = catmull_rom(pts)
# future dashed extension: gentle arc from SF toward the open Pacific
last = pts[-1]
future_d = f"M{last[0]:.1f},{last[1]:.1f} Q{last[0]-40:.1f},{last[1]-26:.1f} {fut[0]:.1f},{fut[1]:.1f}"

# ---- Build node markup ----
CORE_COLORS = ["#ffd58a"] * 3 + ["#ff9a76"] * 3 + ["#8fd0ff"] * 5
node_svg = []
for (lon, lat, key, (dx, dy, anchor), year, delay), col in zip(nodes, CORE_COLORS):
    x, y = X(lon), Y(lat)
    dly = f' style="animation-delay:{delay}s"' if delay else ""
    ydly = f' style="animation-delay:{delay}s"' if delay else ""
    lbl = f'<text class="node__city" x="{dx}" y="{dy}" text-anchor="{anchor}" data-i18n="map.{key}">·</text>'
    yr = ""
    if year:
        yy = dy + 14 if dy > 0 else dy - 14
        yr = f'<text class="node__year" x="{dx}" y="{yy}" text-anchor="{anchor}" data-i18n="map.{key}y">·</text>'
    node_svg.append(
        f'''<g class="node" transform="translate({x:.1f},{y:.1f})">
            <circle class="node__pulse" r="12" fill="none" stroke="{col}" stroke-width="2"{dly}/>
            <circle class="node__core" r="5.5" fill="{col}" stroke="#2a3450" stroke-width="2"/>
            {lbl}{yr}
          </g>''')
nodes_markup = "\n          ".join(node_svg)

future_markup = f'''<g class="node node--future" transform="translate({fut[0]:.1f},{fut[1]:.1f})">
            <circle class="node__core" r="6" fill="none" stroke="#8fd0ff" stroke-width="2" stroke-dasharray="3 4"/>
            <text class="node__city" x="0" y="-16" text-anchor="middle" opacity=".75" data-i18n="map.future">未来 …</text>
          </g>'''

# ---- Compass at bottom-left (empty South Pacific area) ----
compass = '''<g class="compass" transform="translate(70,548)">
            <circle r="26" fill="rgba(255,255,255,.05)" stroke="rgba(160,180,220,.35)" stroke-width="1.4"/>
            <g class="compass__needle">
              <polygon points="0,-16 4,0 0,4 -4,0" fill="#ff9a76"/>
              <polygon points="0,16 4,0 0,-4 -4,0" fill="rgba(160,180,220,.5)"/>
            </g>
            <circle r="2.4" fill="#eaf0ff"/>
            <text x="0" y="-32" text-anchor="middle" font-size="9" fill="rgba(200,215,240,.7)" font-family="Outfit, sans-serif">N</text>
          </g>'''

svg = f'''<svg class="map map--world" viewBox="0 0 {W} {H}" role="img" aria-label="world journey" data-i18n-aria="map.aria">
          <defs>
            <linearGradient id="routeGrad" x1="0" y1="0" x2="1" y2="0">
              <stop offset="0%" stop-color="#ffd58a"/>
              <stop offset="55%" stop-color="#ff9a76"/>
              <stop offset="100%" stop-color="#8fd0ff"/>
            </linearGradient>
          </defs>

          <!-- land dot-matrix world map (no borders; Taiwan & S. China Sea islands included) -->
          <path class="map-land" d="{path_d}" fill="none" stroke-width="3.2" stroke-linecap="round"/>

          <!-- equator + tropics, very faint -->
          <g stroke="rgba(160,180,220,.10)" stroke-width="1" stroke-dasharray="2 8">
            <line x1="0" y1="{Y(0):.1f}" x2="{W}" y2="{Y(0):.1f}"/>
            <line x1="0" y1="{Y(23.5):.1f}" x2="{W}" y2="{Y(23.5):.1f}"/>
            <line x1="0" y1="{Y(-23.5):.1f}" x2="{W}" y2="{Y(-23.5):.1f}"/>
          </g>

          <!-- base route -->
          <path class="route route--base" d="{route_d}"/>
          <!-- flowing dashes -->
          <path class="route route--flow" d="{route_d}"/>
          <!-- future dashed extension -->
          <path class="route route--future" d="{future_d}"/>

          {nodes_markup}

          {future_markup}

          {compass}
        </svg>'''

with open("world_map.svg.frag", "w") as f:
    f.write(svg)
print("wrote world_map.svg.frag")
print("route:", route_d[:120], "...")
