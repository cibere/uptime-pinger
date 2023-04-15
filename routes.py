import asyncio

from starlette.endpoints import WebSocketEndpoint
from starlette.responses import PlainTextResponse, Response
from starlette.routing import Route, WebSocketRoute
from websockets.exceptions import (
    ConnectionClosed,
    ConnectionClosedError,
    ConnectionClosedOK,
)

from objects.app import Request, WebSocket

__all__ = ("ROUTES",)


async def index_callback(req: Request):
    return req.app.templates.TemplateResponse(
        "index.jinja",
        {
            "request": req,
            "services": req.app.config.websites,
            "title": req.app.config.title,
        },
    )


async def get_website_callback(req: Request):
    websitename = req.path_params["website"]
    website = req.app.cache.get(websitename)

    if not website:
        return Response(status_code=404)

    return req.app.templates.TemplateResponse(
        "service.jinja", {"request": req, "service": website}
    )


async def get_website_offline_since_callback(req: Request):
    websitename = req.path_params["website"]
    website = req.app.cache.get(websitename)

    if not website:
        return Response(status_code=404)

    return PlainTextResponse(website.offline_since)


class WebsocketStatus(WebSocketEndpoint):
    encoding = "text"

    async def on_connect(self, ws: WebSocket):
        await ws.accept()
        websitename = ws.path_params["website"]
        website = ws.app.cache.get(websitename)
        if website is None:
            await ws.send_text("404, unknown website")
            return await ws.close()

        while 1:
            try:
                await ws.send_text(website.offline_since)
            except (ConnectionClosedOK, ConnectionClosedError, ConnectionClosed):
                return
            await asyncio.sleep(3)


ROUTES = [
    Route("/", index_callback, methods=["GET"]),
    Route("/{website:str}", get_website_callback, methods=["GET"]),
    WebSocketRoute("/{website:str}/ws", WebsocketStatus),
]
