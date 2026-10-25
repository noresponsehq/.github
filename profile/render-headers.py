# /// script
# requires-python = ">=3.10"
# dependencies = ["pillow==11.3.0", "fonttools[woff]==4.60.1", "resvg-py==0.2.4"]
# ///
"""Render the GitHub headers from the website's own artwork and lettering.

uv run profile/render-headers.py /path/to/noresponse/apps/website
"""
import argparse
import io
from pathlib import Path

from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import instantiateVariableFont
from PIL import Image, ImageDraw, ImageFont
import resvg_py


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("website", type=Path)
    args = parser.parse_args()
    website = args.website.resolve()
    output = Path(__file__).resolve().parent
    cream, night = "#f2f0e6", "#0e1038"
    font = TTFont(website / "src/assets/fonts/IBMPlexSans-Variable.woff2")
    font = instantiateVariableFont(font, {"wght": 500}, inplace=True)
    font.flavor = None
    font_bytes = io.BytesIO()
    font.save(font_bytes)

    def face(size):
        return ImageFont.truetype(io.BytesIO(font_bytes.getvalue()), size)

    field = Image.open(website / "public/assets/field-hero.webp").convert("RGB")
    symbol_svg = (website / "public/assets/symbol-white.svg").read_text().replace("#FFFFFF", cream)

    def brand(canvas, x, y, size):
        symbol = Image.open(io.BytesIO(resvg_py.svg_to_bytes(svg_string=symbol_svg, width=size, height=size))).convert("RGBA")
        canvas.paste(symbol, (x, y + 5), symbol)
        ImageDraw.Draw(canvas).text((x + size + 20, y), "NoResponse", font=face(size), fill=cream)

    # Keep the reading area clear. The pixel field is the website asset,
    # drawn at its original pixel scale rather than blurred or stretched.
    def field_on(canvas, crop, position):
        artwork = field.crop(crop)
        mask = Image.new("L", artwork.size, 255)
        edge = ImageDraw.Draw(mask)
        for x in range(160):
            edge.line((x, 0, x, artwork.height), fill=round(x * 255 / 159))
        canvas.paste(artwork, position, mask)

    sdk = Image.new("RGB", (1600, 280), night)
    field_on(sdk, (700, 250, 1440, 530), (860, 0))
    brand(sdk, 64, 52, 64)
    ImageDraw.Draw(sdk).text((64, 158), "Identity Intelligence", font=face(38), fill="#bcbfe2")
    sdk.save(output / "sdk-header.png", optimize=True)

    banner = Image.new("RGB", (1600, 520), night)
    field_on(banner, (620, 220, 1440, 740), (780, 0))
    brand(banner, 64, 45, 44)
    draw = ImageDraw.Draw(banner)
    draw.text((64, 176), "Find the abuse", font=face(84), fill=cream)
    draw.text((64, 270), "in your API.", font=face(84), fill=cream)
    banner.save(output / "banner.png", optimize=True)


if __name__ == "__main__":
    main()
