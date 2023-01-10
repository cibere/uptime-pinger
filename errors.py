class BaseException(Exception):
    def __init__(self, _type: str, message: str):
        self.msg = f"{_type}: {message}"
        self.type = _type
        super().__init__(self.msg)


class ConfigNotFound(BaseException):
    def __init__(self):
        super().__init__(
            _type="ConfigNotFound",
            message="A configuration file was not found. Please create a 'config.json' file",
        )


class UnknownConfigFormat(BaseException):
    def __init__(self, old):
        super().__init__(
            _type="UnknownConfigFormat",
            message="Your configuration file's format is unknown.",
        )
        self.old = old


class UnknownEmbedType(BaseException):
    def __init__(self, _type):
        super().__init__(
            _type="UnknownEmbedType", message=f"Unknown Embed Type '{_type}'"
        )
        self.type = _type
