from app.anki_connect import get_note_ids, get_notes_data, update_note_fields
from app.utils import get_words_and_note_ids, get_word_base_form, save_file
from app.models import Note
from time import time
from app.fetcher import fetch_word_data
import os
from dotenv import load_dotenv

#? Manually changed the note type from the old one to the new in anki app, cause ankiconnect doesn't have the option to do that (or I haven't found it)
#? Only brought the german words from the old note, left the rest (including translation blank)
#? Here I stadardize the words, put them through fetcher to get all the new fields, and put them into the old notes (in order to keep the due dates)

#? May be poorly optimized and bad practice, cause I reused a lot of code from create_notes.py

load_dotenv()
ANKI_COLLECTIONS_PATH = os.getenv("ANKI_COLLECTIONS_PATH")

def main():
    note_ids = get_note_ids("GermanVocab")
    notes_data = get_notes_data(note_ids)
    
    words_and_note_ids = get_words_and_note_ids(notes_data)
    
    words_requiring_manual_processing = []

    for word_and_id in words_and_note_ids:
        uncleared_word: str = word_and_id["word"] # type: ignore
        id: int = word_and_id["id"] # type: ignore

        word = get_word_base_form(uncleared_word)
        if not word:
            words_requiring_manual_processing.append(uncleared_word)
            continue

        print(f"Creating a note for the word \"{word}\" (\"{uncleared_word}\")...\n\n")
        beginning_time = time()
        
        note = fetch_word_data(word)

        finishing_time = time()
        completion_time = finishing_time-beginning_time
        print(f"Note created in {completion_time} seconds.\n\n")

        if note.audio == b"": print(1111) # type: ignore
        if note is not None and note.audio:
            save_file(note.audio_filename, note.audio, ANKI_COLLECTIONS_PATH) # pyright: ignore[reportArgumentType]
            save_file(note.image_filename, note.image, ANKI_COLLECTIONS_PATH) # pyright: ignore[reportArgumentType]
            
            fields = {
                "ID": note.id,
                "Russian": note.russian,
                "German": note.german,
                "Article": note.article,
                "Plural": note.plural,
                "POS": note.pos,
                "IPA": note.ipa,
                "Audio": note.audio_field,
                "Image": note.image_field,
                "Praeteritum": note.praeteritum,
                "Partizip": note.partizip,
                "Sentence_DE": note.german_example,
                "Sentence_RU": note.russian_example,
                "Tags": note.tags
            }

            update_note_fields(id, fields)

        else: print(f"No data on the word \"{word}\", discarding.\n\n")

    print("Words requiring manual processing:", words_requiring_manual_processing)


if (__name__ == "__main__"):
    main()