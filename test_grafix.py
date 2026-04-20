import os
from grafix import G, E
from grafix.api import Export

def draw_hex(t: float):
    # Create a hexagon
    geometry = G.polygon(n=6, r=50)
    return geometry

if __name__ == "__main__":
    os.makedirs("output", exist_ok=True)
    export = Export(draw_hex, t=0.0, fmt="svg", path="output/hex.svg", canvas_size=(200, 200))
    # It seems Export constructor might already perform the save based on 'fmt' and 'path'
    print("Export initialized, checking file...")
    if os.path.exists("output/hex.svg"):
        print("File exists!")
