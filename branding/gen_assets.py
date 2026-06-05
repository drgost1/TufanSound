"""Generate every TUFAN brand asset for the FxSound rebrand.

- Wordmark SVGs (Gilroy-Bold text as paths + kitsune diamond mark) x4 colors
- IconLogo SVGs (diamond mark) x2 colors
- Multi-size ICOs: icon (full logo), white/red/gray/blue tray variants (mask-only)
- fxsound.png 32 / fxsound_large.png 256
- Legacy raster wordmarks (logo-white.png, logo-red.png, FxSound Logo White.png)
"""
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont
from scipy import ndimage
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.misc.transform import Transform

BR = r"C:\Users\drgos_5ax3dfg\Desktop\fxsound-app\branding"
REPO = r"C:\Users\drgos_5ax3dfg\Desktop\fxsound-app"
IMAGES = REPO + r"\fxsound\Images"
PROJ = REPO + r"\fxsound\Project"
PROJ_ARM = REPO + r"\fxsound\ProjectARM"
FONT_PATH = REPO + r"\fxsound\Fonts\Gilroy-Bold.ttf"

# ---------------------------------------------------------------- mask-only art
full = Image.open(BR + r"\tufan-logo.png").convert("RGBA")

raw = Image.open(BR + r"\tufan-rembg-raw.png").convert("RGBA")
orig = Image.open(BR + r"\tufan-logo-original.jpg").convert("RGB")
rgb = np.asarray(orig).astype(np.int16)
ra = np.asarray(raw)[:, :, 3]
r, g, b = rgb[:, :, 0], rgb[:, :, 1], rgb[:, :, 2]
luma = 0.299 * r + 0.587 * g + 0.114 * b
a = ra > 128
dark = (luma < 50) & a
disk = lambda rad: (lambda yy, xx: (yy**2 + xx**2) <= rad**2)(*np.ogrid[-22:23, -22:23])
seeds = ndimage.binary_erosion(dark, structure=disk(22))
if seeds.any():
    hood = ndimage.binary_dilation(seeds, structure=disk(22), iterations=1) & dark
    a = a & ~hood
