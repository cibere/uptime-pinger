from .base import BaseException

class UnknownConfigFormat(BaseException):
    def __init__(self, old):
        super().__init__(_type="UnknownConfigFormat", message="Your configuration file's format is unknown.")
        self.old = old