"""Clean background removal for the TUFAN kitsune logo via rembg/U2Net."""
from PIL import Image
from rembg import remove, new_session

SRC = r"C:\Users\drgos_5ax3dfg\Desktop\fxsound-app\branding\tufan-logo-original.jpg"
DST = r"C:\Users\drgos_5ax3dfg\Desktop\fxsound-app\branding\tufan-logo.png"
PREVIEW = r"C:\Users\drgos_5ax3dfg\Desktop\fxsound-app\branding\tufan-logo-preview.jpg"

img = Image.open(SRC).convert("RGB")
session = new_session("isnet-general-use")
out = remove(img, session=session)
out.save(r"C:\Users\drgos_5ax3dfg\Desktop\fxsound-app\branding\tufan-rembg-raw.png")

# trim + square-pad
bbox = out.getbbox()
out = out.crop(bbox)
side = max(out.size)
canvas = Image.new("RGBA", (side, side), (0, 0, 0, 0))
canvas.paste(out, ((side - out.size[0]) // 2, (side - out.size[1]) // 2))
canvas.save(DST)

preview = Image.new("RGBA", canvas.size, (40, 40, 46, 255))
preview.alpha_composite(canvas)
preview.convert("RGB").resize((448, 448)).save(PREVIEW, quality=88)
print(f"saved {DST} {canvas.size} bbox was {bbox}")
