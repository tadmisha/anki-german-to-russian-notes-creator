from app.scrapers.forvo import get_word_pronunciation
from app.scrapers.pons import get_translation, get_pos, get_plural, get_phonetics, get_article, get_verb_past_tenses, _update_soup as pons_update_soup
from app.scrapers.arasaac import get_image
from app.scrapers.pexels import get_image as get_image_alternative
from app.generator import generate_example_with_translation, choose_most_suitable_tags
from app.utils import generate_id, error_handling_with_retrying
from app.models import Note
from curl_cffi.requests.exceptions import RequestException, Timeout
from groq import APIConnectionError, RateLimitError, AuthenticationError
from time import sleep
import os
from dotenv import load_dotenv

load_dotenv()
ANKI_COLLECTIONS_PATH = os.getenv("ANKI_COLLECTIONS_PATH")

def fetch_word_data(word: str) -> Note | None:
    basic_exceptions = (RequestException, ValueError, LookupError, Timeout)

    id = generate_id()
    correct_word, russian_word = error_handling_with_retrying(get_translation, (word, "russian"), basic_exceptions, 4, (None, None), "translation", 1.048596*4) # type: ignore #? word gets reassigned to the best match in pons so spelling is better
    if russian_word is None: return None

    if not ('(' in correct_word or ')' in correct_word) and len(word.split()) == len(correct_word.split()): word = correct_word #? if pons' match is something like Freund -> Freund(in) and for expressions (multiple words), that are not in pons
    word = ''.join([symb for symb in word if symb != '·']) #? Deleting '·' that for some reason appears in pons if the word is the same in English and German
    phonetics = error_handling_with_retrying(get_phonetics, (word,), basic_exceptions, 2, "–", "phonetics", 1.048596/3)
    pos = error_handling_with_retrying(get_pos, (word,), basic_exceptions, 2, "–", "part of speech", 1.048596/3)
    plural = error_handling_with_retrying(get_plural, (word,), basic_exceptions, 3, "–", "plural", error_function=pons_update_soup, error_function_args=(word,)) if pos=="noun" else ""
    article = error_handling_with_retrying(get_article, (word,), basic_exceptions, 3, "–", "article", error_function=pons_update_soup, error_function_args=(word,)) if pos=="noun" else ""
    praeteritum, partizip = error_handling_with_retrying(get_verb_past_tenses, (word,), basic_exceptions, 3, ("–", "–"), "past form of verbs") if pos=="verb" else ("", "")
    _, english_word = error_handling_with_retrying(get_translation, (word, "english"), basic_exceptions, 3, ("–", "–"), "english translation")
    english_word = english_word.split()[-1] #? remove "to" for verb translations, cause it messes with the images.
    image = error_handling_with_retrying(get_image, (english_word, "en"), basic_exceptions, 3, b"", "image")
    if not image: image = error_handling_with_retrying(get_image_alternative, (english_word,), basic_exceptions, 3, b"", "image (alternative)")
    tags = error_handling_with_retrying(choose_most_suitable_tags, (word, pos), basic_exceptions+(APIConnectionError, RateLimitError), 2, "", "tags suitable for the word")
    german_example, russian_example = error_handling_with_retrying(generate_example_with_translation, (word, pos, russian_word), basic_exceptions+(APIConnectionError, RateLimitError), 2, ("",""), "example sentence")
    pronunciation, audio_ext = error_handling_with_retrying(get_word_pronunciation, (word,), basic_exceptions, 6, (b"", ".mp3"), "pronounciation", 1.048596*3, error_function=lambda: sleep(1.048596*10), error_function_attempt=4) # type: ignore

    audio_filename = f"{word}_{id}.{audio_ext}"
    image_filename = f"{word}_{id}.png"
    audio_field = f"[sound:{audio_filename}]"
    image_field = f"<img src=\"{image_filename}\">"

    note = Note(
        id=id,
        german=word,
        russian=russian_word,
        english = english_word,
        article=article, # pyright: ignore[reportArgumentType]
        plural=plural, # pyright: ignore[reportArgumentType]
        praeteritum=praeteritum,
        partizip=partizip,
        pos=pos, # type: ignore
        ipa=phonetics, # type: ignore
        audio_field=audio_field,
        image_field=image_field,
        audio_filename=audio_filename,
        image_filename=image_filename,
        german_example=german_example,
        russian_example=russian_example,
        tags=tags,
        image=image,
        audio=pronunciation
    )
    
    return note