import discord
from discord.ext import commands

class AutoHeart(commands.Cog):

    def __init__(self, bot, introductions_channel_id) -> None:
        self.bot = bot
        self.introductions_channel_id = introductions_channel_id

    @commands.Cog.listener()
    async def on_message(self, message) -> None:
        
        if message.channel.id != self.introductions_channel_id:
            return

        if "name" not in message.content.lower():
            return

        # self.bot.get_emoji()

        await message.add_reaction("💜")
