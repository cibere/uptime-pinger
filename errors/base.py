class BaseException(Exception):
    def __init__(self, _type: str, message: str):
        self.msg = f"{_type}: {message}"
        self.type = _type
        super().__init__(self.msg)