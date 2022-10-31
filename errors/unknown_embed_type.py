from .base import BaseException

class UnknownEmbedType(BaseException):
    def __init__(self, _type):
        super().__init__(_type="UnknownEmbedType", message=f"Unknown Embed Type '{_type}'")
        self.type = _type