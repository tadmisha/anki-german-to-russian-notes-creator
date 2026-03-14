from app.scrapers.forvo import get_word_pronunciation
from app.scrapers.pons import get_translation, get_pos, get_plural, get_phonetics, get_article, get_verb_past_tenses, _update_soup as pons_update_soup
from app.scrapers.arasaac import get_image
from app.scrapers.pexels import get_image as get_image_alternative
from app.generator import generate_example_with_translation, choose_most_suitable_tags
from app.utils import generate_id, error_handling_with_retrying
from app.models import Note
from curl_cffi.requests.exceptions import RequestException
from groq import APIConnectionError, RateLimitError, AuthenticationError
from time import sleep
import os
from dotenv import load_dotenv

load_dotenv()
ANKI_COLLECTIONS_PATH = os.getenv("ANKI_COLLECTIONS_PATH")

def fetch_word_data(word: str) -> Note:
    id = generate_id()
    correct_word, russian_word = get_translation(word) #? word gets reassigned to the best match in pons so spelling is better
    if not ('(' in correct_word or ')' in correct_word) and len(word.split()) == len(correct_word.split()): word = correct_word #? if pons' match is something like Freund -> Freund(in) and for expressions (multiple words), that are not in pons
    word = ''.join([symb for symb in word if symb != '·']) #? Deleting '·' that for some reason appears in pons if the word is the same in English and German
    phonetics = error_handling_with_retrying(get_phonetics, (word,), (RequestException, ValueError, LookupError), 2, "–", "phonetics")
    pos = error_handling_with_retrying(get_pos, (word,), (RequestException, ValueError, LookupError), 3, "–", "part of speech")
    plural = error_handling_with_retrying(get_plural, (word,), (RequestException, ValueError, LookupError), 3, "–", "plural", error_function=pons_update_soup, error_function_args=(word,)) if pos=="noun" else ""
    article = error_handling_with_retrying(get_article, (word,), (RequestException, ValueError, LookupError), 3, "–", "article", error_function=pons_update_soup, error_function_args=(word,)) if pos=="noun" else ""
    praeteritum, partizip = error_handling_with_retrying(get_verb_past_tenses, (word,), (RequestException, ValueError, LookupError), 3, ("–", "–"), "past form of verbs") if pos=="verb" else ("", "")
    _, english_word = error_handling_with_retrying(get_translation, (word, "english"), (RequestException, ValueError, LookupError), 3, ("–", "–"), "english translation")
    image = error_handling_with_retrying(get_image, (english_word, "en"), (RequestException, ValueError, LookupError), 3, b"", "image")
    if not image: image = error_handling_with_retrying(get_image_alternative, (english_word,), (RequestException, ValueError, LookupError), 3, b"", "image (alternative)")
    tags = error_handling_with_retrying(choose_most_suitable_tags, (word, pos), (APIConnectionError, RateLimitError, RequestException, ValueError), 2, "", "tags suitable for the word")
    german_example, russian_example = error_handling_with_retrying(generate_example_with_translation, (word, pos, russian_word), (APIConnectionError, RateLimitError, RequestException, ValueError), 2, ("",""), "example sentence")
    pronunciation, audio_ext = error_handling_with_retrying(get_word_pronunciation, (word,), (RequestException, ValueError, LookupError), 6, (b"", ".mp3"), "pronounciation", 1.048596*3, error_function=lambda: sleep(1.048596*10), error_function_attempt=4) # type: ignore

    audio_filename = f"{word}_{id}.{audio_ext}"
    image_filename = f"{word}_{id}.png"
    audio_field = f"[sound:{audio_filename}]"
    image_field = f"<img src=\"{image_filename}\">"

    note = Note(
        id=id,
        german=word,
        russian=russian_word,
        article=article, # pyright: ignore[reportArgumentType]
        plural=plural, # pyright: ignore[reportArgumentType]
        praeteritum=praeteritum,
        partizip=partizip,
        pos=pos,
        ipa=phonetics,
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