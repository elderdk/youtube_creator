import os
import sys
import urllib.request
from decouple import Csv, config
from pathlib import Path
from zipfile import ZipFile

from django.core.files.temp import NamedTemporaryFile
from django.http import FileResponse


class MakeDub:
    def __init__(self, submissions):
        self.BASE_DIR = Path(__file__).parent
        self.speaker = 'nsujin'
        self.volume = '0'
        self.speed = '2'
        self.pitch = '0'
        self.emotion = '1'
        self.format = 'mp3'
        self.submissions = submissions

    def file_name(self, idx, speaker, sub_id):
        return f"{sub_id}_dub_{str(idx).zfill(3)}_{speaker}"

    def make_dubs(self, idx, line, sub_id):

        client_id = config("X_NCP_APIGW_API_KEY_ID")
        client_secret = config("X_NCP_APIGW_API_KEY")
        encText = urllib.parse.quote(line)

        data = ''.join(
                [
                f"speaker={self.speaker}&", 
                f"volume={self.volume}&", 
                f"speed={self.speed}&", 
                f"pitch={self.pitch}&", 
                f"emotion={self.emotion}&", 
                f"format={self.format}&", 
                f"text={encText}"
                ]
            )

        url = "https://naveropenapi.apigw.ntruss.com/tts-premium-plus/v1/tts"
        
        request = urllib.request.Request(url)
        request.add_header("X-NCP-APIGW-API-KEY-ID",client_id)
        request.add_header("X-NCP-APIGW-API-KEY",client_secret)

        response = urllib.request.urlopen(
            request, data=data.encode('utf-8')
            )

        rescode = response.getcode()

        if(rescode==200):
            response_body = response.read()
            
            tfile = NamedTemporaryFile(
                suffix='.mp3', 
                prefix=self.file_name(idx, self.speaker, sub_id)
                )
            tfile.write(response_body)

        return tfile

    def make_tmp_dub(self):

        tmp_dub = list()
        
        for sub in self.submissions:

            lines = sub.dub_text.split('\n')
            
            for idx, line in enumerate(lines):
                if len(line.strip()) != 0:
                    tfile = self.make_dubs(idx, line, sub.sub_id)
                    tmp_dub.append(tfile)

        return tmp_dub

    def make_zip(self, tmp_files):
        with NamedTemporaryFile(
            prefix='dub_download', suffix='.zip'
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
        tmp_files = self.make_tmp_dub()
        zip_response = self.make_zip(tmp_files)

        return zip_response