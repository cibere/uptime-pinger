import sys

from loggers import setup_logging
from objects.app import App
from routes import ROUTES

app = App(routes=ROUTES)
app.config.reload_config()


if __name__ == "__main__":
    debug = False
    try:
        if sys.argv[1] == "--debug":
            debug = True
    except IndexError:
        pass

    setup_logging(debug)

    import uvicorn

    uvicorn.run(app, host=app.config.host, port=app.config.port)
