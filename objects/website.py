from __future__ import annotations

import asyncio
import datetime
import logging
from typing import TYPE_CHECKING, Optional

import aiohttp

from time_to_human import human_timedelta

if TYPE_CHECKING:
    from ..types.website import WebsiteLink
    from .config import Config

logger = logging.getLogger("uptime")

__all__ = ("Link", "Website")


class Link:
    def __init__(self, name: str, url: str, color: Optional[str] = None) -> None:
        self.name = name
        self.url = url
        self.color = color or "gray"


class Website:
    links: list[Link]

    def __init__(
        self,
        name: str,
        *,
        description: str,
        url: str,
        wait: int,
        webhook_url: str,
        ignore_ssl: bool,
        _config: Config,
        links: list[WebsiteLink],
        hidden: bool,
        online_text: str | None,
    ):
        self.name = name
        self.url = url
        self.online: bool = True
        self.wait = wait
        self.webhook_url = webhook_url
        self.ignore_ssl = ignore_ssl
        self._config = _config
        self.description = description
        self.hidden = hidden
        self.online_text = online_text

        self.time: datetime.datetime = None  # type: ignore
        self.links = [Link(**x) for x in links]

    @property
    def offline_since(self) -> str:
        if self.time:
            return human_timedelta(self.time)
        else:
            return "an unknown amount of time"

    async def start(self, session: aiohttp.ClientSession):
        while True:
            logger.info(f"Checking {self.name}...")

            try:
                raw = await session.get(self.url, ssl=self.ignore_ssl)
                text = await raw.read()
                text = text.decode()
                up = True
            except Exception as e:
                logger.info(f"{self.name} is offline. Reason: could not connect ({e})")
                up = False
                text = ""

            if up is True:
                if text == self.online_text:
                    up = True
                    logger.info(f"{self.name} is online")
                else:
                    if self.online_text is not None:
                        up = False
                        logger.info(
                            f"{self.name} is offline. Reason: does not display {self.online_text!r}"
                        )

            send = False
            if not self.online and up is True:
                send = True
                embed = self._config.get_embed(0)
                embed["description"] = embed["description"].format(
                    website=self.name, time=human_timedelta(self.time)
                )
                embed["timestamp"] = str(datetime.datetime.utcnow())
                self.online = True

            elif self.online and up is False:
                send = True
                embed = self._config.get_embed(1)
                embed["description"] = embed["description"].format(website=self.name)
                embed["timestamp"] = str(datetime.datetime.utcnow())
                self.time = datetime.datetime.utcnow()
                self.online = False

            if send:
                payload = {"embeds": [embed]}  # type: ignore[reportUnboundVariable]
                logger.debug(f"Payload Sent: {payload}")
                x = await session.post(
                    self.webhook_url, json=payload, ssl=self.ignore_ssl
                )
                try:
                    logger.debug(f"Payload Recieved: {await x.json()}")
                except aiohttp.ContentTypeError:
                    pass
                logger.info(f"Send Report for {self.name}. Received code: {x.status}")

            await asyncio.sleep(self.wait)
