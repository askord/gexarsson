import os
import math
from grafix import G, E
from grafix.api import Export
from app.game.tiles import TILES, CITY, MEADOW, ROAD

def draw_tile(t_data):
    def draw(t: float):
        # Hex centered at (100, 100) with radius 50.
        # grafix polygon(n=6, scale=100) gives radius 50.
        hex_geom = G.polygon(n_sides=6, center=(100, 100, 0), scale=100)

        layers = [hex_geom]

        # Draw roads if center is ROAD or any side is ROAD
        if t_data['center'] == ROAD:
            for i, side in enumerate(t_data['sides']):
                if side == ROAD:
                    angle_deg = i * 60
                    # Connect (100, 100) to edge.
                    # Use anchor='left' so center is start point.
                    road_seg = G.line(center=(100, 100, 0), anchor='left', length=50, angle=angle_deg)
                    layers.append(road_seg)
        elif ROAD in t_data['sides']:
            road_sides = [i for i, s in enumerate(t_data['sides']) if s == ROAD]
            if len(road_sides) == 2:
                # This is a bit complex with G.line because it needs center/angle/length.
                # Let's just use two lines from center if it's easier, but center is not ROAD.
                # For now, let's just connect them via center for simplicity in this version.
                for i in road_sides:
                    angle_deg = i * 60
                    road_seg = G.line(center=(100, 100, 0), anchor='left', length=50, angle=angle_deg)
                    layers.append(road_seg)

        # If it's a city, maybe draw some arcs or smaller polygons
        if t_data['center'] == CITY:
            # Draw a smaller hex inside or something to indicate city
            city_geom = G.polygon(n_sides=6, center=(100, 100, 0), scale=80)
            layers.append(city_geom)
        else:
            for i, side in enumerate(t_data['sides']):
                if side == CITY:
                    # Draw a small polygon near the side
                    angle = math.radians(i * 60)
                    cx = 100 + 40 * math.cos(angle)
                    cy = 100 + 40 * math.sin(angle)
                    city_part = G.polygon(n_sides=3, center=(cx, cy, 0), scale=20)
                    layers.append(city_part)

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
