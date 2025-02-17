from asyncio import Lock
from datetime import datetime, timedelta, timezone
from discord import HTTPException, Message, AuditLogAction
from discord.ext import commands
from lib.embeds import create_authored_embed, create_basic_embed
from lib.utils import get_message_link_string

KEY_TIMESTAMP = 'timestamp'  # type: datetime
KEY_CHANNEL_ID = 'channel_id'  # type: int
KEY_USER = 'user'  # type: Member
KEY_CONTENT = 'content'  # type: str
KEY_EXTRAS = 'extras'  # type: str or list[Attachment]

SNIPE_WINDOW = timedelta(seconds=30)
SLOWPOKE_WINDOW = timedelta(seconds=5)

TEXT_SNIPER_FAIL = '**"SNIPER, NO SNIPING!"**\n*"Oh, mannnn...*"'
TEXT_SENT_FILE = '*Sent a file!*'
TEXT_SENT_FILES = '*Sent some files!*'

EMOJI_SLOWPOKE = '<:slowpoke:854520068372168714>'
EMOJI_THUMBS_DOWN = '👎' # Fallback option for when the slowpoke emoji isn't available

URL_SNIPER_ICON = 'https://cdn.discordapp.com/attachments/919924341343399966/919934086183813120/sniper.png'
URL_SWIPER_ICON = 'https://cdn.discordapp.com/attachments/919924341343399966/919933002270789653/swiper.png'


