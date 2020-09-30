import os
import sys
import urllib.request
from decouple import Csv, config
from pathlib import Path

from django.core.files.temp import NamedTemporaryFile

from .zip import get_zip

import requests


URL = "https://naveropenapi.apigw.ntruss.com/tts-premium-plus/v1/tts"

class DubError(Exception):
    pass

class MakeDubbingAudioFiles:
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

    def make_dubbing_files(self, idx, line, sub_id):

        client_id = config("X_NCP_APIGW_API_KEY_ID")
        client_secret = config("X_NCP_APIGW_API_KEY")
        encText = line

        data = {
                "speaker": self.speaker,
                "volume": self.volume,
                "speed": self.speed,
                "pitch": self.pitch,
                "emotion": self.emotion,
                "format": self.format,
                "text": encText.encode('utf-8')
            }
        
        headers = {
            "X-NCP-APIGW-API-KEY-ID": client_id,
            "X-NCP-APIGW-API-KEY": client_secret,
        }

        response = requests.post(URL, data=data, headers=headers)

        if response.status_code == 200:
            
            tfile = NamedTemporaryFile(
                suffix='.mp3', 
                prefix=self.file_name(idx, self.speaker, sub_id),
                )

            tfile.write(response.content)

        else:
            raise DubError

        return tfile

    def make_tmp_dubbing_files(self):

        tmp_dub = list()
        
        for sub in self.submissions:

            lines = sub.dub_text.split('\n')
            
            for idx, line in enumerate(lines):
                if len(line.strip()) != 0:
                    tfile = self.make_dubbing_files(idx, line, sub.sub_id)
                    tmp_dub.append(tfile)

        return tmp_dub

    def return_zip(self):
        tmp_files = self.make_tmp_dubbing_files()
        kwargs = {
            "prefix": "dub_download",
            "suffix": ".zip",
        }
        return get_zip(tmp_files, **kwargs)