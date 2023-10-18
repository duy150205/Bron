import discord
from discord import app_commands
from discord.app_commands import Group
from discord.ext import commands
from discord.ui import Button, View, Select
import requests
import random

import os
import music_config
from music.audiocontroller import AudioController
from music.settings import Settings
from music.utils import guild_to_audiocontroller, guild_to_settings

intents = discord.Intents.all()
bot = commands.Bot(command_prefix='!', intents=intents)
bot.remove_command("help")

initial_extensions = ['music.commands.music',
                      'music.commands.general', 'music.plugins.button']

if __name__ == '__main__':
    music_config.ABSOLUTE_PATH = os.path.dirname(os.path.abspath(__file__))
    music_config.COOKIE_PATH = music_config.ABSOLUTE_PATH + music_config.COOKIE_PATH
'''
    for extension in initial_extensions:
        try:
            bot.load_extension(extension)
        except Exception as e:
            print(e)
'''

@bot.event
async def on_ready():
    print('Bot da den')
    print('Syncing slash commands...')
    await bot.change_presence(activity=discord.Game(name="/help"))
    for extension in initial_extensions:
        try:
            await bot.load_extension(extension)
        except Exception as e:
            print(e)

    for guild in bot.guilds:
        await register(guild)
        print("Joined {}".format(guild.name))
    try:
        synced = await bot.tree.sync()
        print(f'Synced {len(synced)} commands')
    except Exception as e:
        print(e)
    nest_asyncio.apply()
    db_thread = threading.Thread(target=check_updates)
    db_thread.start()

@bot.event
async def on_guild_join(guild):
    print(guild.name)
    await register(guild)

async def register(guild):

    guild_to_settings[guild] = Settings(guild)
    guild_to_audiocontroller[guild] = AudioController(bot, guild)

    sett = guild_to_settings[guild]

    try:
        await guild.me.edit(nick=sett.get('default_nickname'))
    except:
        pass

    if music_config.GLOBAL_DISABLE_AUTOJOIN_VC == True:
        return

    vc_channels = guild.voice_channels

    if sett.get('vc_timeout') == False:
        if sett.get('start_voice_channel') == None:
            try:
                await guild_to_audiocontroller[guild].register_voice_channel(guild.voice_channels[0])
            except Exception as e:
                print(e)

        else:
            for vc in vc_channels:
                if vc.id == sett.get('start_voice_channel'):
                    try:
                        await guild_to_audiocontroller[guild].register_voice_channel(vc_channels[vc_channels.index(vc)])
                    except Exception as e:
                        print(e)

@bot.event
async def on_member_join(member: discord.Member):
    await bot.get_channel(1034827460937789510).send(f"{member.mention} Chào mừng đến với bình nguyên vô tận! <:Homies_1:1021371909973233774>")

@bot.event
async def on_member_remove(member: discord.Member):
    await bot.get_channel(1032308866496614431).send(f"**{member}** has left")


# -----------------------------------PREFIX COMMANDS-----------------------------------------------
@bot.command(name="ping")
async def ping(ctx):
    await ctx.send(f"{int(round(bot.latency * 1000, 1))}ms")

@bot.command(name="promotion")
async def promotion(ctx):
    await ctx.send('https://bronyafeetlicker.github.io/')

@bot.command(name="surprise")
async def surprise(ctx):
    await ctx.send(random.choice(['kys (kill yourself) :joy:','kys (keep yourself safe) :smiling_face_with_3_hearts:']))


# -----------------------------------------SLASH COMMANDS--------------------------------------------------------

