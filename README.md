## DroiTaka

A personal bot that runs on Discord.

## Running

I would prefer if you don't run an instance of my bot. Just call the join command with an invite URL to have it on your server. The source here is provided for educational purposes for discord.py.

However...

You should only need two main configuration files while the rest will be created automatically.

First is a credentials.json file with the credentials:

```js
{
    "email": "myemail@gmail.com",
    "password": "mypassword"
}
```

After you do the setup required just edit the `cogs/utils/checks.py` file with your owner ID.

## Requirements

- Python 3.5+
- Async version of discord.py
- lxml
