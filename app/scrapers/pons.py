from curl_cffi import requests
from curl_cffi.requests import RequestsError
from bs4 import BeautifulSoup as bs
from app.utils import conjugate_regular_verb
from app.scrapers.constants import _headers

_base_url = "https://en.pons.com/text-translation/german-%s?q=%s"

_soup = None
_current_word = None
_current_lang = None

_genus_to_article = {"masculine": "der", "feminine": "die", "neuter": "das"}

def _get_soup(url: str) -> bs:
    response = requests.get(url, headers=_headers)
    if response.status_code != 200:
        raise RequestsError(f"Request failed with status code: {response.status_code}.")

    html = response.text

    soup = bs(html, "html.parser")
    return soup


def _update_soup(word: str, language: str = "russian"):
    global _current_word, _current_lang, _soup
    
    if _current_word != word or _current_lang != language: 
        url = _base_url % (language, word)
        _current_word = word
        _current_lang = language
        _soup = _get_soup(url)


#^ Noun exclusives

def get_article(word: str) -> str:
    _update_soup(word)
    soup = _soup

    try: genus = soup.find("span", class_="genus").find("acronym").get("title") # pyright: ignore[reportOptionalMemberAccess]
    except AttributeError: raise LookupError(f"Genus for the word \"{word}\" not found.")

    if '(' in genus: genus = genus[:genus.find('(')] # pyright: ignore[reportOptionalSubscript, reportAttributeAccessIssue, reportOptionalMemberAccess, reportOperatorIssue]
    
    article = _genus_to_article[genus] # pyright: ignore[reportArgumentType]

    return article


def get_plural(word: str) -> str:
    _update_soup(word)
    soup = _soup

    try: flexion_text = soup.find("span", class_="flexion").text # pyright: ignore[reportOptionalMemberAccess]
    except AttributeError: raise LookupError(f"Plural for the word \"{word}\" not found.")


    if flexion_text == "<->":
        return ""

    flexion = flexion_text[1:-1].split(' ')
    plural = flexion[1] if len(flexion) != 1 else flexion[0]

    plural = word+plural[1:] if plural[0] == '-' else plural

    return plural

#^ ––––––––––––––

#^ Verb exclusives

def get_verb_past_tenses(word: str) -> tuple[str, str]:
    _update_soup(word)
    soup = _soup

    past_tenses_el = soup.find("h3", class_="bg-gray-light text-p1 max-w-full overflow-hidden px-4 py-2 text-ellipsis whitespace-nowrap").find("span", class_="info") # pyright: ignore[reportOptionalMemberAccess]

    if past_tenses_el is not None:
        past_tenses = past_tenses_el.text.split(", ")
    
    else: 
        past_tenses = conjugate_regular_verb(word)
    
    if len(past_tenses) == 1:
        past_tenses = [""]+past_tenses
        print("One past tense")

    
    return past_tenses

#^ ––––––––––––––

def get_phonetics(word: str) -> str:
    _update_soup(word)
    soup = _soup

    try: phonetics = soup.find("span", class_="phonetics").text # pyright: ignore[reportOptionalMemberAccess]
    except AttributeError: raise LookupError(f"Phonetics for the word \"{word}\" not found.")

    return phonetics


def get_pos(word: str) -> str:
    _update_soup(word)
    soup = _soup

    try: pos = soup.find("span", class_="wordclass").find("acronym").get("title") # pyright: ignore[reportOptionalMemberAccess]
    except AttributeError: raise LookupError(f"Part of speech of the word \"{word}\" not found.")

    return pos # pyright: ignore[reportReturnType]


def get_translation(word: str, lang: str = "russian") -> tuple[str, str]:
    _update_soup(word, lang)
    soup = _soup
    
    try:
        german = soup.find(lambda tag: tag.name=="div" and tag.get("data-e2e")=="translation-source").find("strong").text # pyright: ignore[reportOptionalMemberAccess]
        translated = soup.find(lambda tag: tag.name=="div" and tag.get("data-e2e")=="translation-target").find("a").text # pyright: ignore[reportOptionalMemberAccess]

    except AttributeError:
        raise LookupError(f"Translation for the word \"{word}\" not found.")

    return german, translated