# ----------------------------------------------GENERAL----------------------------------------------------
# embeds for help command
def help_pages():
    pages = []

    page1 = discord.Embed(colour=discord.Color.from_rgb(42, 66, 129),
                          title=f"General")
    page1.add_field(name=f"\u200b\n",
                    value=f"**/help**\n"
                          f"The help command\n",
                    inline=False)
    page1.add_field(name=f"\u200b\n",
                    value=f"\u200b\n"
                          f"**!ping**\n"
                          f"Displays latency of bot\n"
                          f"\u200b\n"
                          f"**!promotion**\n"
                          f"Self-promotion hihi\n"
                          f"\u200b\n"
                          f"**!surprise**\n"
                          f"Try it! (you may get 2 different responses)\n"
                          f"\u200b\n"
                    ,inline=False)
    page1.set_author(name='Help')
    page1.set_footer(text="Page 1", icon_url="https://i.imgur.com/HRGXb9i.jpg")
    pages.append(page1)

    page2 = discord.Embed(colour=discord.Color.from_rgb(42, 66, 129),
                          title=f"Manga Tracker")
    page2.add_field(name=f"\u200b\n",
                    value=f"**/manga search**\n"
                          f"Search for a manga on MangaDex.\n"
                          f"\u200b\n"
                          f"**/manga tracklist**\n"
                          f"Shows all mangas in your tracklist.\n"
                          f"\u200b\n"
                    ,inline=False)
    page2.set_author(name='Help')
    page2.set_footer(text="Page 2", icon_url="https://i.imgur.com/HRGXb9i.jpg")
    pages.append(page2)

    page3 = discord.Embed(colour=discord.Color.from_rgb(42, 66, 129),
                          title=f"AI Image")
    page3.add_field(name=f"\u200b\n",
                    value=f"**/ai image**\n"
                          f"AI generates 9 images based on your prompt.\n"
                          f"\u200b\n"
                          f"**/ai art**\n"
                          f"AI generates 9 images based on your prompt (art style).\n"
                          f"\u200b\n"
                          f"**/ai drawing**\n"
                          f"AI generates 9 images based on your prompt (drawing style).\n"
                          f"\u200b\n"
                          f"**/ai photo**\n"
                          f"AI generates 9 images based on your prompt (photo style).\n"
                          f"\u200b\n"
                    ,inline=False)
    page3.set_author(name='Help')
    page3.set_footer(text="Page 3", icon_url="https://i.imgur.com/HRGXb9i.jpg")
    pages.append(page3)

    page5 = discord.Embed(colour=discord.Color.from_rgb(42, 66, 129),
                          title=f"Music")
    page5.add_field(name=f"\u200b\n",
                    value=f"**!connect**\n"
                          f"Make bot join your current voice channel\n"
                          f"\u200b\n"
                          f"**!disconnect**\n"
                          f"Clear music and leave voice channel\n"
                          f"\u200b\n"
                          f"**!reset**\n"
                          f"Bot should be disconnected with **/disconnect**, not manually. If bot ran into trouble after forced disconnection, use **/reset**\n"
                          f"\u200b\n"
                          f"**!play** `[keyword / Youtube URL / Spotify URL / SoundClound URL]`\n"
                          f"Play song from URL or search from keyword, add to queue if there is already playing song\n"
                          f"\u200b\n"
                          f"**!pause**\n"
                          f"Pause music\n"
                          f"\u200b\n"
                          f"**!resume**\n"  
                          f"Resume music\n"
                          f"\u200b\n"
                          f"**!loop**\n"
                          f"Loop the current playing song\n"
                          f"\u200b\n"
                          f"**!now**\n"
                          f"Display current playing song\n"
                          f"\u200b\n"
                          f"**!history**\n"
                          f"Display all preiously played music\n"
                          f"\u200b\n"
                          f"**!prev**\n"
                          f"Play the previous song\n"
                          f"\u200b\n"
                          f"**!queue**\n"
                          f"Display queue\n"
                          f"\u200b\n"
                          f"**!skip**\n"
                          f"Skip to next song in queue\n"
                          f"\u200b\n"
                          f"**!move** `[index-from]` `[index-to]`\n"
                          f"Move a song in queue to another position\n"
                          f"\u200b\n"
                          f"**!clear**\n"
                          f"Clear queue\n"
                          f"\u200b\n"
                    , inline=False)
    page5.set_author(name='Help')
    page5.set_footer(text="Page 5", icon_url="https://i.imgur.com/HRGXb9i.jpg")
    pages.append(page5)

    return pages


@bot.tree.command(name="help", description='Display command list.')
async def help(ctx: discord.Interaction):
    pages = help_pages()
    c = 0

    async def button_GoToPage1_callback(interaction):
        nonlocal c
        if interaction.user == ctx.user:
            c = 0
            await ctx.edit_original_response(embed=pages[c], view=help_view)
            await interaction.response.defer()
        else:
            await interaction.response.send_message(content='Only command user can use this button.',ephemeral=True)

    async def button_GoToPage2_callback(interaction):
        nonlocal c
        if interaction.user == ctx.user:
            c = 1
            await ctx.edit_original_response(embed=pages[c], view=help_view)
            await interaction.response.defer()
        else:
            await interaction.response.send_message(content='Only command user can use this button.',ephemeral=True)
    async def button_GoToPage3_callback(interaction):
        nonlocal c
        if interaction.user == ctx.user:
            c = 2
            await ctx.edit_original_response(embed=pages[c], view=help_view)
            await interaction.response.defer()
        else:
            await interaction.response.send_message(content='Only command user can use this button.',ephemeral=True)

    async def button_GoToPage4_callback(interaction):
        nonlocal c
        if interaction.user == ctx.user:
            c = 3
            await ctx.edit_original_response(embed=pages[c], view=help_view)
            await interaction.response.defer()
        else:
            await interaction.response.send_message(content='Only command user can use this button.',ephemeral=True)

    button1 = Button(label='General', style=discord.ButtonStyle.blurple)
    button1.callback = button_GoToPage1_callback

    button2 = Button(label='Manga Tracker', style=discord.ButtonStyle.blurple)
    button2.callback = button_GoToPage2_callback

    button3 = Button(label='AI Image Generator', style=discord.ButtonStyle.blurple)
    button3.callback = button_GoToPage3_callback

    button4 = Button(label='Music', style=discord.ButtonStyle.blurple)
    button4.callback = button_GoToPage4_callback

    help_view = View(timeout=300)
    help_view.add_item(button1)
    help_view.add_item(button2)
    help_view.add_item(button3)
    help_view.add_item(button4)

    await ctx.response.send_message(embed=pages[c], view=help_view)



