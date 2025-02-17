from discord import FFmpegPCMAudio, PCMVolumeTransformer
from discord.ext import commands
from lib.embeds import create_basic_embed, EMOJI_ERROR, EMOJI_SUCCESS
from youtube_dl import YoutubeDL
import urllib.request
import os.path

TEXT_SUCCESS_FORMAT = '{0} \u200B \u200B Now playing **{1}** in **{2}**!'  # args: emoji, title, channel name

YTDL_OPTIONS = {
    'format': 'bestaudio/best',
    'quiet': True,
}

class AudioPlayer(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def allstar(self, ctx):
        audio_emoji = '🌟'
        audio_title = 'All Star'
        audio_url = 'https://www.youtube.com/watch?v=5xxQs34UMx4'
        await self.handle_audio_command(ctx, audio_emoji, audio_title, audio_url)

    @commands.command()
    async def babyshark(self, ctx):
        audio_emoji = '🦈'
        audio_title = 'Baby Shark'
        audio_url = 'https://www.youtube.com/watch?v=LBHYhvOHgvc'
        await self.handle_audio_command(ctx, audio_emoji, audio_title, audio_url, skip_seconds=17)

    @commands.command()
    async def bingbangbong(self, ctx):
        audio_emoji = '💃'
        audio_title = 'UK Hun?'
        audio_url = 'https://www.youtube.com/watch?v=z9wRiNzM6Ww'
        await self.handle_audio_command(ctx, audio_emoji, audio_title, audio_url)

    @commands.command()
    async def bitesthedust(self, ctx):
        audio_emoji = '🧹'
        audio_title = 'Another One Bites the Dust'
        audio_url = 'https://www.youtube.com/watch?v=cGJ_IyFwieY'
        await self.handle_audio_command(ctx, audio_emoji, audio_title, audio_url, skip_seconds=42)

    @commands.command()
    async def letitgo(self, ctx):
        audio_emoji = '❄'
        audio_title = 'Let It Go'
        audio_url = 'https://www.youtube.com/watch?v=FnpJBkAMk44'
        await self.handle_audio_command(ctx, audio_emoji, audio_title, audio_url, skip_seconds=59, volume=0.1)

    @commands.command()
    async def squidgame(self, ctx):
        audio_emoji = '❄'
        audio_title = 'Squid Game OST - Pink Soldiers'
        audio_url = 'https://www.youtube.com/watch?v=v9NQYKv2rTg'
        await self.handle_audio_command(ctx, audio_emoji, audio_title, audio_url, skip_seconds=1, volume=0.15)

    @commands.command()
    async def chase(self, ctx):
        audio_emoji = '❄'
        audio_title = 'Horror Chase Music - Scary Movie Intense Suspense Instrumental Royalty Free'
        audio_url = 'https://www.youtube.com/watch?v=nEuXiJ-d2YM&t=24'
        await self.handle_audio_command(ctx, audio_emoji, audio_title, audio_url, skip_seconds=22, volume=0.15)

    @commands.command()
    async def nyancat(self, ctx):
        audio_emoji = '🐱'
        audio_title = 'Nyan Cat'
        audio_url = 'https://www.youtube.com/watch?v=QH2-TGUlwu4'
        await self.handle_audio_command(ctx, audio_emoji, audio_title, audio_url, volume=0.1)

    @commands.command()
    async def afrocircus(self, ctx):
        audio_emoji = '🕺'
        audio_title = 'Afro Circus/ I Like To Move It'
        audio_url = 'https://www.youtube.com/watch?v=slMub4NtrSk'
        await self.handle_audio_command(ctx, audio_emoji, audio_title, audio_url, skip_seconds=9)

    @commands.command()
    async def livinlavidaloca(self, ctx):
        audio_emoji = '🕺'
        audio_title = 'Livin\' La Vida Loca'
        audio_url = 'https://www.youtube.com/watch?v=p47fEXGabaY'
        await self.handle_audio_command(ctx, audio_emoji, audio_title, audio_url, skip_seconds=2)

    # Rick Roll -.-
    @commands.command()
    async def vidaloca(self, ctx):
        audio_emoji = '🕺'
        audio_title = 'Livin\' La Vida Loca'
        audio_url = 'https://www.youtube.com/watch?v=dQw4w9WgXcQ'
        await self.handle_audio_command(ctx, audio_emoji, audio_title, audio_url, skip_seconds=43)

    @commands.command()
    async def rickroll(self, ctx):
        audio_emoji = '🕺'
        audio_title = 'Never Gonna Give You Up'
        audio_url = 'https://www.youtube.com/watch?v=dQw4w9WgXcQ'
        await self.handle_audio_command(ctx, audio_emoji, audio_title, audio_url, skip_seconds=43)

    @commands.command()
    async def stayinalive(self, ctx):
        audio_emoji = '🚑'
        audio_title = 'Stayin\' Alive'
        audio_url = 'https://www.youtube.com/watch?v=fNFzfwLM72c'
        await self.handle_audio_command(ctx, audio_emoji, audio_title, audio_url, skip_seconds=43)

    @commands.command()
    async def tunak(self, ctx):
        audio_emoji = '🚑'
        audio_title = 'Tunak Tunak Tun'
        audio_url = 'https://www.youtube.com/watch?v=eZ2PtEx9-ls'
        await self.handle_audio_command(ctx, audio_emoji, audio_title, audio_url, skip_seconds=27, volume=0.12)

    @commands.command()
    async def saltyballs(self, ctx):
        audio_emoji = '🍫'
        audio_title = 'Chocolate Salty Balls (P.S. I Love You)'
        audio_url = 'https://www.youtube.com/watch?v=bB59Ow8hSyY'
        await self.handle_audio_command(ctx, audio_emoji, audio_title, audio_url, skip_seconds=47, volume=0.08)

    @commands.command()
    async def doubletrouble(self, ctx):
        audio_emoji = '<:surprisedPika:741269041657806879>'
        audio_title = 'TEAM ROCKET (Double Trouble) - Pokémon METAL cover by Jonathan Young'
        audio_url = 'https://www.youtube.com/watch?v=Oc_ifA4lGIo'
        await self.handle_audio_command(ctx, audio_emoji, audio_title, audio_url, skip_seconds=14, volume=0.03)
        
    @commands.command()
    async def crimmis(self, ctx):
        audio_emoji = '❄'
        audio_title = 'Mariah Carey - All I Want For Christmas Is You (Official Video)'
        audio_url = 'https://www.youtube.com/watch?v=yXQViqx6GMY'
        await self.handle_audio_command(ctx, audio_emoji, audio_title, audio_url, skip_seconds=2, volume=0.25)
        
    @commands.command()
    async def spacejam(self, ctx):
        audio_emoji = '🏀'
        audio_title = 'Space Jam Theme Song'
        audio_url = 'https://www.youtube.com/watch?v=J9FImc2LOr8'
        await self.handle_audio_command(ctx, audio_emoji, audio_title, audio_url, skip_seconds=0, volume=0.25)

    @commands.command()
    async def stopaudio(self, ctx):
        await self.disconnect_voice_clients()
        await ctx.channel.send(embed=create_basic_embed('Successfully stopped all audio playback.', EMOJI_SUCCESS))

    async def handle_audio_command(self, ctx, audio_emoji, audio_title, audio_url, skip_seconds=0, volume=0.25):
        text_channel = ctx.channel
        if len(ctx.message.mentions) == 1:
            user = ctx.message.mentions[0]
            if user.voice:
                voice_channel = user.voice.channel
                success_text = TEXT_SUCCESS_FORMAT.format(audio_emoji, audio_title, voice_channel.name)
                async with text_channel.typing():
                    await self.disconnect_voice_clients()
                    await self.play_youtube_audio(audio_url, voice_channel, text_channel, success_text, skip_seconds, volume)
            else:
                embed = create_basic_embed(f'**{user.mention}** is not currently in a voice channel.', EMOJI_ERROR)
                await text_channel.send(embed=embed)
        else:
            embed = create_basic_embed('Please specify exactly one person to receive the audio.', EMOJI_ERROR)
            await text_channel.send(embed=embed)

    async def play_youtube_audio(self, url, voice_channel, text_channel, success_text, skip_seconds, volume):
        # noinspection PyBroadException
        try:
            loop = self.bot.loop or asyncio.get_event_loop()
            videoId = url.split("v=")[1]
            videoCache = 'data/' + videoId + '.webm'

            if not os.path.isfile('data/' + videoId + '.webm'):
                print(f'Downloading and caching video for {videoId} to {videoCache}')
                data = await loop.run_in_executor(None, lambda: YoutubeDL(YTDL_OPTIONS).extract_info(url, download=False))
                await loop.run_in_executor(None, lambda: urllib.request.urlretrieve(data['url'], videoCache))

            audio_source = FFmpegPCMAudio(videoCache, options=f'-ss {skip_seconds}')
            voice_client = await voice_channel.connect()
            voice_client.play(PCMVolumeTransformer(audio_source, volume=volume))
            await text_channel.send(embed=create_basic_embed(success_text))
        except Exception as exception:
            print(exception)
            await text_channel.send(embed=create_basic_embed('Error playing YouTube audio.', EMOJI_ERROR))

    async def disconnect_voice_clients(self):
        for voice_client in self.bot.voice_clients:
            await voice_client.disconnect()


def setup(bot):
    bot.add_cog(AudioPlayer(bot))
