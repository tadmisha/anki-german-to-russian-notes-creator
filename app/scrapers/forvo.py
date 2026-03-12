from curl_cffi import requests
from curl_cffi.requests import RequestsError
from bs4 import BeautifulSoup as bs
from base64 import b64decode
from app.scrapers.constants import _headers


_base_url = "https://forvo.com/word/%s"

def _get_soup(url: str) -> bs:
    response = requests.get(url, headers=_headers)
    if response.status_code != 200:
        raise RequestsError(f"Request failed with status code: {response.status_code}.")

    html = response.text
    soup = bs(html, "html.parser")

    return soup


def get_audio_file_url(url: str, country_code: str = "de") -> str:
    soup = _get_soup(url)

    german_pronounciations = soup.find("ul", id="pronunciations-list-"+country_code)

    if german_pronounciations is None:
        raise ValueError(f"Word does not exist in German / no German pronounciation is available.") # ? Word exists on the website, but with no German variant
    
    audio_play_button = german_pronounciations.find("div", class_="play icon-size-xl")
    
    onclick_function = audio_play_button.get("onclick") # pyright: ignore[reportOptionalMemberAccess]
    onclick_function = onclick_function[onclick_function.find("'")+1:] # pyright: ignore[reportAttributeAccessIssue, reportOptionalMemberAccess, reportOptionalSubscript]
    onclick_function = onclick_function[:onclick_function.find("'")] # pyright: ignore[reportAttributeAccessIssue]

    audio_path_encoded = onclick_function

    audio_path = b64decode(audio_path_encoded).decode("utf-8") # pyright: ignore[reportArgumentType]
    extension = audio_path[-3:]

    audio_url = f"https://forvo.com/{extension}/{audio_path}"

    return audio_url


def get_word_pronunciation(word: str, country_code: str = "de") -> tuple[bytes, str]: # ? Returns the word's pronounciation (audio file)
    url = _base_url % word # ? The page of the specific word
    audio_url = get_audio_file_url(url, country_code)
    file_extension = audio_url[-3:]
    audio_file = requests.get(audio_url, headers=_headers).content
    return audio_file, file_extension
