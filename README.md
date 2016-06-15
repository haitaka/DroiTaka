## DroiTaka
A personal bot that runs on Discord.

## Features

- Music playing ( from YaDisk & from Vk.com )
- Random frection selector for Endless Legend
- Some nice mod utilities

## Running

credentials.json file with the credentials:

```json
{
    "bot_token": "your bot token",
    "client_id": "your client_id",
    "yadisk_token": "yandex-disk token",
    "vk_token": "vk.com tokken",
}
```

After you do the setup required just edit the `cogs/utils/checks.py` file with your owner ID.

## Requirements

- Python 3.5+
- Async version of discord.py (`pip install git+https://github.com/Rapptz/discord.py@async`)
- Requests
