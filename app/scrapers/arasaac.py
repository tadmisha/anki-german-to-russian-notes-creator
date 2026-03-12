from curl_cffi import requests
from bs4 import BeautifulSoup as bs
import json
from app.scrapers.constants import _headers

_base_url = "https://api.arasaac.org/api/pictograms/%s/search/%s"
_base_image_url = "https://api.arasaac.org/api/pictograms/%s"

def _get_first_match_api_response(api_url: str) -> dict:
    images = json.loads(requests.get(api_url).text)
    if not images:
        raise ValueError(f"Word does not exist in German / no image (pictorgram) is available for it.")

    return images[0]


def get_image(word: str, language: str = "de") -> bytes:
    api_url = _base_url % (language, word)
    _image_id = _get_first_match_api_response(api_url)["_id"]
    
    image_url = _base_image_url % (_image_id)
    image = requests.get(image_url, headers=_headers).content

    return image