class Sniper(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.deleted_message_cache = []
        self.deleted_message_cache_lock = Lock()
        self.edited_message_cache = []
        self.edited_message_cache_lock = Lock()
        self.removed_reaction_cache = []
        self.removed_reaction_cache_lock = Lock()
        self.last_snipe_cache = {}
        self.last_snipe_cache_lock = Lock()

    @commands.Cog.listener()
    async def on_message_delete(self, message):
        if message.guild is None:
            return

        audit_entry = None

        async for entry in message.guild.audit_logs(limit=1,action=AuditLogAction.message_delete):
            if entry.created_at >= (datetime.now() - timedelta(seconds=300)):
                audit_entry = entry
            else:
                print(f"on_message_delete failed time check {entry.created_at} < {(datetime.now() - timedelta(seconds=300))}: {entry}")

        if audit_entry:
            print(f"on_message_delete audit_entry: {audit_entry}, {audit_entry.target}, {message.author}")

        if not message.author.bot and (not audit_entry or audit_entry.target.id != message.author.id):
            await Sniper.add_to_cache(self.deleted_message_cache, self.deleted_message_cache_lock,
                                      channel=message.channel,
                                      user=message.author,
                                      content=message.content,
                                      extras=message.attachments)

    @commands.Cog.listener()
    async def on_message_edit(self, original_message, edited_message):
        changed_content = original_message.content != edited_message.content
        removed_attachments = [a for a in original_message.attachments if a not in edited_message.attachments]
        if (not original_message.author.bot) and (changed_content or removed_attachments):
            await Sniper.add_to_cache(self.edited_message_cache, self.edited_message_cache_lock,
                                      channel=original_message.channel,
                                      user=original_message.author,
                                      content=original_message.content,  # TODO: Display the text diff more clearly.
                                      extras=removed_attachments)

    @commands.Cog.listener()
    async def on_reaction_remove(self, reaction, user):
        if not user.bot:
            await Sniper.add_to_cache(self.removed_reaction_cache, self.removed_reaction_cache_lock,
                                      channel=reaction.message.channel,
                                      user=user,
                                      content=reaction.emoji,
                                      extras=reaction.message.jump_url)

    @commands.command()
    async def snipe(self, ctx: commands.Context=None, msg: Message=None):
        await self.attempt_snipe(
            msg or ctx.message, self.deleted_message_cache, self.deleted_message_cache_lock, Sniper.send_snipe_response)

    @commands.command(aliases=['esnipe'])
    async def editsnipe(self, ctx: commands.Context=None, msg: Message=None):
        await self.attempt_snipe(
            msg or ctx.message, self.edited_message_cache, self.edited_message_cache_lock, Sniper.send_snipe_response)

    @commands.command(aliases=['rsnipe'])
    async def reactsnipe(self, ctx: commands.Context=None, msg: Message=None):
        await self.attempt_snipe(
            msg or ctx.message, self.removed_reaction_cache, self.removed_reaction_cache_lock, Sniper.send_rsnipe_response)

    @staticmethod
    async def add_to_cache(cache, cache_lock, channel=None, user=None, content=None, extras=None):
        timestamp = datetime.now(timezone.utc)
        async with cache_lock:
            cache.append({
                KEY_TIMESTAMP: timestamp,
                KEY_CHANNEL_ID: channel.id,
                KEY_USER: user,
                KEY_CONTENT: content,
                KEY_EXTRAS: extras
            })

    async def attempt_snipe(self, message, message_cache, message_cache_lock, success_callback):
        channel = message.channel
        sniped_user = None
        sniped_content = []
        sniped_extras = []
        sniped_at = datetime.now(timezone.utc)
        snipe_threshold = sniped_at - SNIPE_WINDOW

        async with message_cache_lock:
            # Remove messages in the cache that were deleted too long ago to be sniped (i.e. outside the snipe window).
            while message_cache and (message_cache[0][KEY_TIMESTAMP] < snipe_threshold):
                message_cache.pop(0)

            # Identify the first user who deleted their messages/reactions in the current channel within the
            # snipe window, and capture ALL deleted messages/reactions within the snipe window by that same user
            # in the current channel.
            cache_index = 0
            while cache_index < len(message_cache):
                cache_entry = message_cache[cache_index]
                if cache_entry[KEY_CHANNEL_ID] == channel.id:
                    # Lock onto a target user if one hasn't already been chosen.
                    if not sniped_user:
                        sniped_user = cache_entry[KEY_USER]
                    # Snipe the message/reaction if it came from the target user.
                    if cache_entry[KEY_USER].id == sniped_user.id:
                        sniped_content.append(cache_entry[KEY_CONTENT])
                        if isinstance(cache_entry[KEY_EXTRAS], list):
                            sniped_extras += cache_entry[KEY_EXTRAS]
                        else:
                            sniped_extras.append(cache_entry[KEY_EXTRAS])
                        message_cache.pop(cache_index)
                        continue  # Continue without incrementing the index because we removed the current entry.
                cache_index += 1

        if sniped_user and sniped_content:
            async with self.last_snipe_cache_lock:
                self.last_snipe_cache[channel.id] = datetime.now(timezone.utc)
            await success_callback(channel, sniped_user, sniped_content, sniped_extras, sniped_at)
        else:
            await Sniper.send_failure_response(message, self.last_snipe_cache.get(channel.id))

    @staticmethod
    async def send_failure_response(message: Message, last_snipe_timestamp: datetime = None):
        slowpoke_threshold = datetime.now(timezone.utc) - SLOWPOKE_WINDOW
        if last_snipe_timestamp and (last_snipe_timestamp > slowpoke_threshold):
            try:
                await message.add_reaction(EMOJI_SLOWPOKE)
            except HTTPException:
                await message.add_reaction(EMOJI_THUMBS_DOWN)
        else:
            embed = create_basic_embed(TEXT_SNIPER_FAIL)
            embed.set_thumbnail(url=URL_SWIPER_ICON)
            await message.channel.send(embed=embed)

    @staticmethod
    async def send_rsnipe_response(channel, user, emojis, message_urls, timestamp):
        # TODO: Handle long emoji lists better. Currently, this will send a separate message for every emoji.
        for i, emoji in enumerate(emojis):
            message_link_string = f'**{get_message_link_string(message_urls[i])}**'
            embed = create_basic_embed(f'Message: {message_link_string}', timestamp=timestamp)

            if isinstance(emoji, str):
                embed.set_author(name=f'{emoji} {user.name}#{user.discriminator}')
            else:
                embed.set_author(name=f'{user.name}#{user.discriminator} with :{emoji.name}:', icon_url=emoji.url)

            await channel.send(embed=embed)

    @staticmethod
    async def send_snipe_response(channel, user, messages, attachments, timestamp):
        embed = create_authored_embed(user, timestamp, '\n'.join(messages).strip())
        file = None

        if attachments and Sniper.is_image(attachments[0]):
            file = await Sniper.attach_image_file(channel, embed, attachments[0])
            attachments.pop(0)

        if not attachments:
            await channel.send(embed=embed, file=file)
            return

        if (not embed.description) and any(not Sniper.is_image(attachment) for attachment in attachments):
            embed.description = TEXT_SENT_FILE if len(attachments) == 1 else TEXT_SENT_FILES

        await channel.send(embed=embed, file=file)

        for attachment in attachments:
            if Sniper.is_image(attachment):
                embed = create_authored_embed(user, timestamp)
                file = await Sniper.attach_image_file(channel, embed, attachment)
                await channel.send(embed=embed, file=file)
            else:
                async with channel.typing():
                    try:
                        file = await attachment.to_file(use_cached=True)
                        await channel.send(file=file)
                    except HTTPException:
                        embed = create_authored_embed(user, timestamp, f'**{attachment.proxy_url}**')
                        await channel.send(embed=embed)

    @staticmethod
    async def attach_image_file(channel, embed, attachment):
        async with channel.typing():
            file = await attachment.to_file(use_cached=True)
            embed.set_image(url=f'attachment://{file.filename}')
        return file

    @staticmethod
    def is_image(attachment):
        return 'image' in attachment.content_type


def setup(bot):
    bot.add_cog(Sniper(bot))