# ----------------------------------------AI ART---------------------------------------------

ai_group = Group(name='ai', description='description')
from datetime import datetime

import typing
import functools

import m_ai

async def run_blocking(blocking_func: typing.Callable, *args, **kwargs) -> typing.Any:
    func = functools.partial(blocking_func, *args, **kwargs)
    return await bot.loop.run_in_executor(None, func)

@ai_group.command(name='image', description='[AI] Generates 9 images based on your prompt.')
@app_commands.describe(prompt="Describe what you want the bot to generate.")
async def image(ctx: discord.Interaction, prompt: str):
    await ctx.response.send_message(f'**{prompt}** - Generating...\n'
                                    f'You will be pinged when the images are ready.')
    a = datetime.now()

    r = await run_blocking(m_ai.image_generate, prompt)
    b = datetime.now()
    d = (b - a).seconds
    if r == 403:
        msg = await ctx.channel.send(f'**{prompt}** - Requested by {ctx.user.mention}\n'
                                    f'Style: None\n'
                                    f'Time taken: {d} seconds\n'
                                    f'**RESPONSE 403 (DECLINED)**')
    if r == 524:
        msg = await ctx.channel.send(f'**{prompt}** - Requested by {ctx.user.mention}\n'
                                    f'Style: None\n'
                                    f'Time taken: {d} seconds\n'
                                    f'**RESPONSE 524 (TIMED OUT)**')
    if r != 524 and r != 403:
        msg = await ctx.channel.send(f'**{prompt}** - Requested by {ctx.user.mention}\n'
                                    f'Style: None\n'
                                    f'Time taken: {d} seconds'
                                    , files=r)
    await ctx.edit_original_response(content=f'[[See Result]]({msg.jump_url})')

@ai_group.command(name='art', description='[AI] Generates 9 images based on your prompt (art style).')
@app_commands.describe(prompt="Describe what you want the bot to generate.")
async def image_art(ctx: discord.Interaction, prompt: str):
    await ctx.response.send_message(f'**{prompt}** - Generating...\n'
                                    f'You will be pinged when the images are ready.')
    a = datetime.now()

    r = await run_blocking(m_ai.image_art_generate, prompt)
    b = datetime.now()
    d = (b - a).seconds
    if r == 403:
        msg = await ctx.channel.send(f'**{prompt}** - Requested by {ctx.user.mention}\n'
                                     f'Style: Art\n'
                                     f'Time taken: {d} seconds\n'
                                     f'**RESPONSE 403 (DECLINED)**')
    if r == 524:
        msg = await ctx.channel.send(f'**{prompt}** - Requested by {ctx.user.mention}\n'
                                     f'Style: Art\n'
                                     f'Time taken: {d} seconds\n'
                                     f'**RESPONSE 524 (TIMED OUT)**')
    if r != 524 and r != 403:
        msg = await ctx.channel.send(f'**{prompt}** - Requested by {ctx.user.mention}\n'
                                     f'Style: Art\n'
                                     f'Time taken: {d} seconds'
                                     , files=r)
    await ctx.edit_original_response(content=f'[[See Result]]({msg.jump_url})')

@ai_group.command(name='drawing', description='[AI] Generates 9 images based on your prompt (drawing style).')
@app_commands.describe(prompt="Describe what you want the bot to generate.")
async def image_drawing(ctx: discord.Interaction, prompt: str):
    await ctx.response.send_message(f'**{prompt}** - Generating...\n'
                                    f'You will be pinged when the images are ready.')
    a = datetime.now()

    r = await run_blocking(m_ai.image_drawing_generate, prompt)
    b = datetime.now()
    d = (b - a).seconds
    if r == 403:
        msg = await ctx.channel.send(f'**{prompt}** - Requested by {ctx.user.mention}\n'
                                     f'Style: Drawing\n'
                                     f'Time taken: {d} seconds\n'
                                     f'**RESPONSE 403 (DECLINED)**')
    if r == 524:
        msg = await ctx.channel.send(f'**{prompt}** - Requested by {ctx.user.mention}\n'
                                     f'Style: Drawing\n'
                                     f'Time taken: {d} seconds\n'
                                     f'**RESPONSE 524 (TIMED OUT)**')
    if r != 524 and r != 403:
        msg = await ctx.channel.send(f'**{prompt}** - Requested by {ctx.user.mention}\n'
                                     f'Style: Drawing\n'
                                     f'Time taken: {d} seconds'
                                     , files=r)
    await ctx.edit_original_response(content=f'[[See Result]]({msg.jump_url})')

