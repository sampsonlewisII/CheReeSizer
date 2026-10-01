"""Generate CheReeSizer's app icons: dark tile, amber corner brackets (the edge inspector), a magnified edge line."""
import os, sys
from PIL import Image, ImageDraw
root = sys.argv[1]; out = os.path.join(root, "src-tauri", "icons"); os.makedirs(out, exist_ok=True)
S = 1024
im = Image.new("RGBA", (S, S), (0, 0, 0, 0))
d = ImageDraw.Draw(im)
d.rounded_rectangle([40, 40, S - 40, S - 40], radius=190, fill=(17, 20, 27, 255), outline=(44, 52, 68, 255), width=14)
amber, cyan = (240, 163, 44, 255), (76, 196, 214, 255)
m, L, w = 200, 230, 56   # bracket inset, arm length, stroke width
for (cx, cy, sx, sy) in [(m, m, 1, 1), (S - m, m, -1, 1), (m, S - m, 1, -1), (S - m, S - m, -1, -1)]:
    d.rectangle(sorted([cx, cx + sx * L])[:1] + [min(cy, cy + sy * w)] + [max(cx, cx + sx * L)] + [max(cy, cy + sy * w)], fill=amber)
    d.rectangle([min(cx, cx + sx * w), min(cy, cy + sy * L), max(cx, cx + sx * w), max(cy, cy + sy * L)], fill=amber)
# the "inspected edge": a thin bright line hard against an inner rule
d.rectangle([330, 470, S - 330, 500], fill=amber)
d.rectangle([330, 540, S - 330, 556], fill=cyan)
im.save(os.path.join(out, "icon.png"))
for size, name in [(32, "32x32.png"), (128, "128x128.png"), (256, "128x128@2x.png")]:
    im.resize((size, size), Image.LANCZOS).save(os.path.join(out, name))
im.save(os.path.join(out, "icon.ico"), sizes=[(16, 16), (24, 24), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)])
print(sorted(os.listdir(out)))
