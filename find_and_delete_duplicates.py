from app.anki_connect import get_note_ids, get_notes_data, update_note_fields
from app.utils import get_duplicates, find_files_by_id
from dotenv import load_dotenv
import os


load_dotenv()
ANKI_COLLECTIONS_PATH = os.getenv("ANKI_COLLECTIONS_PATH")

def main():
    note_ids = get_note_ids("GermanVocab")
    notes_data = get_notes_data(note_ids)

    duplicates = get_duplicates(notes_data)
    duplicate_files = []
    for duplicate in duplicates:
        duplicate_files += find_files_by_id(duplicate["word_id"], ANKI_COLLECTIONS_PATH) # type: ignore

    print("Duplicates:\n  "+"\n  ".join([duplicate["word"] for duplicate in duplicates]))

    want_to_delete_files = input("\nDelete duplicate words files? [y/n]: ").lower()[0]
    if want_to_delete_files == 'y':
        for duplicate_file in duplicate_files:
            os.remove(duplicate_file)
    
    want_to_delete_cards = input("Delete duplicate notes? [y/n]: ").lower()[0]
    if want_to_delete_cards == 'y':
        for duplicate in duplicates:
            fields = [
                "ID",
                "Russian",
                "German",
                "Article",
                "Plural",
                "POS",
                "IPA",
                "Audio",
                "Image",
                "Praeteritum",
                "Partizip",
                "Sentence_DE",
                "Sentence_RU",
                "Tags"
            ]

            fields = {field:"_delete_" for field in fields}
            update_note_fields(duplicate["note_id"], fields)
        
        print("\nMarked every field of cards to delete as \"_delete_\"") #? AnkiConnect doesn't have a delete function


if __name__ == "__main__":
    main()
