import asyncio
from logging import Logger
from typing import Sequence

from aiohttp import ClientSession, ClientTimeout
from starlette.applications import Starlette
from starlette.requests import Request as _Request
from starlette.routing import Mount, Route
from starlette.templating import Jinja2Templates

from objects.config import Config
from objects.website import Website

__all__ = (
    "App",
    "Request",
)


class App(Starlette):
    def __init__(self, routes: Sequence[Route | Mount]) -> None:
        super().__init__(
            routes=routes, on_startup=[self.on_startup], on_shutdown=[self.on_shutdown]
        )
        self.config: Config = Config()
        self.templates: Jinja2Templates = Jinja2Templates(directory="templates")
        self.cache: dict[str, Website] = {}

    session: ClientSession
    loop: asyncio.AbstractEventLoop
    logs: Logger

    async def on_startup(self):
        timeout = ClientTimeout(total=self.config.timeout)
        self.session = ClientSession(timeout=timeout)
        self.loop = asyncio.get_running_loop()

        for website in self.config.websites:
            if not website.hidden:
                self.cache[website.name] = website
            self.loop.create_task(website.start(self.session))

    async def on_shutdown(self):
        if getattr(self, "session", None):
            await self.session.close()


class Request(_Request):
    app: App
