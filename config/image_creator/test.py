import textwrap
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

BASE_DIR = Path(__file__).parent
FONT_BASE = Path(__file__).parent.joinpath('library/fonts/')
FONT_SIZE = 100
LINE_LIMIT = 5


with open('test_text.txt', 'r', encoding='utf-8') as f:
    lines = f.readlines()







# make text image
otf_bold_path = FONT_BASE.joinpath('TmoneyRoundWindExtraBold.otf')
otf_bold_font=ImageFont.truetype(otf_bold_path.as_posix(), FONT_SIZE)


for idx, lines in enumerate(lines):

    # make background image
    bg_image = Image.open('pottery.jpg')
    bg_image = bg_image.convert('RGBA')

    width, height = bg_image.size
    height_ratio = height / width
    width, height = 1920, 1920 * height_ratio
    bg_image = bg_image.resize((width, int(height)))

    top_margin = 680
    height = 1080 - top_margin

    image = Image.new("RGBA", (1920, height), (0, 0, 0, 215))
    draw = ImageDraw.Draw(image)

    y_loc = 10

    for subline in textwrap.wrap(lines, width=20):     
        draw.text((100, y_loc), subline, font=otf_bold_font)
        y_loc += otf_bold_font.getsize(subline)[1]

    # paste the image on top of the bg_image
    bg_image.paste(image, (0, top_margin), mask=image)
    bg_image.save(BASE_DIR.joinpath(f"output/{str(idx).zfill(4)}.png"))
