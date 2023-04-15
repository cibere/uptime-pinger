import copy
import json
from typing import Optional

import errors

from .website import Website

default_embeds = [
    {
        "title": "Uptime Alert",
        "description": "{website} is now **online**\nIt was offline for {time}",
        "color": 65292,
    },
    {
        "title": "Downtime Alert",
        "description": "{website} is now **offline**",
        "color": 16711680,
    },
]

__all__ = ("Config",)


class Config:
    websites: list[Website]
    timeout: int
    webhook_url: Optional[str]
    often: Optional[int]
    port: int
    host: str
    title: str

    def __init__(self):
        self.websites = []
        self._raw_websites = []
        self.webhook_url = None
        self.often = None
        self.timeout = 15

        self._embeds = default_embeds

    def get_embed(self, /, _type: int):
        if _type not in [0, 1]:
            raise errors.UnknownEmbedType(_type)
        return copy.copy(self._embeds[_type])

    def reload_website_cache(self):
        websites = []
        for website in self._raw_websites:
            try:
                wait = int(website["wait"])
            except (KeyError, ValueError):
                wait = int(self.often)  # type: ignore
            try:
                ignore_ssl = bool(website["ignore_ssl"])
            except (KeyError, ValueError):
                ignore_ssl = self.ignore_ssl
            try:
                links = website["links"]
            except KeyError:
                links = []
            try:
                hidden = bool(website["hidden"])
            except (KeyError, ValueError):
                hidden = False

            websites.append(
                Website(
                    name=website["name"],
                    url=website["url"],
                    wait=wait,
                    webhook_url=str(website.get("webhook_url") or self.webhook_url),
                    ignore_ssl=ignore_ssl,
                    _config=self,
                    links=links,
                    description=website.get("description", ""),
                    hidden=hidden,
                )
            )
        self.websites = websites

    def reload_config(self):
        try:
            with open("config.json", "r") as f:
                config = json.load(f)

            self._raw_websites = config["websites"]
            self.webhook_url = config["webhook_url"]
            self.often = config.get("often", 30)
            self.timeout = config.get("timeout", 15)
            self.ignore_ssl = bool(config.get("ignore_ssl", False))
            self._embeds = config.get("embed_format", default_embeds)
            self.host = config.get("host", "0.0.0.0")
            self.port = config.get("port", 443)
            self.title = config.get("title", "Uptime Checker")

        except FileNotFoundError:
            raise errors.ConfigNotFound() from None
        except (json.decoder.JSONDecodeError, KeyError):
            raise errors.UnknownConfigFormat() from None  # type: ignore
        if self._raw_websites:
            self.reload_website_cache()
