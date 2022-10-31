import aiohttp, asyncio
import datetime
from time_to_human import human_timedelta
import traceback
from errors import *
import objects
from loggers import setup_logging
logger = setup_logging()

config = objects.Config()
config.reload_config()

async def main():
    async with aiohttp.ClientSession(timeout=config.timeout) as cs:
        while True:
            for website in config.websites:
                logger.info(f"Checking {website.name}...")
                up = None
                try:
                    raw = await cs.get(website.url, ssl=config.ignore_ssl)
                    status = await raw.read()
                except Exception as e:
                    logger.info(f"offline (could not connect): {e}")
                    up = False
                if up is None:
                    if str(status) == "b'Pong!'":
                        up = True
                        logger.info(f"online")
                    else:
                        up = False
                        logger.info(f"offline (does not display 'Pong!')")
                send = False
                if website.name in config.down.keys() and up is True:
                    send = True
                    embed = config.get_embed(0)
                    embed['description'] = embed['description'].format(website = website.name, time=human_timedelta(config.down[website.name]))
                    embed['timestamp'] = str(datetime.datetime.utcnow())
                    config.down.pop(website.name)

                elif website.name not in config.down and up is False:
                    config.down[website.name] = datetime.datetime.utcnow()
                    send = True
                    embed = config.get_embed(1)
                    embed['description'] = embed['description'].format(website = website.name)
                    embed['timestamp'] = str(datetime.datetime.utcnow())
                if send:
                    payload = {
                        'embeds' : [embed]
                    }
                    logger.debug(f"Payload Sent: {payload}")
                    x = await cs.post(config.webhook_url, json=payload, ssl=config.ignore_ssl)
                    try:
                        logger.debug(f"Payload Recieved: {await x.json()}")
                    except aiohttp.ContentTypeError:
                        pass
                    logger.info(f"Send Report with code: {x.status}")
            logger.debug(f"Down Websites: {config.down}")
            logger.info("sleeping...")
            await config.wait()
                

try:
    asyncio.run(main())
except Exception as e:
    logger.error(traceback.format_exc())