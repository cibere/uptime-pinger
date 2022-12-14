import copy
import json
import logging

import errors

from .website import Website

logger = logging.getLogger("uptime")

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


class Config:
    def __init__(self):
        # {'name' : datetime.datetime obj}
        self.down = {}
        self.websites = []
        self.raw_websites = []
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
        for website in self.raw_websites:
            try:
                wait = int(website["wait"])
            except:
                wait = int(self.often)  # type: ignore
            try:
                ignore_ssl = bool(website["ignore_ssl"])
            except:
                ignore_ssl = self.ignore_ssl

            websites.append(
                Website(
                    website["name"],
                    website["url"],
                    wait=wait,
                    webhook_url=str(website.get("webhook_url") or self.webhook_url),
                    ignore_ssl=ignore_ssl,
                    _config=self,
                )
            )
        self.websites = websites

    def reload_config(self):
        try:
            with open("config.json", "r") as f:
                config = json.load(f)

            self.raw_websites = config["websites"]
            self.webhook_url = config["webhook_url"]
            self.often = config.get("often", 30)
            self.timeout = config.get("timeout", 15)
            self.ignore_ssl = bool(config.get("ignore_ssl", False))
            self._embeds = config.get("embed_format", default_embeds)

        except FileNotFoundError:
            raise errors.ConfigNotFound()
        except (json.decoder.JSONDecodeError, KeyError):
            raise errors.UnknownConfigFormat(config)  # type: ignore
        if self.raw_websites:
            self.reload_website_cache()
