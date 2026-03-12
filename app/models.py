class Note():
    def __init__(self, id: str, german: str, russian: str, article: str, plural: str, pos: str, ipa: str, audio_field: str, image_field: bytes, german_example: str, russian_example: str, tags: list[str]):
        self.id = id
        self.russian = russian
        self.german = german
        self.article = article
        self.plural = plural
        self.pos = pos
        self.ipa = ipa
        self.audio_field = audio_field
        self.image_field = image_field
        self.german_example = german_example
        self.russian_example = russian_example
        self.tags = tags
