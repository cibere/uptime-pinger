from starlette.responses import PlainTextResponse, Response
from starlette.routing import Route

from objects.app import Request

__all__ = ("ROUTES",)


async def index_callback(req: Request):
    return req.app.templates.TemplateResponse(
        "index.html", {"request": req, "services": req.app.config.websites}
    )


async def get_website_callback(req: Request):
    websitename = req.path_params["website"]
    website = req.app.cache.get(websitename)

    if not website:
        return Response(status_code=404)

    return req.app.templates.TemplateResponse(
        "service.html", {"request": req, "service": website}
    )


async def get_website_offline_since_callback(req: Request):
    websitename = req.path_params["website"]
    website = req.app.cache.get(websitename)

    if not website:
        return Response(status_code=404)

    return PlainTextResponse(website.offline_since)


ROUTES = [
    Route("/", index_callback, methods=["GET"]),
    Route("/{website:str}", get_website_callback, methods=["GET"]),
    Route(
        "/{website:str}/offline_since",
        get_website_offline_since_callback,
        methods=["GET"],
    ),
]
