from app.scrapers.forvo import get_word_pronunciation
from app.scrapers.pons import get_translation, get_pos, get_plural, get_phonetics, get_article, get_verb_past_tenses
from app.scrapers.arasaac import get_image, get_tags
from app.generator import generate_example_with_translation, choose_most_suitable_tags
from app.utils import generate_id, generate_csv_from_notes
from app.models import Note
from curl_cffi.requests.exceptions import RequestException
from time import time, sleep
import argparse
import os
from dotenv import load_dotenv

#! This creates notes from a given list of words

def fetch_word_data(word: str):
    print(f"Creating a note for the word \"{word}\"...\n\n")
    beginning_time = time()

    word, russian_word = get_translation(word) #? word gets reassigned to the best match in pons if spelled incorrectly

    id = generate_id()
    
    phonetics = get_phonetics(word)
    
    pos = get_pos(word)
    plural = get_plural(word) if pos=="noun" else ""
    article = get_article(word) if pos=="noun" else ""
    praeteritum, partizip = get_verb_past_tenses(word) if pos=="verb" else ("", "")
    _, english_word = get_translation(word, "english")
    image = get_image(english_word, "en")
    tags = choose_most_suitable_tags(word, pos)
    german_example, russian_example = generate_example_with_translation(word, pos, russian_word)
    pronunciation, audio_ext = get_word_pronunciation(word)

    audio_filename = f"{word}_{id}.{audio_ext}"
    image_filename = f"{word}_{id}.png"

    audio_backup_path = "app/data/media/" + audio_filename
    image_backup_path = "app/data/media/" + image_filename

    audio_anki_path = ANKI_COLLECTIONS_PATH + audio_filename
    image_anki_path = ANKI_COLLECTIONS_PATH + image_filename

    audio_field = f"[sound:{audio_filename}]"
    image_field = f"<img src=\"{image_filename}\">"

    with open(image_backup_path, "wb") as file: file.write(image)
    with open(audio_backup_path, "wb") as file: file.write(pronunciation)

    with open(image_anki_path, "wb") as file: file.write(image)
    with open(audio_anki_path, "wb") as file: file.write(pronunciation)

    note = Note(
        id=id,
        russian=russian_word,
        german=word,
        article=article,
        plural=plural,
        pos=pos,
        ipa=phonetics,
        audio_field=audio_field,
        image_field=image_field,
        german_example=german_example,
        russian_example=russian_example,
        tags=tags
    )

    finishing_time = time()
    completion_time = round(finishing_time-beginning_time, 2)
    
    print(f"\n\nNote created! {completion_time}s")
    print(f"\nid: {id}\nword: {word}\nrussian: {russian_word}\nenglish: {english_word}\npos: {pos}\nplural: {plural}\nphonetics: {phonetics}\narticle: {article}\npraeteritum: {praeteritum}\npartizip: {partizip}\ntags: {tags}\ngerman example: {german_example}\nrussian example: {russian_example}\n\n\n")


if __name__ == "__main__":
    '''parser = argparse.ArgumentParser(description="Anki cards from words creator")
    parser.add_argument("-i", "--input", type=str, required=True, help="Path to the input txt file")
    args = parser.parse_args()'''

    main()