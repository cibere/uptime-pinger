import aiohttp, asyncio
import datetime
from time_to_human import human_timedelta
import traceback
import errors
import copy, json
from loggers import setup_logging
logger = setup_logging()

class Website:
    def __init__(self, name: str, url: str, wait: int, webhook_url: str, ignore_ssl: bool):
        self.name = name
        self.url = url
        self.online: bool = True
        self.wait = wait
        self.webhook_url = webhook_url
        self.ignore_ssl = ignore_ssl
        
        self.time: datetime.datetime = None # type: ignore
    
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
                embed = config.get_embed(0)
                embed['description'] = embed['description'].format(website = self.name, time=human_timedelta(self.time))
                embed['timestamp'] = str(datetime.datetime.utcnow())
                self.online = True

            elif self.online and up is False:
                send = True
                embed = config.get_embed(1)
                embed['description'] = embed['description'].format(website = self.name)
                embed['timestamp'] = str(datetime.datetime.utcnow())
                self.time = datetime.datetime.utcnow()
                self.online = False
            
            else:
                raise RuntimeError('Unknown set of items')
                
            if send:
                payload = {
                    'embeds' : [embed]
                }
                logger.debug(f"Payload Sent: {payload}")
                x = await session.post(self.webhook_url, json=payload, ssl=self.ignore_ssl)
                try:
                    logger.debug(f"Payload Recieved: {await x.json()}")
                except aiohttp.ContentTypeError:
                    pass
                logger.info(f"Send Report with code: {x.status}")
            
            await asyncio.sleep(self.wait)

default_embeds = [
    {
        "title" : "Uptime Alert",
        "description" : "{website} is now **online**\nIt was offline for {time}",
        "color" : 65292
    },
    {
        "title" : "Downtime Alert",
        "description" : "{website} is now **offline**",
        "color" : 16711680
    }
]

class Config:
    def __init__(self):
        # {'name' : datetime.datetime obj}
        self.down = {}
        self.websites = []
        self.raw_websites = []
        self.webhook_url = None
        self.often = None
        self.timeout = 15
        
        self._embeds = default_embeds
    
    def get_embed(self, /, _type: int):
        if _type not in [0, 1]:
            raise errors.UnknownEmbedType(_type)
        return copy.copy(self._embeds[_type])
    
    def reload_website_cache(self):
        websites = []
        for website in self.raw_websites:
            try:
                wait = int(website['wait'])
            except:
                wait = int(self.often) # type: ignore
            try:
                ignore_ssl = bool(website['ignore_ssl'])
            except:
                ignore_ssl = self.ignore_ssl
                
            websites.append(
                Website(website['name'], website['url'], wait=wait, webhook_url= str(website.get("webhook_url") or self.webhook_url), ignore_ssl=ignore_ssl)
            )
        self.websites = websites
    
    def reload_config(self):
        try:
            with open('config.json', 'r') as f:
                config = json.load(f)
                
            self.raw_websites = config['websites']
            self.webhook_url = config['webhook_url']
            self.often = config.get("often", 30)
            self.timeout = config.get("timeout", 15)
            self.ignore_ssl = bool(config.get("ignore_ssl", False))
            self._embeds = config.get("embed_format", default_embeds)
            
        except FileNotFoundError:
            raise errors.ConfigNotFound()
        except (json.decoder.JSONDecodeError, KeyError):
            raise errors.UnknownConfigFormat(config) # type: ignore
        if self.raw_websites:
            self.reload_website_cache()

config = Config()
config.reload_config()

async def main():
    timeout = aiohttp.ClientTimeout(total=config.timeout)
    async with aiohttp.ClientSession(timeout=timeout) as cs:
        loop = asyncio.get_running_loop()
        for website in config.websites:
            loop.create_task(website.start(cs))
        
        while True:
            await asyncio.sleep(0.1)
                

try:
    asyncio.run(main())
except Exception as e:
    logger.error(traceback.format_exc())