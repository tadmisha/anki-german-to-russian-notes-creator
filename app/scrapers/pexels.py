from curl_cffi import requests
from app.scrapers.constants import _headers
from bs4 import BeautifulSoup

_base_url = "https://www.pexels.com/search/%s"

def _get_image_url(word: str) -> str:
    url = _base_url % word

    r = requests.get(url, headers=_headers)
    soup = BeautifulSoup(r.text, "html.parser")

    image_el = soup.find("img")
    try: return image_el.get("src") # pyright: ignore[reportOptionalMemberAccess, reportReturnType]
    except AttributeError: raise LookupError(f"Image for the word \"{word}\" not found. (Alternative source)")

def get_image(word: str) -> bytes:
    image_url = _get_image_url(word)
    image = requests.get(image_url, headers=_headers)

    return image.content