a = ndimage.binary_fill_holes(a)
lbl, n = ndimage.label(a)
sizes = ndimage.sum(a, lbl, range(1, n + 1))
a = np.isin(lbl, [i + 1 for i, s in enumerate(sizes) if s > 2500])
alpha_u8 = np.asarray(Image.fromarray((a * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(1.0)))
mask_only = np.dstack([rgb.clip(0, 255).astype(np.uint8), alpha_u8])
mask_img = Image.fromarray(mask_only, "RGBA")
bbox = mask_img.getbbox()
mask_img = mask_img.crop(bbox)
side = max(mask_img.size)
canvas = Image.new("RGBA", (side, side), (0, 0, 0, 0))
canvas.paste(mask_img, ((side - mask_img.size[0]) // 2, (side - mask_img.size[1]) // 2))
mask_img = canvas
mask_img.save(BR + r"\tufan-mask.png")

# ------------------------------------------------------------------ recoloring
def recolor(img, mode):
    px = np.asarray(img).astype(np.int16).copy()
    rr, gg, bb, aa = px[:, :, 0], px[:, :, 1], px[:, :, 2], px[:, :, 3]
    red_dom = (rr > gg + 40) & (rr > bb + 40)
    if mode == "white":
        px[red_dom, 0:3] = 255
    elif mode == "blue":  # theme blue #23B6EB
        px[red_dom, 0] = 0x23; px[red_dom, 1] = 0xB6; px[red_dom, 2] = 0xEB
    elif mode == "gray":
        lum = (0.299 * rr + 0.587 * gg + 0.114 * bb).clip(0, 255)
        lum = (lum * 0.75).astype(np.int16)  # dimmed
        px[:, :, 0] = lum; px[:, :, 1] = lum; px[:, :, 2] = lum
        px[:, :, 3] = aa
    return Image.fromarray(px.clip(0, 255).astype(np.uint8), "RGBA")

ICO_SIZES = [16, 24, 32, 48, 64, 128, 256]

def save_ico(img, path):
    frames = [img.resize((s, s), Image.LANCZOS) for s in ICO_SIZES]
    frames[-1].save(path, format="ICO", append_images=frames[:-1],
                    sizes=[(s, s) for s in ICO_SIZES])

for proj in (PROJ, PROJ_ARM):
    save_ico(full, proj + r"\icon.ico")
    # idle ("white") stays full-color so the brand shows; gray = powered off
    save_ico(mask_img, proj + r"\white_logo.ico")
    save_ico(mask_img, proj + r"\red_logo.ico")
    save_ico(recolor(mask_img, "gray"), proj + r"\gray_logo.ico")
    save_ico(recolor(mask_img, "blue"), proj + r"\blue_logo.ico")

full.resize((256, 256), Image.LANCZOS).save(IMAGES + r"\fxsound_large.png")
full.resize((32, 32), Image.LANCZOS).save(IMAGES + r"\fxsound.png")

# ------------------------------------------------------- diamond mark (vector)
def diamond(cx, cy, hw, hh):
    return f"M{cx} {cy - hh}L{cx + hw} {cy}L{cx} {cy + hh}L{cx - hw} {cy}Z"

def mark_path(cx, cy, hw, hh):
    # frame (outer minus inner via even-odd) + solid center diamond
    return (diamond(cx, cy, hw, hh)
            + diamond(cx, cy, hw * 0.62, hh * 0.62)
            + diamond(cx, cy, hw * 0.34, hh * 0.34))

# ------------------------------------------------------ wordmark text -> paths
font = TTFont(FONT_PATH)
glyph_set = font.getGlyphSet()
cmap = font.getBestCmap()
upem = font["head"].unitsPerEm
cap_height = getattr(font["OS/2"], "sCapHeight", 0) or int(upem * 0.7)

CAP_PX = 64.0                      # letter height in viewBox units
BASELINE = 70.0                    # baseline y in viewBox
scale = CAP_PX / cap_height
TRACK = CAP_PX * 0.10              # letter spacing
TEXT_X = 112.0

def text_paths(text, x0):
    paths, x = [], x0
    for ch in text:
        gname = cmap[ord(ch)]
        spen = SVGPathPen(glyph_set)
        tpen = TransformPen(spen, Transform(scale, 0, 0, -scale, x, BASELINE))
        glyph_set[gname].draw(tpen)
        d = spen.getCommands()
        if d:
            paths.append(d)
        x += glyph_set[gname].width * scale + TRACK
    return paths, x - TRACK

word_paths, text_end = text_paths("TUFAN", TEXT_X)
VB_W = round(text_end + 8, 2)
VB_H = 75.15

def wordmark_svg(text_color, mark_color):
    d_mark = mark_path(48, 37.5, 40, 34)
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {VB_W} {VB_H}">',
             f'<path fill="{mark_color}" fill-rule="evenodd" d="{d_mark}"/>']
    parts += [f'<path fill="{text_color}" d="{d}"/>' for d in word_paths]
    parts.append('</svg>')
    return ''.join(parts)

# default logos carry the brand-red diamond mark; highlighted variants go full accent
for name, text_color, mark_color in [("logo-white.svg", "#fff", "#e63462"),
                                     ("logo-black.svg", "#000", "#e63462"),
                                     ("logo-red.svg", "#e63462", "#e63462"),
                                     ("logo-blue.svg", "#23B6EB", "#23B6EB")]:
    with open(IMAGES + "\\" + name, "w", encoding="utf-8") as f:
        f.write(wordmark_svg(text_color, mark_color))

def bars_svg(color):
    d = mark_path(149.9, 109.6, 105, 95)
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 299.83 219.26">'
            f'<path fill="{color}" fill-rule="evenodd" d="{d}"/></svg>')

# IconLogo: brand-red accent in both theme modes
with open(IMAGES + r"\FxSound White Bars.svg", "w", encoding="utf-8") as f:
    f.write(bars_svg("#e63462"))
with open(IMAGES + r"\FxSound Black Bars.svg", "w", encoding="utf-8") as f:
    f.write(bars_svg("#e63462"))

# ------------------------------------------------- legacy raster wordmark PNGs
def raster_wordmark(w, h, color):
    S = 8  # supersample
    W, H = w * S, h * S
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    # scale the same geometry used in the SVG
    sc = (h * S) / VB_H
    def dpoly(cx, cy, hw, hh, fill):
        draw.polygon([(cx, cy - hh), (cx + hw, cy), (cx, cy + hh), (cx - hw, cy)], fill=fill)
    cx, cy = 48 * sc, 37.5 * sc
    dpoly(cx, cy, 40 * sc, 34 * sc, color)
    dpoly(cx, cy, 40 * 0.62 * sc, 34 * 0.62 * sc, (0, 0, 0, 0))
    dpoly(cx, cy, 40 * 0.34 * sc, 34 * 0.34 * sc, color)
    pil_font = ImageFont.truetype(FONT_PATH, int(CAP_PX * sc * upem / cap_height * 0.72))
    # place text: PIL baseline handling via anchor 'ls' (left, baseline)
    x = TEXT_X * sc
    for ch in "TUFAN":
        draw.text((x, BASELINE * sc), ch, font=pil_font, fill=color, anchor="ls")
        x += draw.textlength(ch, font=pil_font) + TRACK * sc
    return img.resize((w, h), Image.LANCZOS)

raster_wordmark(266, 40, (255, 255, 255, 255)).save(IMAGES + r"\logo-white.png")
raster_wordmark(266, 40, (230, 52, 98, 255)).save(IMAGES + r"\logo-red.png")
raster_wordmark(701, 101, (255, 255, 255, 255)).save(IMAGES + r"\FxSound Logo White.png")

print(f"done. wordmark viewBox: 0 0 {VB_W} {VB_H}; text ends {text_end:.1f}")
print("ICOs written to Project, ProjectARM, Installer/Resources")
