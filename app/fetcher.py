from app.scrapers.forvo import get_word_pronunciation
from app.scrapers.pons import get_translation, get_pos, get_plural, get_phonetics, get_article, get_verb_past_tenses
from app.scrapers.arasaac import get_image
from app.generator import generate_example_with_translation, choose_most_suitable_tags
from app.utils import generate_id, error_handling_with_retrying
from app.models import Note
from curl_cffi.requests.exceptions import RequestException
from groq import APIConnectionError, RateLimitError, AuthenticationError
from time import time, sleep
import os
from dotenv import load_dotenv

load_dotenv()
ANKI_COLLECTIONS_PATH = os.getenv("ANKI_COLLECTIONS_PATH")

def fetch_word_data(word: str) -> Note:
    #print(f"Creating a note for the word \"{word}\"...\n\n")

    id = generate_id()
    word, russian_word = get_translation(word) #? word gets reassigned to the best match in pons if spelled incorrectly

    finished_tries = 0
    phonetics = ""
    while finished_tries<3:
        try:
            phonetics = get_phonetics(word)
        except (LookupError, RequestException): 
            print(f"Couldn't fetch phonetics on try N{finished_tries+1}.")
        finished_tries+=1
        sleep(1.5)

    phonetics = error_handling_with_retrying(get_phonetics, (word,), (RequestException, ValueError), 3, "–", "phonetics")
    pos = error_handling_with_retrying(get_pos, (word,), (RequestException, ValueError), 3, "–", "part of speech")
    plural = error_handling_with_retrying(get_plural, (word,), (RequestException, ValueError), 3, "–", "plural") if pos=="noun" else ""
    article = error_handling_with_retrying(get_article, (word,), (RequestException, ValueError), 3, "–", "article") if pos=="noun" else ""
    praeteritum, partizip = error_handling_with_retrying(get_verb_past_tenses, (word,), (RequestException, ValueError), 3, ("–", "–"), "past form of verbs")
    _, english_word = error_handling_with_retrying(get_translation, (word, "english"), (RequestException, ValueError), 3, ("–", "–"), "english translation")
    image = error_handling_with_retrying(get_image, (english_word, "en"), (RequestException, ValueError), 3, b"", "image")
    tags = error_handling_with_retrying(choose_most_suitable_tags, (word, pos), (APIConnectionError, RateLimitError, RequestException, ValueError), 2, "", "tags suitable for the word")
    german_example, russian_example = error_handling_with_retrying(generate_example_with_translation, (word, pos, russian_word), (APIConnectionError, RateLimitError, RequestException, ValueError), 2, ("",""), "example sentence")
    pronunciation, audio_ext = error_handling_with_retrying(get_word_pronunciation, (word,), (RequestException, ValueError), 4, (b"", ".mp3"), "pronounciation")

    audio_filename = f"{word}_{id}.{audio_ext}"
    image_filename = f"{word}_{id}.png"
    audio_field = f"[sound:{audio_filename}]"
    image_field = f"<img src=\"{image_filename}\">"

    note = Note(
        id=id,
        german=word,
        russian=russian_word,
        article=article,
        plural=plural,
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