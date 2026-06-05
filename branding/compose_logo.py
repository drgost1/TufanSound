"""Reconstruct the full TUFAN logo: red square + kitsune mask, true transparency.

Strategy: rembg gave a clean mask of the fox face but kept the black bg "hood"
between the ears and dropped the red square. We rebuild:
  alpha = red_square_region  UNION  (rembg_alpha - big_dark_bg_blobs)
"""
import numpy as np
from PIL import Image, ImageFilter
from scipy import ndimage

BR = r"C:\Users\drgos_5ax3dfg\Desktop\fxsound-app\branding"
orig = np.asarray(Image.open(BR + r"\tufan-logo-original.jpg").convert("RGB")).astype(np.int16)
rembg_im = Image.open(BR + r"\tufan-rembg-raw.png").convert("RGBA")
rembg_a = np.asarray(rembg_im)[:, :, 3]

h, w, _ = orig.shape
r, g, b = orig[:, :, 0], orig[:, :, 1], orig[:, :, 2]
luma = (0.299 * r + 0.587 * g + 0.114 * b)

# --- 1. Red square region: strongly red pixels -> largest blob -> filled bbox
red = (r > 90) & (r - g > 50) & (r - b > 50)
# square edges via histograms: rows/cols belonging to the square have massive red
# counts; red details inside the mask (ears, eyes, diamond) stay below threshold
row_counts, col_counts = red.sum(axis=1), red.sum(axis=0)
row_ok = np.where(row_counts > 0.30 * row_counts.max())[0]
col_ok = np.where(col_counts > 0.30 * col_counts.max())[0]
y0, y1, x0, x1 = row_ok.min(), row_ok.max(), col_ok.min(), col_ok.max()
square = np.zeros((h, w), bool)
square[y0:y1 + 1, x0:x1 + 1] = True
print(f"red square bbox: x {x0}-{x1}, y {y0}-{y1}")

# --- 2. rembg alpha minus background "hood": large dark blobs outside the square
a = rembg_a > 128
dark = (luma < 50) & a & ~square
# erode with a disk ~22px: thin outline strokes vanish, big bg blobs survive
disk = lambda rad: (lambda yy, xx: (yy**2 + xx**2) <= rad**2)(*np.ogrid[-22:23, -22:23])
seeds = ndimage.binary_erosion(dark, structure=disk(22))
if seeds.any():
    # recover blob extent: dilate seeds back within the dark region (limited reach)
    hood = ndimage.binary_dilation(seeds, structure=disk(22), iterations=1) & dark
    lblh, nh = ndimage.label(hood)
    print(f"hood blobs removed: {nh}, px: {hood.sum()}")
    a = a & ~hood

# --- 3. final alpha: square + cleaned mask, holes filled
alpha = ndimage.binary_fill_holes(a | square)
# drop stray hairline fragments (JPEG/AI artifacts floating around the art)
lbl2, n2 = ndimage.label(alpha)
sizes2 = ndimage.sum(alpha, lbl2, range(1, n2 + 1))
keep = [i + 1 for i, s in enumerate(sizes2) if s > 2500]
alpha = np.isin(lbl2, keep)
print(f"alpha components: {n2}, kept: {len(keep)}")

# --- 4. soften edges, keep rembg's native anti-aliasing where it exists
alpha_u8 = (alpha * 255).astype(np.uint8)
soft = np.asarray(Image.fromarray(alpha_u8).filter(ImageFilter.GaussianBlur(1.2)))
# where rembg alpha was semi-transparent (edge AA) and inside our mask, prefer it
out_a = np.where((rembg_a < 250) & (rembg_a > 5) & ~square, np.minimum(soft, rembg_a), soft)

rgb = orig.clip(0, 255).astype(np.uint8)
out = np.dstack([rgb, out_a.astype(np.uint8)])
img = Image.fromarray(out, "RGBA")

# trim + square-pad with small margin
bbox = img.getbbox()
img = img.crop(bbox)
side = max(img.size)
canvas = Image.new("RGBA", (side, side), (0, 0, 0, 0))
canvas.paste(img, ((side - img.size[0]) // 2, (side - img.size[1]) // 2))
canvas.save(BR + r"\tufan-logo.png")

for bg, name in [((40, 40, 46, 255), "dark"), ((235, 235, 240, 255), "light")]:
    pv = Image.new("RGBA", canvas.size, bg)
    pv.alpha_composite(canvas)
    pv.convert("RGB").resize((448, 448)).save(BR + rf"\tufan-logo-preview-{name}.jpg", quality=88)
print(f"saved tufan-logo.png {canvas.size}, content bbox {bbox}")
