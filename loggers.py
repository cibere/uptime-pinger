import logging
import logging.handlers

__all__ = ("setup_logging",)


def setup_logging():
    logger = logging.getLogger("uptime")
    logger.setLevel(logging.DEBUG)

    class ahandler(logging.Formatter):
        LEVEL_COLOURS = [
            (logging.DEBUG, "\x1b[40;1m"),
            (logging.INFO, "\x1b[34;1m"),
            (logging.WARNING, "\x1b[33;1m"),
            (logging.ERROR, "\x1b[31m"),
            (logging.CRITICAL, "\x1b[41m"),
        ]

        FORMATS = {
            level: logging.Formatter(
                f"\x1b[30;1m%(asctime)s\x1b[0m {colour}%(levelname)-8s\x1b[0m \x1b[33m%(name)s\x1b[0m %(message)s",
                "%Y-%m-%d %H:%M:%S",
            )
            for level, colour in LEVEL_COLOURS
        }

        def format(self, record):
            formatter = self.FORMATS.get(record.levelno)
            if formatter is None:
                formatter = self.FORMATS[logging.DEBUG]
            if record.exc_info:
                text = formatter.formatException(record.exc_info)
                record.exc_text = f"\x1b[31m{text}\x1b[0m"

            output = formatter.format(record)
            record.exc_text = None
            return output

    handler = logging.handlers.RotatingFileHandler(
        filename="logs.log", encoding="utf-8", maxBytes=32 * 1024 * 1024, backupCount=5
    )
    dt_fmt = "%Y-%m-%d %H:%M:%S"
    formatter = logging.Formatter(
        "[{asctime}] [{levelname:<8}] {name}: {message}", dt_fmt, style="{"
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    log_handler = logging.StreamHandler()
    log_handler.setFormatter(ahandler())
    logger.addHandler(log_handler)
    return logger
