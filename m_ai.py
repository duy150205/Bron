from __future__ import annotations
from cloudscraper import CloudScraper

class Craiyon:
    def __init__(self, api_token=None, model_version="c4ue22fb7kb6wlac") -> None:
        self.BASE_URL = "https://api.craiyon.com"
        self.DRAW_API_ENDPOINT = "/v3"
        self.model_version = model_version
        self.api_token = api_token

    def generate(self, prompt: str, negative_prompt: str = "", model_type: str = "none"):

        url = self.BASE_URL + self.DRAW_API_ENDPOINT
        session = CloudScraper()
        resp = session.post(url, json={'prompt': prompt, "negative_prompt": negative_prompt, "model": model_type, "token": self.api_token, "version": self.model_version})
        if str(resp) == '<Response [403]>':
            return 403
        if str(resp) == '<Response [524]>':
            return 524
        resp = resp.json()

        images = [f"https://img.craiyon.com/{item}" for item in resp['images']]

        return images

import discord
from PIL import Image
from io import BytesIO
import requests

def decode(links):
    if links == 403:
        return 403
    if links == 524:
        return 524
    files = []
    for img in links:
        response = requests.get(img)
        image = Image.open(BytesIO(response.content))
        bytes = BytesIO()
        image.save(bytes, format='PNG')
        bytes.seek(0)
        file = discord.File(bytes, filename='image.png')
        files.append(file)
    return files

def image_generate(prompt: str):
    generator = Craiyon()
    result = generator.generate(prompt)
    return decode(result)

def image_art_generate(prompt: str):
    generator = Craiyon()
    result = generator.generate(prompt, model_type='art')
    return decode(result)

def image_drawing_generate(prompt: str):
    generator = Craiyon()
    result = generator.generate(prompt, model_type='drawing')
    return decode(result)

def image_photo_generate(prompt: str):
    generator = Craiyon()
    result = generator.generate(prompt, model_type='photo')
    return decode(result)
