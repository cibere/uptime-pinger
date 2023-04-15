# Uptime Timer

This is just something that I use, and I do not support self-use.
Feel free to make a PR if you find any flaws or have any improvements.

# How to use

Simply fill the config.json file, install the requirements, and run the `main.py` file.

# How to fill config

`config.json` has some configuration choices. Here is an example:

```json
{
  "host": "127.0.0.1", // the host ip/domain to listen for. Defaults to 0.0.0.0
  "port": 8080, // the port to listen for. Defaults to 443
  "title": "...", // title that is shown on the index page
  "online_text": "", // default is an empty string ("") which means no online_text. If an online text is set, a website will only be marked online if it displays excacly the online_text. If no online_text is set (or an empty string is set) then it doesn't matter what the website displays.
  "webhook_url": "...", // the global webhook_url to send updates to.
  "ignore_ssl": "True", // takes a bool, wether to ignore_ssl or not
  "timeout": 30, // timeout max amount of time the script will wait for a website to load before marking it as offline
  "often": 30, // how often to check
  "websites": [
    // the websites to check
    {
      "name": "...", // the name to show instead of the url
      "url": "...", // the websites url. By default it checks for `Pong!`
      "description": "...", // description for the website
      "links": [
        {
          // special links for the website
          "name": "...", // link name
          "url": "..." // link url
        }
      ]
    } // each website can also get its own `webhook_url`, `timeout`, `online_text`, and `often` values, but not required.
  ],
  "embed_format": [
    // this is the default embed_format, but it controls how the data is sent to the webhook. Mainly because webhook_url is made to be a discord webhook
    {
      "title": "Uptime Alert",
      "description": "{website} is now **online**\nIt was offline for {time}",
      "color": 65292
    },
    {
      "title": "Downtime Alert",
      "description": "{website} is now **offline**",
      "color": 16711680
    }
  ]
}
```
