import io
import textwrap
from pathlib import Path
from zipfile import ZipFile

from django.core.files.temp import NamedTemporaryFile
from django.http import FileResponse
from PIL import Image, ImageDraw, ImageFont

from .zip import get_zip


BASE_DIR = Path(__file__).parent
FONT_BASE = Path(__file__).parent.joinpath('library/fonts/')
FONT_FILE = FONT_BASE.joinpath('TmoneyRoundWindExtraBold.otf')
FONT_SIZE = 90

BACKGROUND_IMAGE = BASE_DIR.joinpath('pottery.jpg')


class MakeSubImageFiles:
    def __init__(self, submissions):
        self.submissions = submissions

        # make text image
        self.otf_bold_font = ImageFont.truetype(
            FONT_FILE.as_posix(), 
            FONT_SIZE
            )

    def file_name(self, idx, sub_id):
        return f"{sub_id}_sub_{str(idx).zfill(3)}"

    def make_subtitles(self, idx, line, sub_id):

        # make background image
        bg_image = Image.open(BACKGROUND_IMAGE)
        bg_image = bg_image.convert('RGBA')

        # resize the bg image to 1920
        width, height = bg_image.size
        height_ratio = height / width
        width, height = 1920, 1920 * height_ratio
        bg_image = bg_image.resize((width, int(height)))

        # set textbox height    
        top_margin = 780
        height = bg_image.size[1] - top_margin

        # make textbox
        textbox = Image.new("RGBA", (1920, height), (0, 0, 0, 215))
        draw = ImageDraw.Draw(textbox)

        # tetxbox top y padding
        y_loc = 10

        # write text
        for subline in textwrap.wrap(line, width=20):     
            draw.text((100, y_loc), subline, font=self.otf_bold_font)
            y_loc += self.otf_bold_font.getsize(subline)[1]

        # paste the textbox on top of the bg_image
        bg_image.paste(textbox, (0, top_margin), mask=textbox)
        output = io.BytesIO()
        bg_image.save(output, format='png')
        hex_data = output.getvalue()

        tfile = NamedTemporaryFile(
                suffix='.png', 
                prefix=self.file_name(idx, sub_id),
                )
        tfile.write(hex_data)

        return tfile

    def make_tmp_subtitles(self):

        temporary_subtitles = list()

        for sub in self.submissions:

            lines = sub.dub_text.split('\n')

            for idx, line in enumerate(lines):
                if line.strip():
                    tfile = self.make_subtitles(idx, line, sub.sub_id)
                    temporary_subtitles.append(tfile)

        return temporary_subtitles

    def return_zip(self):
        tmp_files = self.make_tmp_subtitles()
        kwargs = {
            "prefix": "sub_download",
            "suffix": ".zip",
        }
        return get_zip(tmp_files, **kwargs)
