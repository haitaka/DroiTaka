## DroiTaka

A personal bot that runs on Discord.

## Running

You should only need two main configuration files while the rest will be created automatically.

First is a credentials.json file with the credentials:

```js
{
    "email": "myemail@gmail.com",
    "password": "mypassword"
}
```

Second is copy_cred.json file with `copy.com` file-storage credentials:

```js
{
    "login": "myemail@gmail.com",
    "passwd": "mypassword"
}
```

After you do the setup required just edit the `cogs/utils/checks.py` file with your owner ID.

## Requirements

- Python 3.5+
- Async version of discord.py (`pip install git+https://github.com/Rapptz/discord.py@async`)
