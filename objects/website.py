from __future__ import annotations

import asyncio
import datetime
import logging
from typing import TYPE_CHECKING

import aiohttp

from time_to_human import human_timedelta

if TYPE_CHECKING:
    from .config import Config

logger = logging.getLogger("uptime")


class Website:
    def __init__(
        self,
        name: str,
        url: str,
        wait: int,
        webhook_url: str,
        ignore_ssl: bool,
        _config: Config,
    ):
        self.name = name
        self.url = url
        self.online: bool = True
        self.wait = wait
        self.webhook_url = webhook_url
        self.ignore_ssl = ignore_ssl
        self._config = _config

        self.time: datetime.datetime = None  # type: ignore

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
                up = True
            except Exception as e:
                logger.info(f"{self.name} is offline (could not connect): {e}")
                up = False
                text = ""

            if up is True:
                if str(text) == "b'Pong!'":
                    up = True
                    logger.info(f"online")
                else:
                    up = False
                    logger.info(f"offline (does not display 'Pong!')")

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
                logger.info(f"Send Report with code: {x.status}")

            await asyncio.sleep(self.wait)
