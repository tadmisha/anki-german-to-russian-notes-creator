class Note():
    def __init__(self, id: str, german: str, russian: str, english: str, article: str, plural: str, praeteritum: str, partizip: str, pos: str, ipa: str, audio_field: str, image_field: str, audio_filename: str, image_filename: str, german_example: str, russian_example: str, tags: str, image: bytes, audio: bytes):
        self.id = id
        self.russian = russian
        self.english = english
        self.german = german
        self.article = article
        self.plural = plural
        self.praeteritum = praeteritum
        self.partizip = partizip
        self.pos = pos
        self.ipa = ipa
        self.audio_field = audio_field
        self.image_field = image_field
        self.audio_filename = audio_filename
        self.image_filename = image_filename
        self.german_example = german_example
        self.russian_example = russian_example
        self.tags = tags
        self.image = image
        self.audio = audio        
