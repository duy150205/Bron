import asyncio

import discord
import music_config
from discord.ext import commands
from music import linkutils, utils


class Music(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='play', description=music_config.HELP_YT_LONG, help=music_config.HELP_YT_SHORT)
    async def _play_song(self, ctx, *, track: str):

        current_guild = utils.get_guild(self.bot, ctx.message)
        audiocontroller = utils.guild_to_audiocontroller[current_guild]

        if (await utils.is_connected(ctx) == None):
            if await audiocontroller.uconnect(ctx) == False:
                return

        if track.isspace() or not track:
            return

        if await utils.play_check(ctx) == False:
            return

        # reset timer
        audiocontroller.timer.cancel()
        audiocontroller.timer = utils.Timer(audiocontroller.timeout_handler)

        if audiocontroller.playlist.loop == True:
            await ctx.send("Loop is enabled. Use {}loop to disable".format(music_config.BOT_PREFIX))
            return

        song = await audiocontroller.process_song(track)

        if song is None:
            await ctx.send(music_config.SONGINFO_ERROR)
            return

        if song.origin == linkutils.Origins.Default:

            if audiocontroller.current_song != None and len(audiocontroller.playlist.playque) == 0:
                await ctx.send(embed=song.info.format_output(music_config.SONGINFO_NOW_PLAYING))
            else:
                await ctx.send(embed=song.info.format_output(music_config.SONGINFO_QUEUE_ADDED))
        elif song.origin == linkutils.Origins.Playlist:
            await ctx.send(music_config.SONGINFO_PLAYLIST_QUEUED)

    @commands.command(name='loop', description=music_config.HELP_LOOP_LONG, help=music_config.HELP_LOOP_SHORT)
    async def _loop(self, ctx):

        current_guild = utils.get_guild(self.bot, ctx.message)
        audiocontroller = utils.guild_to_audiocontroller[current_guild]

        if await utils.play_check(ctx) == False:
            return

        if len(audiocontroller.playlist.playque) < 1 and current_guild.voice_client.is_playing() == False:
            await ctx.send("No songs in queue")
            return

        if audiocontroller.playlist.loop == False:
            audiocontroller.playlist.loop = True
            await ctx.send("Loop enabled :arrows_counterclockwise:")
        else:
            audiocontroller.playlist.loop = False
            await ctx.send("Loop disabled :x:")

    @commands.command(name='pause', description=music_config.HELP_PAUSE_LONG, help=music_config.HELP_PAUSE_SHORT)
    async def _pause(self, ctx):
        current_guild = utils.get_guild(self.bot, ctx.message)

        if await utils.play_check(ctx) == False:
            return

        if current_guild is None:
            await ctx.send(music_config.NO_GUILD_MESSAGE)
            return
        if current_guild.voice_client is None or not current_guild.voice_client.is_playing():
            return
        current_guild.voice_client.pause()
        await ctx.send("Paused music :pause_button:")

    @commands.command(name='queue', description=music_config.HELP_QUEUE_LONG, help=music_config.HELP_QUEUE_SHORT)
    async def _queue(self, ctx):
        current_guild = utils.get_guild(self.bot, ctx.message)

        if await utils.play_check(ctx) == False:
            return

        if current_guild is None:
            await ctx.send(music_config.NO_GUILD_MESSAGE)
            return
        if current_guild.voice_client is None or not current_guild.voice_client.is_playing():
            await ctx.send("Queue is empty :x:")
            return

        playlist = utils.guild_to_audiocontroller[current_guild].playlist

        if music_config.MAX_SONG_PRELOAD > 25:
            music_config.MAX_SONG_PRELOAD = 25

        embed = discord.Embed(title=":scroll: Queue [{}]".format(
            len(playlist.playque)), color=music_config.EMBED_COLOR)

        for counter, song in enumerate(list(playlist.playque)[:music_config.MAX_SONG_PRELOAD], start=1):
            if song.info.title is None:
                embed.add_field(name="{}.".format(str(counter)), value="[{}]({})".format(
                    song.info.webpage_url, song.info.webpage_url), inline=False)
            else:
                embed.add_field(name="{}.".format(str(counter)), value="[{}]({})".format(
                    song.info.title, song.info.webpage_url), inline=False)

        await ctx.send(embed=embed)

    @commands.command(name='move', description=music_config.HELP_MOVE_LONG, help=music_config.HELP_MOVE_SHORT)
    async def _move(self, ctx, *args):
        if len(args) != 2:
            ctx.send("Wrong number of arguments")
            return

        try:
            oldindex, newindex = map(int, args)
        except ValueError:
            ctx.send("Wrong argument")
            return

        current_guild = utils.get_guild(self.bot, ctx.message)
        audiocontroller = utils.guild_to_audiocontroller[current_guild]
        if current_guild.voice_client is None or (
                not current_guild.voice_client.is_paused() and not current_guild.voice_client.is_playing()):
            await ctx.send("Queue is empty :x:")
            return
        try:
            audiocontroller.playlist.move(oldindex - 1, newindex - 1)
        except IndexError:
            await ctx.send("Wrong position")
            return
        await ctx.send("Moved")

    @commands.command(name='skip', description=music_config.HELP_SKIP_LONG, help=music_config.HELP_SKIP_SHORT)
    async def _skip(self, ctx):
        current_guild = utils.get_guild(self.bot, ctx.message)

        if await utils.play_check(ctx) == False:
            return

        audiocontroller = utils.guild_to_audiocontroller[current_guild]
        audiocontroller.playlist.loop = False

        audiocontroller.timer.cancel()
        audiocontroller.timer = utils.Timer(audiocontroller.timeout_handler)

        if current_guild is None:
            await ctx.send(music_config.NO_GUILD_MESSAGE)
            return
        if current_guild.voice_client is None or (
                not current_guild.voice_client.is_paused() and not current_guild.voice_client.is_playing()):
            await ctx.send("Queue is empty :x:")
            return
        current_guild.voice_client.stop()
        await ctx.send("Skipped current song :fast_forward:")

    @commands.command(name='clear', description=music_config.HELP_CLEAR_LONG, help=music_config.HELP_CLEAR_SHORT, aliases=['cl'])
    async def _clear(self, ctx):
        current_guild = utils.get_guild(self.bot, ctx.message)

        if await utils.play_check(ctx) == False:
            return

        audiocontroller = utils.guild_to_audiocontroller[current_guild]
        audiocontroller.clear_queue()
        current_guild.voice_client.stop()
        audiocontroller.playlist.loop = False
        await ctx.send("Cleared queue :no_entry_sign:")

    @commands.command(name='prev', description=music_config.HELP_PREV_LONG, help=music_config.HELP_PREV_SHORT)
    async def _prev(self, ctx):
        current_guild = utils.get_guild(self.bot, ctx.message)

        if await utils.play_check(ctx) == False:
            return

        audiocontroller = utils.guild_to_audiocontroller[current_guild]
        audiocontroller.playlist.loop = False

        audiocontroller.timer.cancel()
        audiocontroller.timer = utils.Timer(audiocontroller.timeout_handler)

        if current_guild is None:
            await ctx.send(music_config.NO_GUILD_MESSAGE)
            return
        await utils.guild_to_audiocontroller[current_guild].prev_song()
        await ctx.send("Playing previous song :track_previous:")

    @commands.command(name='resume', description=music_config.HELP_RESUME_LONG, help=music_config.HELP_RESUME_SHORT)
    async def _resume(self, ctx):
        current_guild = utils.get_guild(self.bot, ctx.message)

        if await utils.play_check(ctx) == False:
            return

        if current_guild is None:
            await ctx.send(music_config.NO_GUILD_MESSAGE)
            return
        current_guild.voice_client.resume()
        await ctx.send("Resumed music :arrow_forward:")

    @commands.command(name='now', description=music_config.HELP_SONGINFO_LONG, help=music_config.HELP_SONGINFO_SHORT)
    async def _now(self, ctx):
        current_guild = utils.get_guild(self.bot, ctx.message)

        if await utils.play_check(ctx) == False:
            return

        if current_guild is None:
            await ctx.send(music_config.NO_GUILD_MESSAGE)
            return
        song = utils.guild_to_audiocontroller[current_guild].current_song
        if song is None:
            await ctx.send('No song playing right now')
        await ctx.send(embed=song.info.format_output(music_config.SONGINFO_SONGINFO))

    @commands.command(name='history', description=music_config.HELP_HISTORY_LONG, help=music_config.HELP_HISTORY_SHORT)
    async def _history(self, ctx):
        current_guild = utils.get_guild(self.bot, ctx.message)

        if await utils.play_check(ctx) == False:
            return

        if current_guild is None:
            await ctx.send(music_config.NO_GUILD_MESSAGE)
            return
        await ctx.send(utils.guild_to_audiocontroller[current_guild].track_history())



async def setup(bot):
    await bot.add_cog(Music(bot))
