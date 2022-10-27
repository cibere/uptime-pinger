import aiohttp, asyncio
import datetime, time
import traceback
from errors import *
import objects
from loggers import setup_logging
logger = setup_logging()

config = objects.Config()
config.reload_config()

async def main():
    async with aiohttp.ClientSession() as cs:
        while True:
            for website in config.websites:
                logger.info(f"Checking {website.name}...")
                up = None
                try:
                    raw = await cs.get(website.url, ssl=config.ignore_ssl)
                except:
                    logger.info(f"offline: {status}")
                    up = False
                status = await raw.read()
                if up is None:
                    if str(status) == "b'Pong!'":
                        up = True
                        logger.info(f"online")
                    else:
                        up = False
                        logger.info(f"offline: {status}")
                send = False
                if website.name in config.down.keys() and up is True:
                    config.down.pop(website.name)
                    send = True
                    embed = config._embeds[0]
                    embed['description'] = embed['description'].format(website = website.name, time = time.human_timedelta(config.down[website.name], accuracy=None, brief=False, suffix=False))
                    embed['timestamp'] = str(datetime.datetime.utcnow())

                elif website.name not in config.down and up is False:
                    config.down[website.name] = int(datetime.datetime.utcnow().timestamp())
                    send = True
                    embed = config._embeds[1]
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
            logger.info("sleeping...")
            await config.wait()
                

try:
    asyncio.run(main())
except Exception as e:
    logger.error(traceback.format_exc())