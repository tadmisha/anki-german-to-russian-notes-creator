class Note():
    def __init__(self, id: str, russian: str, german: str, article: str|None, plural: str|None, pos: str, ipa: str, audio: bytes, image: bytes, notes: str, tags: list[str]):
        self.id = id
        self.russian = russian
        self.german = german
        self.article = article
        self.plural = plural
        self.pos = pos
        self.ipa = ipa
        self.audio = audio
        self.image = image
        self.notes = notes
        self.tags = tags
