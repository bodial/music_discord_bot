import discord
import config
from discord.ext import commands
from youtube_dl import YoutubeDL
import random
from discord.utils import get

vc = None

YDL_OPTIONS = {'format': 'worstaudio/best',
               'noplaylist': 'False',
               'simulate': 'True',
               'preferredquality': '192',
               'preferredcodec': 'mp3',
               'key': 'FFmpegExtractAudio'
               }
FFMPEG_OPTIONS = {'before_options': '-http_persistent 0 -reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',  #-http_persistent 0
                  'options': '-vn'
                  }
intents= discord.Intents.all()
#intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)
 
@bot.event
async def on_ready():
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')
    print('Bot online')

@bot.command()
async def play(ctx, *, arg):
    """Воспроизводит музыку"""
    global vc
    if vc == None:
        print('vc none')
        #vc = await ctx.message.author.voice.channel.connect()
        vc = await ctx.message.author.voice.channel.connect()
    print('подключился')
 
    with YoutubeDL(YDL_OPTIONS) as ydl:
        if 'https://' in arg:
            print('полная ссылка')
            info = ydl.extract_info(arg, download=False)
        else:
            print('по названию')
            info = ydl.extract_info(f"ytsearch:{arg}", download=False)['entries'][0]
    print('info получено')
    url = info['formats'][0]['url']


    print('скачал трек')
    vc.play(discord.FFmpegPCMAudio(executable="../../extra_programms/ffmpeg.exe", source=url, **FFMPEG_OPTIONS))

@bot.command()
async def pause(ctx):
    """Ставит на паузу"""
    global vc
    if (vc == None) or not(vc.is_playing()):
        await ctx.channel.send('музыка не играет')
    else:
        vc.pause()

@bot.command()
async def reboot(ctx):
    """Перезагрузка переменной войс канала"""
    global vc
    print('rebooted')
    vc = None

@bot.command()
async def resume(ctx):
    """Снимает трек с паузы"""
    global vc
    if (vc == None):
        await ctx.channel.send('нет активного трека')
    elif not(vc.is_paused()):
        await ctx.channel.send('трек не на паузе')
    else:
        vc.resume()
        
@bot.command()
async def stop(ctx):
    """Прекращает воспроизведение музыки"""
    global vc
    if (vc == None):
        await ctx.channel.send('нет активного трека')
    else:
        vc.stop()

@bot.command()
async def bb(ctx):
    channel = ctx.message.author.voice.channel
    if not channel:
        await ctx.send("You are not connected to a voice channel")
        return
    voice = get(bot.voice_clients, guild=ctx.guild)
    if voice and voice.is_connected():
        await voice.move_to(channel)
    else:
        voice = await channel.connect()
    #source = FFmpegPCMAudio('1.m4a')
    #player = voice.play(source)

@bot.command()
async def join_voice(ctx):
    connected = ctx.author.voice
    if connected:
        await connected.channel.connect()
    print(connected)

@bot.command(name='join', invoke_without_subcommand=True)
async def join(ctx):
    destination = ctx.author.voice.channel
    if ctx.voice_state.voice:
        await ctx.voice_state.voice.move_to(destination)
        return
    
    ctx.voice_state.voice = await destination.connect()
    await ctx.send(f"Joined {ctx.author.voice.channel} Voice Channel")

@bot.command()
async def roll(ctx, *, arg):
    """Роллит случайное число от указанных через пробел min, max"""
    diapazon = arg.split('-');
    min = int(diapazon[0])
    max = int(diapazon[1])
    if (min <= max):   
        result = random.randint(min, max)
    else:
        result = 'неверный формат'
    await ctx.channel.send(result)

@bot.command()
async def write(ctx, *, arg):
    """Повторяет ваше сообщение"""
    await ctx.channel.send(arg)

@bot.command()
async def leave(ctx):
    """Командует боту выйти"""
    global vc
    if vc == None or not vc.is_connected():
        await ctx.channel.send('бот не на канале')
    else:
        await vc.disconnect()

bot.run(config.token)
