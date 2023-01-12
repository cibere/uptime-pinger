import asyncio

from aiohttp import ClientSession, ClientTimeout
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import Response
from starlette.templating import Jinja2Templates

from loggers import setup_logging
from objects.config import Config
from objects.website import Website


class App(Starlette):
    session: ClientSession
    loop: asyncio.AbstractEventLoop

    logs = setup_logging()
    config = Config()
    templates = Jinja2Templates(directory="templates")
    cache: dict[str, Website] = {}


app = App()
app.config.reload_config()


@app.route("/")
async def route_index(req: Request):
    return app.templates.TemplateResponse(
        "index.html", {"request": req, "services": app.config.websites}
    )


@app.route("/{website:str}", methods=["GET"])
async def route_get_website(req: Request):
    websitename = req.path_params["website"]
    website = app.cache.get(websitename)

    if not website:
        return Response(status_code=404)

    return app.templates.TemplateResponse(
        "service.html", {"request": req, "service": website}
    )


@app.on_event("startup")
async def on_startup():
    timeout = ClientTimeout(total=app.config.timeout)
    app.session = ClientSession(timeout=timeout)
    app.loop = asyncio.get_running_loop()

    for website in app.config.websites:
        if not website.hidden:
            app.cache[website.name] = website
        app.loop.create_task(website.start(app.session))


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app)
