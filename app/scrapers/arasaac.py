from curl_cffi import requests
from bs4 import BeautifulSoup as bs
import json
from app.scrapers.constants import _headers

_base_url = "https://api.arasaac.org/api/pictograms/%s/search/%s"
_base_image_page_url = "https://arasaac.org/pictograms/%s/%s"
_base_image_url = "https://api.arasaac.org/api/pictograms/%s"

_api_response = None
_image_id = None
_current_word = None


def _update_api_response(word: str, language: str = "de"):
    global _image_id, _current_word, _api_response

    if _current_word != word: 
        api_url = _base_url % (language, word)
        _current_word = word
        _api_response = _get_first_match_api_response(api_url)
        _image_id = _api_response["_id"]


def _get_first_match_api_response(api_url: str) -> int:
    images = json.loads(requests.get(api_url).text)
    if not images:
        raise ValueError(f"Word does not exist in German / no image (pictorgram) is available for it.")

    return images[0]


def get_tags(word: str) -> list["tags"]:
    _update_api_response(word)

    tags = _api_response["tags"]

    return tags


def get_image(word: str, language: str = "de") -> bytes:
    _update_api_response(word, language)
    
    image_url = _base_image_url % (_image_id)
    image = requests.get(image_url, headers=_headers).content

    return image