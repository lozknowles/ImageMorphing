
from pathlib import Path

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "ImageMorphing_App_Summary.pdf"

PAGE_W = 612
PAGE_H = 792
LEFT_X = 44
RIGHT_X = 320
TOP_Y = 742
BOTTOM_Y = 42
COL_W = 248

content = []
fonts = []
objects = []

def esc(text: str) -> str:
    return text.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")


def wrap(text: str, width: int):
    words = text.split()
    lines = []
    current = ""
    for word in words:
        trial = word if not current else current + " " + word
        if len(trial) <= width:
            current = trial
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def add(cmd: str):
    content.append(cmd)


def rect(x, y, w, h, fill_rgb=None, stroke_rgb=None, line_width=1):
    if fill_rgb:
        add(f"{fill_rgb[0]:.3f} {fill_rgb[1]:.3f} {fill_rgb[2]:.3f} rg")
    if stroke_rgb:
        add(f"{stroke_rgb[0]:.3f} {stroke_rgb[1]:.3f} {stroke_rgb[2]:.3f} RG")
        add(f"{line_width} w")
    op = "B" if fill_rgb and stroke_rgb else "f" if fill_rgb else "S"
    add(f"{x} {y} {w} {h} re {op}")


def text(x, y, value, size=10, font="F1", rgb=(0.12, 0.16, 0.22)):
    add("BT")
    add(f"/{font} {size} Tf")
    add(f"{rgb[0]:.3f} {rgb[1]:.3f} {rgb[2]:.3f} rg")
    add(f"1 0 0 1 {x} {y} Tm")
    add(f"({esc(value)}) Tj")
    add("ET")


def section(x, y, title, items, width_chars, body_size=9.5, lead=12.2, title_rgb=(0.06, 0.46, 0.43)):
    text(x, y, title, size=12, font="F2", rgb=title_rgb)
    y -= 18
    for item in items:
        if item[:3] in {"1. ", "2. ", "3. "}:
            wrapped = wrap(item, width_chars)
            first_prefix = ""
            next_prefix = "   "
        else:
            wrapped = wrap(item, width_chars - 2)
            first_prefix = "? "
            next_prefix = "  "
        for idx, line in enumerate(wrapped):
            prefix = first_prefix if idx == 0 else next_prefix
            text(x, y, prefix + line, size=body_size)
            y -= lead
        y -= 5
    return y

# Background and header
rect(0, 0, PAGE_W, PAGE_H, fill_rgb=(0.973, 0.980, 0.988))
rect(36, 730, 540, 42, fill_rgb=(0.059, 0.463, 0.431))
text(52, 748, "ImageMorphing App Summary", size=20, font="F2", rgb=(1, 1, 1))
text(52, 734, "Based only on evidence found in this repository", size=9, font="F1", rgb=(0.82, 0.98, 0.90))

# Column cards
rect(36, 48, 256, 668, fill_rgb=(1, 1, 1), stroke_rgb=(0.86, 0.89, 0.92))
rect(312, 48, 264, 668, fill_rgb=(1, 1, 1), stroke_rgb=(0.86, 0.89, 0.92))

left_sections = [
    ("What It Is", [
        "A local Python image-morphing tool that lets a user manually pick matching control points across two images, then generates blended transition frames.",
        "The main script also exports an animated GIF and, when ffmpeg is available, an MP4 of the morph sequence.",
    ]),
    ("Who It's For", [
        "Primary user: a local Python user who wants to manually align and morph two related images into transition media.",
    ]),
    ("What It Does", [
        "Loads base and surrogate images from CLI arguments.",
        "Shows both images side by side in a Matplotlib desktop UI.",
        "Collects alternating matching points with numbering and reset support.",
        "Computes affine alignment from at least 3 point pairs.",
        "Blends aligned foreground with the base image across configurable frames.",
        "Applies a sepia-style background effect during the transition.",
        "Writes JPG frames plus GIF output and optional MP4 output.",
    ]),
    ("How To Run", [
        "1. Install Python 3 and the packages implied by imports: opencv-python, numpy, matplotlib, imageio. ffmpeg is also needed for MP4 output. Exact install command: Not found in repo.",
        "2. Run: python image_morpher.py --base_image before.jpg --surrogate_image after.jpg --output_folder morph_output",
        "3. In the UI, click corresponding points on the left and right images alternately (3+ pairs), then click Process.",
    ]),
]

right_sections = [
    ("How It Works", [
        "App shape: local desktop scripts; no backend service, API, database, or deployment config found in repo.",
        "Entry flow: image_morpher.py parses CLI args, loads images with OpenCV, resizes mismatched images to a common minimum size, and converts them for display.",
        "Interaction layer: Matplotlib with TkAgg renders two image panes and Process/Clear Points buttons; click events populate paired control-point arrays.",
        "Morph pipeline: OpenCV estimateAffine2D computes alignment, warpAffine applies it, then contour/mask logic crops the valid aligned region.",
        "Frame generation: each frame uses addWeighted for foreground blending plus a sepia-adjusted base background; frames are saved as JPGs in the output folder.",
        "Media export: imageio builds GIFs and a subprocess ffmpeg call attempts MP4 creation.",
        "Supporting scripts: resize.py provides manual drag/scroll overlay adjustment and save; affine.py, affine2.py, morph.py, and keypointmorph.py are experimental variants; collage.py assembles GIF collages.",
    ]),
    ("Repo Gaps", [
        "README: Not found in repo.",
        "requirements.txt or package manifest: Not found in repo.",
        "Automated tests: Not found in repo.",
        "Named target platform or packaged distribution: Not found in repo.",
    ]),
]

left_y = TOP_Y - 24
for title, items in left_sections:
    left_y = section(48, left_y, title, items, width_chars=47, body_size=9.4, lead=11.6, title_rgb=(0.059, 0.463, 0.431))

right_y = TOP_Y - 24
for title, items in right_sections:
    right_y = section(324, right_y, title, items, width_chars=48, body_size=9.0, lead=11.1, title_rgb=(0.114, 0.306, 0.851))

text(94, 28, str(OUT), size=8, rgb=(0.42, 0.45, 0.50))

stream = "\n".join(content).encode("latin-1", "replace")

obj1 = b"<< /Type /Catalog /Pages 2 0 R >>"
obj2 = b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>"
obj3 = f"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 {PAGE_W} {PAGE_H}] /Resources << /Font << /F1 5 0 R /F2 6 0 R >> >> /Contents 4 0 R >>".encode("latin-1")
obj4 = f"<< /Length {len(stream)} >>\nstream\n".encode("latin-1") + stream + b"\nendstream"
obj5 = b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>"
obj6 = b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica-Bold >>"
objs = [obj1, obj2, obj3, obj4, obj5, obj6]

pdf = bytearray(b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n")
offsets = [0]
for i, obj in enumerate(objs, start=1):
    offsets.append(len(pdf))
    pdf.extend(f"{i} 0 obj\n".encode("latin-1"))
    pdf.extend(obj)
    pdf.extend(b"\nendobj\n")

xref_pos = len(pdf)
pdf.extend(f"xref\n0 {len(objs) + 1}\n".encode("latin-1"))
pdf.extend(b"0000000000 65535 f \n")
for off in offsets[1:]:
    pdf.extend(f"{off:010d} 00000 n \n".encode("latin-1"))
pdf.extend(f"trailer\n<< /Size {len(objs) + 1} /Root 1 0 R >>\nstartxref\n{xref_pos}\n%%EOF\n".encode("latin-1"))

OUT.write_bytes(pdf)
print(OUT)
