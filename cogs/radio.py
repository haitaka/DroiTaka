from .utils import config, checks, formats
import discord
from discord.ext import commands
import discord.utils

class Radio:
    """The radio-bot related commands."""

    def __init__(self, bot):
        self.bot = bot
        self.player = None
        if not discord.opus.is_loaded():
            discord.opus.load_opus('/usr/local/lib/libopus.so') #FreeBSD path

    @property
    def is_playing(self)
        return self.player is not None and self.player.is_playing()
    
    @commands.command()
    async def join(self, *, channel : discord.Channel = None):
        """Join voice channel.
        """
        if channel is None or channel != discord.ChannelType.voice:
            await self.bot.say('Cannot find a voice channel by that name.')
		await self.bot.join_voice_channel(channel)
		
	@commands.command()
    async def leave(self):
        """Leave voice channel.
        """
        await self.stop()
        await self.bot.voice.disconnect()
        
    @commands.command()
    async def pause(self):
        """Pause.
        """
        if self.player is not None:
            self.player.pause()
            
    @commands.command()
    async def resume(self):
        """Resume playing.
        """
        if self.player is not None and not self.is_playing():
            self.player.resume()
            
    @commands.command()
    async def skip(self):
        """Skip song and play next.
        """
        if self.player is not None and self.is_playing():
            self.player.stop()
            self.toggle_next_song()
    
    """
    @commands.group(pass_context=True, invoke_without_command=True)
    async def tag(self, ctx, *, name : str):
        """Allows you to tag text for later retrieval.

        If a subcommand is not called, then this will search the tag
        database for the tag requested.
        """
        lookup = name.lower()
        server = ctx.message.server
        tag = self.get_tag(server, lookup)
        if tag is None:
            await self.bot.say('Tag "{}" not found.'.format(name))
            return

        tag.uses += 1
        await self.bot.say(tag)

        # update the database with the new tag reference
        db = self.config.get(tag.location)
        await self.config.put(tag.location, db)

    @tag.error
    async def tag_error(self, error, ctx):
        if isinstance(error, commands.MissingRequiredArgument):
            await self.bot.say('Missing the tag name to retrieve.')

    @tag.command(pass_context=True, aliases=['add'])
    async def create(self, ctx, name : str, *, content : str):
        """Creates a new tag owned by you.

        If you create a tag via private message then the tag is a generic
        tag that can be accessed in all servers. Otherwise the tag you
        create can only be accessed in the server that it was created in.
        """
        lookup = name.lower()
        location = self.get_database_location(ctx.message)
        db = self.config.get(location, {})
        if lookup in db:
            await self.bot.say('A tag with the name of "{}" already exists.'.format(name))
            return

        db[lookup] = TagInfo(name, content, ctx.message.author.id, location=location)
        await self.config.put(location, db)
        await self.bot.say('Tag "{}" successfully created.'.format(name))

    @tag.command(pass_context=True)
    async def generic(self, ctx, name : str, *, content : str):
        """Creates a new generic tag owned by you.

        Unlike the create tag subcommand,  this will always attempt to create
        a generic tag and not a server-specific one.
        """
        lookup = name.lower()
        db = self.config.get('generic', {})
        if lookup in db:
            await self.bot.say('A tag with the name of "{}" already exists.'.format(name))
            return

        db[lookup] = TagInfo(name, content, ctx.message.author.id, location='generic')
        await self.config.put('generic', db)
        await self.bot.say('Tag "{}" successfully created.'.format(name))

    @tag.command(pass_context=True, aliases=['update'])
    async def edit(self, ctx, name : str, *, content : str):
        """Modifies an existing tag that you own.

        This command completely replaces the original text. If you edit
        a tag via private message then the tag is looked up in the generic
        tag database. Otherwise it looks at the server-specific database.
        """

        lookup = name.lower()
        server = ctx.message.server
        tag = self.get_tag(server, lookup)

        if tag is None:
            await self.bot.say('The tag "{}" does not exist.'.format(name))
            return

        if tag.owner_id != ctx.message.author.id:
            await self.bot.say('Only the tag owner can edit this tag.')
            return

        db = self.config.get(tag.location)
        tag.content = content
        await self.config.put(tag.location, db)
        await self.bot.say('Tag successfully edited.')

    @tag.command(pass_context=True, aliases=['delete'])
    async def remove(self, ctx, *, name : str):
        """Removes a tag that you own.

        The tag owner can always delete their own tags. If someone requests
        deletion and has Manage Messages permissions or a Bot Mod role then
        they can also remove tags from the server-specific database. Generic
        tags can only be deleted by the bot owner or the tag owner.
        """
        lookup = name.lower()
        server = ctx.message.server
        tag = self.get_tag(server, lookup)

        if tag is None:
            await self.bot.say('Tag not found.')
            return

        can_delete = checks.roles_or_permissions(ctx, lambda r: r.name == 'Bot Admin', manage_messages=True)
        can_delete = can_delete or tag.owner_id == ctx.message.author.id

        if not can_delete:
            await self.bot.say('You do not have permissions to delete this tag.')
            return

        db = self.config.get(tag.location)
        del db[lookup]
        await self.config.put(tag.location, db)
        await self.bot.say('Tag successfully removed.')

    @tag.command(pass_context=True)
    async def info(self, ctx, *, name : str):
        """Retrieves info about a tag.

        The info includes things like the owner and how many times it was used.
        """

        lookup = name.lower()
        server = ctx.message.server
        tag = self.get_tag(server, lookup)

        if tag is None:
            await self.bot.say('Tag "{}" not found.'.format(name))
            return

        entries = tag.info_entries(ctx)
        await formats.entry_to_code(self.bot, entries)

    @info.error
    async def info_error(self, error, ctx):
        if isinstance(error, commands.MissingRequiredArgument):
            await self.bot.say('Missing tag name to get info of.')

    @tag.command(name='list', pass_context=True)
    async def _list(self, ctx):
        """Lists all the tags that belong to you.

        This includes the generic tags as well. If this is done in a private
        message then you will only get the generic tags you own and not the
        server specific tags.
        """

        owner = ctx.message.author.id
        server = ctx.message.server
        tags = [tag.name for tag in self.config.get('generic', {}).values() if tag.owner_id == owner]
        if server is not None:
            tags.extend(tag.name for tag in self.config.get(server.id, {}).values() if tag.owner_id == owner)

        if tags:
            fmt = 'You have the following tags:\n{}'
            await self.bot.say(fmt.format(', '.join(tags)))
        else:
            await self.bot.say('You have no tags.')

    @tag.command(pass_context=True)
    async def search(self, ctx, *, query : str):
        """Searches for a tag.

        This searches both the generic and server-specific database. If it's
        a private message, then only generic tags are searched.

        The query must be at least 2 characters.
        """

        server = ctx.message.server
        query = query.lower()
        if len(query) < 2:
            await self.bot.say('The query length must be at least two characters.')
            return

        generic = self.config.get('generic', {})
        results = {value.name for name, value in generic.items() if query in name}

        if server is not None:
            db = self.config.get(server.id, {})
            for name, value in db.items():
                if query in name:
                    results.add(value.name)

        fmt = '{} tag(s) found.\n{}'
        if results:
            await self.bot.say(fmt.format(len(results), '\n'.join(results)))
        else:
            await self.bot.say('No tags found.')

    @search.error
    async def search_error(self, error, ctx):
        if isinstance(error, commands.MissingRequiredArgument):
            await self.bot.say('Missing query to search for.')"""

def setup(bot):
    bot.add_cog(Radio(bot))