@ai_group.command(name='photo', description='[AI] Generates 9 images based on your prompt (photo style).')
@app_commands.describe(prompt="Describe what you want the bot to generate.")
async def image_photo(ctx: discord.Interaction, prompt: str):
    await ctx.response.send_message(f'**{prompt}** - Generating...\n'
                                    f'You will be pinged when the images are ready.')
    a = datetime.now()

    r = await run_blocking(m_ai.image_photo_generate, prompt)
    b = datetime.now()
    d = (b - a).seconds
    if r == 403:
        msg = await ctx.channel.send(f'**{prompt}** - Requested by {ctx.user.mention}\n'
                                     f'Style: Photo\n'
                                     f'Time taken: {d} seconds\n'
                                     f'**RESPONSE 403 (DECLINED)**')
    if r == 524:
        msg = await ctx.channel.send(f'**{prompt}** - Requested by {ctx.user.mention}\n'
                                     f'Style: Photo\n'
                                     f'Time taken: {d} seconds\n'
                                     f'**RESPONSE 524 (TIMED OUT)**')
    if r != 524 and r != 403:
        msg = await ctx.channel.send(f'**{prompt}** - Requested by {ctx.user.mention}\n'
                                     f'Style: Photo\n'
                                     f'Time taken: {d} seconds'
                                     , files=r)
    await ctx.edit_original_response(content=f'[[See Result]]({msg.jump_url})')


bot.tree.add_command(ai_group)



#-----------------MANGA UPDATES-------------------
import time
import json
import threading
import nest_asyncio
import asyncio

import m_manga

def check_updates():
    old_data = m_manga.grab_rss_data()
    old_data.reverse()
    while True:
        now = datetime.now()
        print(now)
        new_data = m_manga.grab_rss_data()
        new_data.reverse()
        if new_data != old_data:
            print("New Manga Releases!")
            new_releases = [manga for manga in new_data if manga not in old_data]
            '''print(new_releases)'''
            for id in new_releases:
                asyncio.run_coroutine_threadsafe(notify_users(id), bot.loop)
                time.sleep(2)
        time.sleep(30)
        old_data = new_data

async def notify_users(id: str):
    response = requests.get(f'https://api.mangadex.org/chapter/{id}?includes[]=scanlation_group&includes[]=manga')
    data = response.json()
    v = data['data']['attributes']['volume']
    c = data['data']['attributes']['chapter']
    if str(v).strip() != 'None':
        chapter = f'v.{v} c.{c}'
    else:
        chapter = f'c.{c}'
    t = data['data']['attributes']['updatedAt']
    update = f"{t[11:19]} (UTC) {t[8:10]}/{t[5:7]}/{t[0:4]}"
    lang = str(data['data']['attributes']['translatedLanguage']).capitalize()
    c_name = data['data']['attributes']['title']
    if c_name == None:
        c_name = "None"
    group = "None"
    for i in data['data']['relationships']:
        if i['type'] == 'scanlation_group':
            group = i['attributes']['name']
        if i['type'] == 'manga':
            title = list(i['attributes']['title'].values())[0]
            m_id = i['id']
            link = f"https://mangadex.org/manga/{i['id']}"
    users = ""
    with open('database.json') as json_file:
        json_data = json.load(json_file)
    json_file.close()
    for a in json_data:
        for b in json_data[a]:
            if b[0] == m_id and lang in ['Vi','En']:
                users = users + f"<@{a}>"
    em = discord.Embed(title=title, url=link)
    em.set_author(name='New Chapter Released')
    em.add_field(name='Chapter Name', value=c_name, inline=False)
    em.add_field(name='Volume/Chapter', value=chapter, inline=True)
    '''em.add_field(name='Translator Group', value=group, inline=True)'''
    em.add_field(name="Translated Language", value=lang, inline=True)
    em.set_footer(text=f"Chapter updated at: {update}")

    channel_update = bot.get_channel(1122103881686585435)
    channel_ping = bot.get_channel(1122103911172550706)
    if users != "":
        await channel_ping.send(content=users + ' New chapter 🔥🔥🔥', embed=em)
        time.sleep(1)
        await channel_update.send(embed=em)
    else:
        await channel_update.send(embed=em)

m_group = Group(name='manga', description='description')

