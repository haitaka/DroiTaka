## DroiTaka

A personal bot that runs on Discord.

## Running
`depricated`
You should only need configuration file while the rest will be created automatically.

credentials.json file with the credentials:

```json
{
    "login": "",
    "passwd": "",
    "copy_login": "",
    "copy_passwd": "",
    "yadisk_token": ""

}
```

After you do the setup required just edit the `cogs/utils/checks.py` file with your owner ID.

## Requirements

- Python 3.5+
- Async version of discord.py (`pip install git+https://github.com/Rapptz/discord.py@async`)
