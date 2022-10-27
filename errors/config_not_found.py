from .base import BaseException

class ConfigNotFound(BaseException):
    def __init__(self):
        super().__init__(_type="ConfigNotFound", message="A configuration file was not found. Please create a 'config.json' file")