@m_group.command(name='search', description='[Manga Updates] Search a manga on MangaDex.')
@app_commands.describe(manga_name="Name of the manga. Get manga name from MangaDex if you want absolute result.")
async def manga_search(ctx: discord.Interaction, manga_name: str):
    manga_name = manga_name.strip()
    response_t = requests.get(f"https://api.mangadex.org/manga?title={manga_name}&limit=100")
    data = response_t.json()
    if len(data['data']) == 0:
        await ctx.response.send_message('No manga found.')
        return
    else:
        id = data['data'][0]['id']

    response_t = requests.get(f"https://api.mangadex.org/manga/{id}")
    data_t = response_t.json()
    title = list(data_t['data']['attributes']['title'].values())[0]
    link = f'https://mangadex.org/manga/{id}'
    year = data_t['data']['attributes']['year']
    status = data_t['data']['attributes']['status'].capitalize()
    rating = data_t['data']['attributes']['contentRating']
    if "safe" in rating:
        rating = "No"
    else:
        rating = "Yes"
    try:
        desc = str(data_t["data"]["attributes"]["description"]["en"])
    except:
        try:
            desc = list(data_t['data']['attributes']['description'].values())[0]
        except:
            desc = "None"
    if len(desc) > 1023:
        desc = desc[0:995] + '... **Read more on MangaDex**'
    genres = ""
    for a in data_t['data']['attributes']['tags']:
        if a['attributes']['group'] == 'genre':
            genres = genres + f"`{a['attributes']['name']['en']}` "
    cover_url = ""
    for a in data_t['data']['relationships']:
        if a['type'] == 'cover_art':
            response_temp = requests.get(f"https://api.mangadex.org/cover/{a['id']}")
            data_temp = response_temp.json()
            cover_url = f"https://uploads.mangadex.org/covers/{id}/{data_temp['data']['attributes']['fileName']}"
            print(cover_url)

    em=discord.Embed(title= title, url = link, color=0xff0000)
    em.add_field(name="Year", value=year, inline=True)
    em.add_field(name="Status", value=status, inline=True)
    em.add_field(name="NSFW", value=rating, inline=True)
    em.add_field(name="Description", value=desc, inline=False)
    em.add_field(name="Genres", value=genres,inline=False)
    em.set_image(url=cover_url)
    em.set_author(name='Manga Info')

    #list
    ems = []
    a = 1
    d = 0
    while d != 101:
        temp = ''
        while a<d*10+1+10 and a>=d*10+1:
            try:
                temp = temp + f"{a}. {list(data['data'][a-1]['attributes']['title'].values())[0]}\n"
            except:
                break
            a+=1
        if temp != '':
            em_t = discord.Embed(title=f"Search for '{manga_name}'",description=temp)
            if len(data['data'])%10 != 0:
                em_t.set_footer(text=f"Page {d + 1}/{int(len(data['data']) / 10)+1}")
            else:
                em_t.set_footer(text=f"Page {d + 1}/{int(len(data['data']) / 10)}")
            ems.append(em_t)
        else:
            break
        d+=1

    c = 0
    async def button_GoToFirst_callback(interaction):
        nonlocal c
        if interaction.user == ctx.user:
            c = 0
            await ctx.edit_original_response(embed=ems[c], view=views[c])
            await interaction.response.defer()
        else:
            await interaction.response.send_message(content='Only command user can use this button.',ephemeral=True)

    async def button_GoToLast_callback(interaction):
        nonlocal c
        if interaction.user == ctx.user:
            c = len(ems) - 1
            await ctx.edit_original_response(embed=ems[c], view=views[c])
            await interaction.response.defer()
        else:
            await interaction.response.send_message(content='Only command user can use this button.',ephemeral=True)

    async def button_GoNext_callback(interaction):
        nonlocal c
        if interaction.user == ctx.user:
            if c < len(ems) - 1:
                c = c + 1
            await ctx.edit_original_response(embed=ems[c], view=views[c])
            await interaction.response.defer()
        else:
            await interaction.response.send_message(content='Only command user can use this button.',ephemeral=True)

    async def button_GoBack_callback(interaction):
        nonlocal c
        if interaction.user == ctx.user:
            if c > 0:
                c = c - 1
            await ctx.edit_original_response(embed=ems[c], view=views[c])
            await interaction.response.defer()
        else:
            await interaction.response.send_message(content='Only command user can use this button.',ephemeral=True)

    button1 = Button(emoji="⏪", style=discord.ButtonStyle.blurple,row=1)
    button1.callback = button_GoToFirst_callback

    button2 = Button(emoji="◀", style=discord.ButtonStyle.blurple,row=1)
    button2.callback = button_GoBack_callback

    button3 = Button(emoji='▶', style=discord.ButtonStyle.blurple,row=1)
    button3.callback = button_GoNext_callback

    button4 = Button(emoji='⏩', style=discord.ButtonStyle.blurple,row=1)
    button4.callback = button_GoToLast_callback

    async def menu_callback(interaction):
        nonlocal id, title, link, cover_url
        if interaction.user == ctx.user:
            id = data['data'][int(menu[c].values[0])-1]['id']
            response_t = requests.get(f"https://api.mangadex.org/manga/{id}")
            data_t = response_t.json()
            title = list(data_t['data']['attributes']['title'].values())[0]
            link = f'https://mangadex.org/manga/{id}'
            year = data_t['data']['attributes']['year']
            status = data_t['data']['attributes']['status'].capitalize()
            rating = data_t['data']['attributes']['contentRating']
            if "safe" in rating:
                rating = "No"
            else:
                rating = "Yes"
            try:
                desc = str(data_t["data"]["attributes"]["description"]["en"])
            except:
                try:
                    desc = list(data_t['data']['attributes']['description'].values())[0]
                except:
                    desc = "None"
            if len(desc) > 1023:
                desc = desc[0:995] + '... **Read more on MangaDex**'
            genres = ""
            for a in data_t['data']['attributes']['tags']:
                if a['attributes']['group'] == 'genre':
                    genres = genres + f"`{a['attributes']['name']['en']}` "
            cover_url = ""
            for a in data_t['data']['relationships']:
                if a['type'] == 'cover_art':
                    response_temp = requests.get(f"https://api.mangadex.org/cover/{a['id']}")
                    data_temp = response_temp.json()
                    cover_url = f"https://mangadex.org/covers/{id}/{data_temp['data']['attributes']['fileName']}"

            em = discord.Embed(title=title, url=link, color=0xff0000)
            em.add_field(name="Year", value=year, inline=True)
            em.add_field(name="Status", value=status, inline=True)
            em.add_field(name="NSFW", value=rating, inline=True)
            em.add_field(name="Description", value=desc, inline=False)
            em.add_field(name="Genres", value=genres, inline=False)
            em.set_image(url=cover_url)
            em.set_author(name='Manga Info')

            user_id = str(ctx.user.id)
            with open('database.json') as json_file:
                json_data = json.load(json_file)
            json_file.close()
            if user_id not in json_data:
                await ctx.edit_original_response(embed=em, view=back_track_view)
            else:
                if [id,title] in json_data[user_id]:
                    await ctx.edit_original_response(embed=em, view=back_untrack_view)
                else:
                    await ctx.edit_original_response(embed=em, view=back_track_view)
            with open('database.json', 'w') as json_file:
                json.dump(json_data, json_file)
            json_file.close()

            await interaction.response.defer()
        else:
            await interaction.response.send_message(content='Only command user can use this button.',ephemeral=True)
    menu = []
    views = []
    for k in range(len(ems)):
        menu.append(Select(placeholder='Choose manga from the list.',
                     min_values=1,
                     max_values=1,
                     options=[discord.SelectOption(label=f"{i+1+k*10}") for i in range(10) if i+k*10<len(data['data'])],
                     row=0))
        menu[k].callback = menu_callback

        myview = View(timeout=300)
        myview.add_item(menu[k])
        myview.add_item(button1)
        myview.add_item(button2)
        myview.add_item(button3)
        myview.add_item(button4)

        views.append(myview)


    async def button_Back_callback(interaction):
        nonlocal c
        if interaction.user == ctx.user:
            await ctx.edit_original_response(embed=ems[c], view=views[c])
            await interaction.response.defer()
        else:
            await interaction.response.send_message(content='Only command user can use this button.',ephemeral=True)
    async def button_Track_callback(interaction):
        nonlocal c
        if interaction.user == ctx.user:
            user_id = str(ctx.user.id)
            with open('database.json') as json_file:
                json_data = json.load(json_file)
            json_file.close()
            if user_id not in json_data:
                json_data[user_id] = []
                json_data[user_id].append([id,title])
                ee = discord.Embed(title='Successfully added manga to tracklist.', description=f"[{title}]({link})")
                ee.set_image(url=cover_url)
            else:
                json_data[user_id].append([id,title])
                ee = discord.Embed(title='Successfully added manga to tracklist.', description=f"[{title}]({link})")
                ee.set_image(url=cover_url)
            with open('database.json', 'w') as json_file:
                json.dump(json_data, json_file)
            json_file.close()
            await ctx.edit_original_response(embed=ee, view=None)
            await interaction.response.defer()
        else:
            await interaction.response.send_message(content='Only command user can use this button.',ephemeral=True)
    async def button_Untrack_callback(interaction):
        nonlocal c
        if interaction.user == ctx.user:
            user_id = str(ctx.user.id)
            with open('database.json') as json_file:
                json_data = json.load(json_file)
            json_file.close()
            json_data[user_id].remove([id,title])
            with open('database.json', 'w') as json_file:
                json.dump(json_data, json_file)
            json_file.close()
            ee = discord.Embed(title='Successfully removed manga from tracklist.', description=f"[{title}]({link})")
            ee.set_image(url=cover_url)
            await ctx.edit_original_response(embed=ee, view=None)
            await interaction.response.defer()
        else:
            await interaction.response.send_message(content='Only command user can use this button.',ephemeral=True)

    back_track_view = View(timeout=300)
    back_untrack_view = View(timeout=300)
    button_back = Button(label='Not this', style=discord.ButtonStyle.grey,emoji='😭')
    button_back.callback = button_Back_callback

    button_track = Button(label='Track this manga', style=discord.ButtonStyle.blurple)
    button_track.callback = button_Track_callback
    back_track_view.add_item(button_back)
    back_track_view.add_item(button_track)

    button_untrack = Button(label='Untrack this manga', style=discord.ButtonStyle.red)
    button_untrack.callback = button_Untrack_callback
    back_untrack_view.add_item(button_back)
    back_untrack_view.add_item(button_untrack)

    user_id = str(ctx.user.id)
    with open('database.json') as json_file:
        json_data = json.load(json_file)
    json_file.close()
    if user_id not in json_data:
        await ctx.response.send_message(embed=em, view= back_track_view)
    else:
        if [id, title] in json_data[user_id]:
            await ctx.response.send_message(embed=em, view= back_untrack_view)
        else:
            await ctx.response.send_message(embed=em, view= back_track_view)
    with open('database.json', 'w') as json_file:
        json.dump(json_data, json_file)
    json_file.close()



