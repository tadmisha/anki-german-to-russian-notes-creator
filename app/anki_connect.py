import requests

def _anki_request(action: str, params: dict):
    response = requests.post("http://localhost:8765", json={
        "action": action,
        "params": params,
        "version": 6
    })

    return response.json()["result"]


def get_note_ids(note_type: str): 
    return _anki_request("findNotes", {"query": f"note:\"{note_type}\""})


def get_notes_data(note_ids: list[int]):
    return _anki_request("notesInfo", {"notes": note_ids})

def update_note_fields(id: int, fields: dict[str, str]):
    params = {"note": 
                {  
                    "id": id,  
                    "fields": fields
                }  
            }

    return _anki_request("updateNoteFields", params)
