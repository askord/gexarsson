import os
import math
from grafix import G, E, L
from grafix.api import Export
from app.game.tiles import TILES, CITY, MEADOW, ROAD, MONASTERY

# Colors (RGB 0-1)
COLOR_MEADOW = (0.2, 0.8, 0.2) # Green
COLOR_CITY = (0.6, 0.4, 0.2)   # Brown
COLOR_ROAD = (0.5, 0.5, 0.5)   # Grey
COLOR_MONASTERY = (0.8, 0.2, 0.2) # Red
COLOR_OUTLINE = (0, 0, 0)      # Black

def draw_tile(t_data):
    def draw(t: float):
        # Hex outline (Pointy-topped, Side 0 is North)
        # G.polygon(n=6, phase=0) puts vertices at 0, 60, 120...
        # Flat sides are at 30, 90, 150, 210, 270, 330.
        # We want Side 0 to be at 270 deg (North).
        hex_geom = G.polygon(n_sides=6, center=(100, 100, 0), scale=100, phase=0)
        layers = L.layer(hex_geom, color=COLOR_OUTLINE, thickness=0.02)

        # Meadow background
        meadow_bg = G.polygon(n_sides=6, center=(100, 100, 0), scale=95, phase=0)
        layers += L.layer(meadow_bg, color=COLOR_MEADOW, thickness=0.01)

        # Side features start at -90 degrees (North)
        # Side 0: -90, Side 1: -30, Side 2: 30, Side 3: 90, Side 4: 150, Side 5: 210
        def get_side_angle(i):
            return i * 60 - 90

        # Roads
        if t_data['center'] == ROAD:
            for i, side in enumerate(t_data['sides']):
                if side == ROAD:
                    angle_deg = get_side_angle(i)
                    road_seg = G.line(center=(100, 100, 0), anchor='left', length=50, angle=angle_deg)
                    layers += L.layer(road_seg, color=COLOR_ROAD, thickness=0.05)
        elif ROAD in t_data['sides']:
            road_sides = [i for i, s in enumerate(t_data['sides']) if s == ROAD]
            for i in road_sides:
                angle_deg = get_side_angle(i)
                road_seg = G.line(center=(100, 100, 0), anchor='left', length=50, angle=angle_deg)
                layers += L.layer(road_seg, color=COLOR_ROAD, thickness=0.05)

        # Cities
        if t_data['center'] == CITY:
            city_geom = G.polygon(n_sides=6, center=(100, 100, 0), scale=80, phase=0)
            layers += L.layer(city_geom, color=COLOR_CITY, thickness=0.1)
        else:
            for i, side in enumerate(t_data['sides']):
                if side == CITY:
                    angle_rad = math.radians(get_side_angle(i))
                    cx = 100 + 40 * math.cos(angle_rad)
                    cy = 100 + 40 * math.sin(angle_rad)
                    city_part = G.polygon(n_sides=3, center=(cx, cy, 0), scale=30, phase=get_side_angle(i))
                    layers += L.layer(city_part, color=COLOR_CITY, thickness=0.05)

        # Monastery
        if t_data['center'] == MONASTERY:
            monastery_geom = G.polygon(n_sides=4, center=(100, 100, 0), scale=30, phase=45)
            layers += L.layer(monastery_geom, color=COLOR_MONASTERY, thickness=0.1)

        return layers
    return draw

def render_all():
    os.makedirs("app/static/tiles", exist_ok=True)
    for t_data in TILES:
        draw_func = draw_tile(t_data)
        path = f"app/static/tiles/{t_data['id']}.svg"
        Export(draw_func, t=0.0, fmt="svg", path=path, canvas_size=(200, 200))
        print(f"Rendered {path}")

if __name__ == "__main__":
    render_all()
