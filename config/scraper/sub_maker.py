import io
import textwrap
from pathlib import Path
from zipfile import ZipFile

from django.core.files.temp import NamedTemporaryFile
from django.http import FileResponse
from PIL import Image, ImageDraw, ImageFont

BASE_DIR = Path(__file__).parent
FONT_BASE = Path(__file__).parent.joinpath('library/fonts/')
FONT_SIZE = 100
BACKGROUND_IMAGE = BASE_DIR.joinpath('pottery.jpg')


class MakeSub:
    def __init__(self, submissions):
        self.submissions = submissions

        # make text image
        self.otf_bold_path = FONT_BASE.joinpath(
            'TmoneyRoundWindExtraBold.otf')
        self.otf_bold_font = ImageFont.truetype(
            self.otf_bold_path.as_posix(), FONT_SIZE)

    def file_name(self, idx, sub_id):
        return f"{sub_id}_sub_{str(idx).zfill(3)}"

    def make_sub(self, idx, line, sub_id):

        # make background image
        bg_image = Image.open(BACKGROUND_IMAGE)
        bg_image = bg_image.convert('RGBA')

        # resize the bg image to 1920
        width, height = bg_image.size
        height_ratio = height / width
        width, height = 1920, 1920 * height_ratio
        bg_image = bg_image.resize((width, int(height)))

        # set textbox height    
        top_margin = 680
        height = 1080 - top_margin

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

    def make_tmp_sub(self):

        tmp_sub = list()

        for sub in self.submissions:

            lines = sub.dub_text.split('\n')

            for idx, line in enumerate(lines):
                if len(line.strip()) != 0:
                    tfile = self.make_sub(idx, line, sub.sub_id)
                    tmp_sub.append(tfile)

        return tmp_sub

    def make_zip(self, tmp_files):
        with NamedTemporaryFile(
            prefix='sub_download', suffix='.zip'
            ) as zf_file:

            with ZipFile(zf_file, 'w') as myzip:
                for tfile in tmp_files:
                    myzip.write(tfile.name)
                    tfile.close()

            response = FileResponse(
                open(zf_file.name, 'rb'), 
                as_attachment=True
                )

            response['Content-Disposition'] = f"attachment; filename={zf_file.name}"

        return response

    def get_zip(self):
        tmp_files = self.make_tmp_sub()
        zip_response = self.make_zip(tmp_files)

        return zip_response
