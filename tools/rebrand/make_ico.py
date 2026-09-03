"""Assemble a multi-size .ico from the favicon PNG frames."""

import os
import sys

from PIL import Image

scratch = os.environ["SCRATCH"]
out = sys.argv[1]
sizes = [16, 32, 48, 64, 128, 256]
frames = [
    Image.open(os.path.join(scratch, f"favicon-{s}.png")).convert("RGBA") for s in sizes
]
frames[-1].save(
    out, format="ICO", sizes=[(s, s) for s in sizes], append_images=frames[:-1]
)
print("wrote", out, os.path.getsize(out), "bytes")
