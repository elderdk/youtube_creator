import io
import textwrap
from pathlib import Path
from zipfile import ZipFile

import requests
from django.core.files.temp import NamedTemporaryFile
from django.http import FileResponse
from PIL import Image, ImageDraw, ImageFont

from .zipper import get_zip

BASE_DIR = Path(__file__).parent
FONT_BASE = Path(__file__).parent.joinpath('library/fonts/')
FONT_FILE = FONT_BASE.joinpath('TmoneyRoundWindExtraBold.otf')
FONT_SIZE = 80

BACKGROUND_IMAGE = BASE_DIR.joinpath('pottery.jpg')
YOUTUBE_WIDTH = 1920
YOUTUBE_HEIGHT = 1080
SUBTITLE_TOP_MARGIN = 650
SUBTITLE_OPACITY = 215
TEXTWRAP_WIDTH = 25
TEXTBOX_YPADDING = 10

class MakeSubImageFiles:
    def __init__(self, submissions):
        self.submissions = submissions

        # make text image
        self.otf_bold_font = ImageFont.truetype(
            FONT_FILE.as_posix(), 
            FONT_SIZE
            )

    def file_name(self, idx, sub_id):
        return f"{sub_id}_sub_{str(idx).zfill(3)}_"

    def img_crop(self, img):
        if img.height > YOUTUBE_HEIGHT:
            delta = (img.height - YOUTUBE_HEIGHT) / 2
            left, upper = 0, delta
            right, lower = YOUTUBE_WIDTH, img.height - delta
            return img.crop((left, upper, right, lower))
        else:
            return img

    def download_image(self, link):
        if link:
            temp_bg = NamedTemporaryFile()
            bg_file = requests.get(link, stream=True)
            temp_bg.write(bg_file.content)
            return Image.open(temp_bg)
        else:
            print('new img created')
            return Image.new('RGBA', 
                            (YOUTUBE_WIDTH, YOUTUBE_HEIGHT),
                            (0, 0, 0, 0)
                            )

    def image_resize(self, img):
        width, height = img.size
        height_ratio = height / width
        width, height = YOUTUBE_WIDTH, YOUTUBE_WIDTH * height_ratio
        img = img.resize((width, int(height)))
        return img

    def image_collapse(self, bg_image, textbox):
        bg_image.paste(textbox, (0, SUBTITLE_TOP_MARGIN), mask=textbox)
        output = io.BytesIO()
        bg_image.save(output, format='png')
        hex_data = output.getvalue()
        return hex_data

    def make_textbox(self, bg_image, line):
        height = bg_image.size[1] - SUBTITLE_TOP_MARGIN
        textbox = Image.new(
            "RGBA", (YOUTUBE_WIDTH, height), (0, 0, 0, SUBTITLE_OPACITY)
            )
        draw = ImageDraw.Draw(textbox)

        # tetxbox top y padding
        y_loc = TEXTBOX_YPADDING

        # write text
        for subline in textwrap.wrap(line, width=TEXTWRAP_WIDTH):     
            draw.text((100, y_loc), subline, font=self.otf_bold_font)
            y_loc += self.otf_bold_font.getsize(subline)[1]

        return textbox
 
    def make_temporary_file(self, idx, sub_id, final_image):
        tfile = NamedTemporaryFile(
                suffix='.png', 
                prefix=self.file_name(idx, sub_id),
                )
        tfile.write(final_image)
        return tfile

    def make_subtitles(self, idx, line, sub_id, bg_image):

        # make background image
        bg_image = bg_image.convert('RGBA')

        # resize and crop
        bg_image = self.image_resize(bg_image)
        bg_image = self.img_crop(bg_image)

        # make textbox
        textbox = self.make_textbox(bg_image, line)
        
        # paste the textbox on top of the bg_image
        final_image = self.image_collapse(bg_image, textbox)

        # make a named temporary file
        tfile = self.make_temporary_file(idx, sub_id, final_image)

        return tfile

    def make_tmp_subtitles(self):

        temporary_subtitles = list()

        for sub in self.submissions:

            lines = sub.dub_text.split('\n')
            bg_image = self.download_image(sub.sub_bg_image)

            for idx, line in enumerate(lines):
                if line.strip():
                    tfile = self.make_subtitles(
                        idx, 
                        line, 
                        sub.sub_id, 
                        bg_image
                        )
                    temporary_subtitles.append(tfile)

        return temporary_subtitles

    def return_zip(self):
        tmp_files = self.make_tmp_subtitles()
        kwargs = {
            "prefix": "sub_download",
            "suffix": ".zip",
        }
        return get_zip(tmp_files, **kwargs)
