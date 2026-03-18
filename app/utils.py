import csv
from random import choice
from time import sleep
from app.models import Note
from typing import Callable as function

_chars = [chr(i) for i in range(48,58)] + [chr(i) for i in range(65,91)] + [chr(i) for i in range(97,123)]

def generate_id(length: int = 10) -> str:
    id = ''.join([choice(_chars) for _ in range(length)])
    return id


def generate_csv_from_notes(notes: list[Note], filename: str = "notes.csv"):
    with open(filename, "w", encoding="utf-8", newline="") as file:
        writer = csv.writer(file)
        for note in notes:
            writer.writerow((note.id, note.russian, note.german, note.article, note.plural, note.pos, note.ipa, note.audio_field, note.image_field, note.praeteritum, note.partizip, note.german_example, note.russian_example, ';'.join(note.tags)))



def conjugate_regular_verb(infinitive: str) -> tuple[str, str]: #! This function is vibe-coded
    infinitive = infinitive.lower().strip()
    
    # 1. Configuration
    separable = ('auf', 'an', 'ein', 'aus', 'mit', 'vor', 'zu', 'ab', 'nach', 'her', 'hin', 'weg')
    inseparable = ('be', 'ver', 'ent', 'er', 'zer', 'ge', 'miss')

    # 2. Detect Prefixes
    found_separable = ""
    remaining = infinitive
    
    # Check for separable prefix first
    for p in separable:
        if infinitive.startswith(p):
            found_separable = p
            remaining = infinitive[len(p):]
            break

    # Check if what remains starts with an inseparable prefix (e.g., 'be' in 'vorbereiten')
    has_inseparable = any(remaining.startswith(p) for p in inseparable)
    is_ieren = infinitive.endswith("ieren")

    # 3. Extract the Stem
    # Handles -en (machen) and -n (wandeln)
    if remaining.endswith("en"):
        stem = remaining[:-2]
    elif remaining.endswith("n"):
        stem = remaining[:-1]
    else:
        stem = remaining

    # 4. Refined "e-insertion" Rule
    # Rule: Needs 'e' if stem ends in d/t OR ends in m/n preceded by a consonant (but NOT l or r)
    ends_in_dt = stem.endswith(('d', 't'))
    ends_in_mn = stem.endswith(('m', 'n'))
    
    needs_e = False
    if ends_in_dt:
        needs_e = True
    elif ends_in_mn and len(stem) > 1:
        preceding_char = stem[-2]
        # Only add 'e' if preceded by a consonant that isn't L or R
        consonants = "bcdfghjkmnpqstvwxz"  # No 'l' or 'r'
        if preceding_char in consonants:
            needs_e = True

    buffer = "e" if needs_e else ""

    # 5. Build the Forms
    # Präteritum (3rd person singular, main clause word order)
    if found_separable:
        # Separable verb: prefix goes to the end
        praeteritum = f"er {stem}{buffer}te {found_separable}"
    else:
        # Non-separable verb: simple form
        praeteritum = f"er {stem}{buffer}te"

    # Partizip II Rule:
    # If it's -ieren OR has an inseparable prefix anywhere, NO "ge-"
    if is_ieren or has_inseparable:
        partizip = f"{found_separable}{stem}{buffer}t"
    else:
        # Standard: [Separable] + "ge" + [Stem] + [Buffer] + "t"
        partizip = f"{found_separable}ge{stem}{buffer}t"

    return (praeteritum, partizip)


def save_file(filename: str, file_content: bytes, anki_path: str, backup_path: str = "app/data/media/"): # ? Saves the file in anki collections and a backup directory (app/data/media/) 
    file_path_backup = backup_path + filename
    file_path_anki = anki_path + filename

    with open(file_path_backup, "wb") as file: file.write(file_content)
    with open(file_path_anki, "wb") as file: file.write(file_content)


def error_handling_with_retrying(get_func: function, args: tuple, exceptions, max_attempts: int = 3, default_return = None, description: str = "data", sleep_time: float = 1.048596, error_function: function = lambda: None, error_function_args: tuple = (), error_function_attempt: int = 2):
    result = default_return

    for attempt in range(max_attempts):
        try:
            result = get_func(*args)
            break
        except exceptions as e:
            print(f"Couldn't fetch {description} on attempt N{attempt+1}.", type(e), end="")
            if (attempt+1) % error_function_attempt == 0: error_function(*error_function_args)
            print(" Discarding." if attempt==max_attempts-1 else "")
            sleep(sleep_time)
    
    return result


def read_words(filename: str) -> list[str]:
    with open(filename, "r", encoding="utf-8") as file:
        words = file.read().split("\n")
    
    return words