#!/usr/bin/env python3
"""Regenerate the journey route: first a loop around China, then around the world.

Reuses the land-blob model from gen_world_map.py (exec'd) for is_land checks.
Splices new route paths + nodes into index.html, replacing everything from
'<!-- base route -->' up to the map svg's closing tag.
"""
import re, math

src = open('gen_world_map.py').read()
g = {}
exec(src.split('# ---- Sample the dot grid ----')[0], g)  # defines W,H,X,Y,blobs,LAT_TOP,LAT_BOT

W, H = g['W'], g['H']
X, Y, blobs = g['X'], g['Y'], g['blobs']

def is_land(lon, lat):
    for blon, blat, r in blobs:
        dlat = lat - blat
        if abs(dlat) > r:
            continue
        dlon = lon - blon
        if abs(dlon) > 180:
            dlon = dlon - 360 if dlon > 0 else dlon + 360
        dlon *= math.cos(math.radians(blat))
        if dlon*dlon + dlat*dlat <= r*r:
            return True
    return False

# ---- Journey nodes: China loop (12) then world loop (7) ----
# (lon, lat, key, (dx, dy, anchor), year_key_or_None, delay)
nodes = [
    # --- Phase 1: around China (schematic spacing to keep east-cluster labels readable) ---
    (110.0, 33.0, "c1",  (0, 22, "middle"),   "1998 · 出生", 0.0, True),   # 菏泽
    (116.0, 36.5, "c2",  (-13, 4, "end"),     None,          0.4, True),   # 济南
    (121.0, 40.0, "c3",  (14, 4, "start"),    None,          0.8, True),   # 天津
    (125.0, 43.5, "c4",  (0, -14, "middle"),  None,          1.2, True),   # 北京
    (130.0, 47.0, "c5",  (0, -14, "middle"),  None,          1.6, True),   # 哈尔滨
    (87.0,  43.0, "c6",  (0, -14, "middle"),  None,          2.0, False),  # 乌鲁木齐
    (91.0,  30.0, "c7",  (14, 0, "start"),    None,          2.4, False),  # 拉萨
    (104.5, 31.0, "c8",  (14, -8, "start"),   None,          2.8, False),  # 成都
    (102.0, 24.0, "c9",  (0, 22, "middle"),   None,          3.2, False),  # 昆明
    (112.5, 25.0, "c10", (0, 22, "middle"),   None,          3.6, False),  # 广州
    (122.0, 31.0, "c11", (14, 4, "start"),    "2026 · 事业", 4.0, False),  # 上海
    (115.5, 21.0, "c12", (0, 22, "middle"),   "2028 · 挂牌", 4.4, False),  # 香港
    # --- Phase 2: around the world ---
    (103.8, 1.35, "c13", (0, 22, "middle"),   "2029 · 远航", 4.8, False),  # 新加坡
    (139.7, 35.7, "c14", (0, -16, "middle"),  "2030 · 东渡", 5.2, False),  # 东京
    (151.2, -33.9, "c15", (0, 22, "middle"),  None,          5.6, False),  # 悉尼
    (-0.13, 51.5, "c16", (0, -16, "middle"),  "2031 · 讲学", 6.0, False),  # 伦敦
    (2.35, 48.85, "c17", (10, 18, "start"),   None,          6.4, False),  # 巴黎
    (-74.0, 40.7, "c18", (0, -16, "middle"),  "2033 · 时代", 6.8, False),  # 纽约
    (-122.4, 37.8, "c19", (0, 22, "middle"),  "2034 · 硅谷", 7.2, False),  # 旧金山
]

FUT_LON, FUT_LAT = -154.0, 26.0

pts = [(X(l), Y(t)) for l, t, *_ in nodes]
fut = (X(FUT_LON), Y(FUT_LAT))

def catmull_rom(points, tension=0.5):
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
last = pts[-1]
future_d = f"M{last[0]:.1f},{last[1]:.1f} Q{last[0]-40:.1f},{last[1]-26:.1f} {fut[0]:.1f},{fut[1]:.1f}"

# ---- Node markup (colors: China-north gold, China-south orange, world blue) ----
CORE_COLORS = ["#ffd58a"] * 6 + ["#ff9a76"] * 6 + ["#8fd0ff"] * 7
node_svg = []
for (lon, lat, key, (dx, dy, anchor), year, delay, tiny), col in zip(nodes, CORE_COLORS):
    x, y = X(lon), Y(lat)
    dly = f' style="animation-delay:{delay}s"' if delay else ""
    cls = "node__city node__city--tiny" if tiny else "node__city"
    lbl = f'<text class="{cls}" x="{dx}" y="{dy}" text-anchor="{anchor}" data-i18n="map.{key}">·</text>'
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

# ---- Phase labels (placed over open ocean) ----
phase1_x, phase1_y = 1350, 312   # Philippine Sea, below the China loop
phase2_x, phase2_y = 630, 110    # North Atlantic, between London and New York
for (px, py) in [(phase1_x, phase1_y), (phase2_x, phase2_y)]:
    lon = px / W * 360 - 180
    lat = 76 - py / H * 142
    print(f"phase label at ({px},{py}) -> lon {lon:.1f}, lat {lat:.1f}, land={is_land(lon, lat)}")

phases_markup = f'''<text class="map-phase map-phase--1" x="{phase1_x}" y="{phase1_y}" text-anchor="middle" data-i18n="map.phase1">① 环游中国</text>
          <text class="map-phase map-phase--2" x="{phase2_x}" y="{phase2_y}" text-anchor="middle" data-i18n="map.phase2">② 环游世界</text>'''

compass = '''<g class="compass" transform="translate(70,548)">
            <circle r="26" fill="rgba(255,255,255,.05)" stroke="rgba(160,180,220,.35)" stroke-width="1.4"/>
            <g class="compass__needle">
              <polygon points="0,-16 4,0 0,4 -4,0" fill="#ff9a76"/>
              <polygon points="0,16 4,0 0,-4 -4,0" fill="rgba(160,180,220,.5)"/>
            </g>
            <circle r="2.4" fill="#eaf0ff"/>
            <text x="0" y="-32" text-anchor="middle" font-size="9" fill="rgba(200,215,240,.7)" font-family="Outfit, sans-serif">N</text>
          </g>'''

new_chunk = f'''<!-- base route -->
          <path class="route route--base" d="{route_d}"/>
          <!-- flowing dashes -->
          <path class="route route--flow" d="{route_d}"/>
          <!-- future dashed extension -->
          <path class="route route--future" d="{future_d}"/>

          {phases_markup}

          {nodes_markup}

          {future_markup}

          {compass}
        '''

html = open('index.html').read()
html, n = re.subn(r'<!-- base route -->.*?</svg>\s*\n      </div>',
                  lambda m: new_chunk + '</svg>\n      </div>',
                  html, count=1, flags=re.S)
assert n == 1, "map chunk not replaced"
open('index.html', 'w').write(html)
print("routes + nodes injected; nodes:", len(nodes))
print("route head:", route_d[:100])
