from app.fetcher import fetch_word_data
from app.utils import generate_csv_from_notes, save_file
from app.models import Note
from time import time
import argparse
import os
from dotenv import load_dotenv

#! This creates notes from a given list of words


load_dotenv()
ANKI_COLLECTIONS_PATH = os.getenv("ANKI_COLLECTIONS_PATH")


def main():
    words = ["verheiret", "Geburtstag", "sehen", "wie", "viele", "Einzelkind", "sympathisch"]
    
    notes: list[Note] = []

    for word in words:
        print(f"Creating a note for the word \"{word}\"...\n\n")
        beginning_time = time()
        
        note = fetch_word_data(word)

        finishing_time = time()
        completion_time = finishing_time-beginning_time
        print(f"Note created in {completion_time} seconds.")

        save_file(note.audio_filename, note.audio, ANKI_COLLECTIONS_PATH) # pyright: ignore[reportArgumentType]
        save_file(note.image_filename, note.image, ANKI_COLLECTIONS_PATH) # pyright: ignore[reportArgumentType]

        notes.append(note)

        
    
    generate_csv_from_notes(notes)


if __name__ == "__main__":
    '''parser = argparse.ArgumentParser(description="Anki cards from words creator")
    parser.add_argument("-i", "--input", type=str, required=True, help="Path to the input txt file")
    args = parser.parse_args()'''

    main()