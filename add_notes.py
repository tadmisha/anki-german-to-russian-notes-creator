from app.scrapers.forvo import get_word_pronunciation
from app.scrapers.pons import get_translation, get_pos, get_plural, get_phonetics, get_article, get_verb_past_tenses
from app.scrapers.arasaac import get_image, get_tags
from app.generator import generate_example_with_translation, choose_most_suitable_tags
from app.utils import generate_id
from app.models import Note
from time import time
import argparse



def main():#file_path: str):
    with open("words.txt", 'r', encoding="utf-8") as file:
        words = file.read().split('\n')

    notes: list[Note] = []

    for word in words:
        word = "Tee"

        print(f"Creating a note for the word \"{word}\"...\n\n")
        beginning_time = time()

        id = generate_id()

        word, russian_word = get_translation(word) #? word gets reassigned to the best match in pons if spelled incorrectly

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

        finishing_time = time()

        completion_time = round(finishing_time-beginning_time, 2)
        print(f"\n\nNote created! {completion_time}s")

        with open("image.png", "wb") as file:
            file.write(image)
        
        with open("audio."+audio_ext, "wb") as file:
            file.write(pronunciation)

        print(f"id: {id}\nword: {word}\nrussian: {russian_word}\nenglish: {english_word}\npos: {pos}\nplural: {plural}\nphonetics: {phonetics}\narticle: {article}\npraeteritum: {praeteritum}\npartizip: {partizip}\ntags: {tags}\ngerman example: {german_example}\nrussian example: {russian_example}")
        quit()

if __name__ == "__main__":
    '''parser = argparse.ArgumentParser(description="Anki cards from words creator")
    parser.add_argument("-i", "--input", type=str, required=True, help="Path to the input txt file")
    args = parser.parse_args()'''

    main()