@m_group.command(name='tracklist', description='[Manga Updates] Shows all manga in your tracklist.')
async def my_manga(ctx: discord.Interaction):
    user_id = str(ctx.user.id)
    with open('database.json') as json_file:
        json_data = json.load(json_file)
    json_file.close()
    if user_id not in json_data:
        ee= discord.Embed(title='You are not tracking any manga')
        await ctx.response.send_message(embed=ee)
    else:
        if json_data[user_id] != []:
            ems = []
            a = 1
            d = 0
            while d != 101:
                temp = ''
                while a < d * 10 + 1 + 10 and a >= d * 10 + 1:
                    try:
                        temp = temp + f"{a}. {json_data[user_id][a-1][1]}\n"
                    except:
                        break
                    a += 1
                if temp != '':
                    em_t = discord.Embed(title=f"Your Manga Tracklist", description=temp)
                    if len(json_data[user_id]) % 10 != 0:
                        em_t.set_footer(text=f"Page {d + 1}/{int(len(json_data[user_id]) / 10) + 1}")
                    else:
                        em_t.set_footer(text=f"Page {d + 1}/{int(len(json_data[user_id]) / 10)}")
                    ems.append(em_t)
                else:
                    break
                d += 1


            c = 0

            async def button_GoToFirst_callback(interaction):
                nonlocal c
                if interaction.user == ctx.user:
                    c = 0
                    await ctx.edit_original_response(embed=ems[c], view=views[c])
                    await interaction.response.defer()
                else:
                    await interaction.response.send_message(content='Only command user can use this button.',
                                                            ephemeral=True)

            async def button_GoToLast_callback(interaction):
                nonlocal c
                if interaction.user == ctx.user:
                    c = len(ems) - 1
                    await ctx.edit_original_response(embed=ems[c], view=views[c])
                    await interaction.response.defer()
                else:
                    await interaction.response.send_message(content='Only command user can use this button.',
                                                            ephemeral=True)

            async def button_GoNext_callback(interaction):
                nonlocal c
                if interaction.user == ctx.user:
                    if c < len(ems) - 1:
                        c = c + 1
                    await ctx.edit_original_response(embed=ems[c], view=views[c])
                    await interaction.response.defer()
                else:
                    await interaction.response.send_message(content='Only command user can use this button.',
                                                            ephemeral=True)

            async def button_GoBack_callback(interaction):
                nonlocal c
                if interaction.user == ctx.user:
                    if c > 0:
                        c = c - 1
                    await ctx.edit_original_response(embed=ems[c], view=views[c])
                    await interaction.response.defer()
                else:
                    await interaction.response.send_message(content='Only command user can use this button.',
                                                            ephemeral=True)

            button1 = Button(emoji="⏪", style=discord.ButtonStyle.blurple, row=1)
            button1.callback = button_GoToFirst_callback

            button2 = Button(emoji="◀", style=discord.ButtonStyle.blurple, row=1)
            button2.callback = button_GoBack_callback

            button3 = Button(emoji='▶', style=discord.ButtonStyle.blurple, row=1)
            button3.callback = button_GoNext_callback

            button4 = Button(emoji='⏩', style=discord.ButtonStyle.blurple, row=1)
            button4.callback = button_GoToLast_callback

            title = ''
            link = ''
            cover_url=''

            async def menu_callback(interaction):
                nonlocal title, link, cover_url
                if interaction.user == ctx.user:
                    id = json_data[user_id][int(menu[c].values[0])-1][0]
                    response_t = requests.get(f"https://api.mangadex.org/manga/{id}")
                    data_t = response_t.json()
                    title = list(data_t['data']['attributes']['title'].values())[0]
                    link = f'https://mangadex.org/manga/{id}'
                    year = data_t['data']['attributes']['year']
                    status = data_t['data']['attributes']['status'].capitalize()
                    rating = data_t['data']['attributes']['contentRating']
                    if "safe" in rating:
                        rating = "No"
                    else:
                        rating = "Yes"
                    try:
                        desc = str(data_t["data"]["attributes"]["description"]["en"])
                    except:
                        try:
                            desc = list(data_t['data']['attributes']['description'].values())[0]
                        except:
                            desc = "None"
                    if len(desc) > 1023:
                        desc = desc[0:995] + '... **Read more on MangaDex**'
                    genres = ""
                    for a in data_t['data']['attributes']['tags']:
                        if a['attributes']['group'] == 'genre':
                            genres = genres + f"`{a['attributes']['name']['en']}` "
                    cover_url = ""
                    for a in data_t['data']['relationships']:
                        if a['type'] == 'cover_art':
                            response_temp = requests.get(f"https://api.mangadex.org/cover/{a['id']}")
                            data_temp = response_temp.json()
                            cover_url = f"https://mangadex.org/covers/{id}/{data_temp['data']['attributes']['fileName']}"

                    em = discord.Embed(title=title, url=link, color=0xff0000)
                    em.add_field(name="Year", value=year, inline=True)
                    em.add_field(name="Status", value=status, inline=True)
                    em.add_field(name="NSFW", value=rating, inline=True)
                    em.add_field(name="Description", value=desc, inline=False)
                    em.add_field(name="Genres", value=genres, inline=False)
                    em.set_image(url=cover_url)
                    em.set_author(name='Manga Info')
                    await ctx.edit_original_response(embed=em, view=back_untrack_view)
                    await interaction.response.defer()
                else:
                    await interaction.response.send_message(content='Only command user can use this button.',
                                                            ephemeral=True)

            menu = []
            views = []
            for k in range(len(ems)):
                menu.append(Select(placeholder='Choose manga to REMOVE from tracklist.',
                                   min_values=1,
                                   max_values=1,
                                   options=[discord.SelectOption(label=f"{i + 1 + k * 10}") for i in range(10) if
                                            i + k * 10 < len(json_data[user_id])],
                                   row=0))
                menu[k].callback = menu_callback

                myview = View(timeout=300)
                myview.add_item(menu[k])
                myview.add_item(button1)
                myview.add_item(button2)
                myview.add_item(button3)
                myview.add_item(button4)

                views.append(myview)

            async def button_Back_callback(interaction):
                nonlocal c
                if interaction.user == ctx.user:
                    await ctx.edit_original_response(embed=ems[c], view=views[c])
                    await interaction.response.defer()
                else:
                    await interaction.response.send_message(content='Only command user can use this button.',
                                                            ephemeral=True)

            async def button_Untrack_callback(interaction):
                nonlocal c
                if interaction.user == ctx.user:
                    user_id = str(ctx.user.id)
                    with open('database.json') as json_file:
                        json_data = json.load(json_file)
                    json_file.close()
                    json_data[user_id].pop(int(menu[c].values[0])-1)
                    with open('database.json', 'w') as json_file:
                        json.dump(json_data, json_file)
                    json_file.close()
                    ee = discord.Embed(title='Successfully removed manga from tracklist.',
                                       description=f"[{title}]({link})")
                    ee.set_image(url=cover_url)
                    await ctx.edit_original_response(embed=ee, view=None)
                    await interaction.response.defer()
                else:
                    await interaction.response.send_message(content='Only command user can use this button.',
                                                            ephemeral=True)

            back_untrack_view = View(timeout=300)
            button_back = Button(label='Not this', style=discord.ButtonStyle.grey, emoji='😭')
            button_back.callback = button_Back_callback
            button_untrack = Button(label='Untrack this manga', style=discord.ButtonStyle.red)
            button_untrack.callback = button_Untrack_callback
            back_untrack_view.add_item(button_back)
            back_untrack_view.add_item(button_untrack)

            await ctx.response.send_message(embed=ems[c], view=myview)


        else:
            ee = discord.Embed(title='You are not tracking any manga')
            await ctx.response.send_message(embed=ee)
    with open('database.json', 'w') as json_file:
        json.dump(json_data, json_file)
    json_file.close()

bot.tree.add_command(m_group)



# --------RUN-----------️
from bot_token import TOKEN

bot.run(TOKEN)