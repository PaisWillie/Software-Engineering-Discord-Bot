import discord
from discord.ext import commands

class PinMe(commands.Cog):

    def __init__(self, bot, ignore_channels, admin_channel_id, server_id, verified_role_id) -> None:
        self.bot = bot
        self.ignore_channels = ignore_channels
        self.admin_channel_id = admin_channel_id
        self.server_id = server_id
        self.verified_role_id = verified_role_id

    @commands.Cog.listener()
    async def on_ready(self):
        self.admin_channel = await self.bot.fetch_channel(self.admin_channel_id)

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        
        if payload.user_id == self.bot.user.id:
            return

        if payload.channel_id in self.ignore_channels:
            return

        if payload.emoji.name == "📌":

            channel = self.bot.get_channel(payload.channel_id)
            message = await channel.fetch_message(payload.message_id)

            guild = self.bot.get_guild(self.server_id)
            role = guild.get_role(self.verified_role_id)

            for reaction in message.reactions:
                if reaction.emoji == "📌":

                    count = 0

                    users = await reaction.users().flatten()

                    for user in users:
                        member = await guild.fetch_member(user.id)
                        if role in member.roles:
                            count += 1
                        
                            if count >= 10:
                                await message.pin()
                                print(f"Pinning {message.id} in #{guild.get_channel(payload.channel_id).name}")
                                embed = discord.Embed(title=f"Message Pinned in #{channel.name}", color=discord.Color.purple(), description=f"*{message.content}*\n—[{payload.member.name}]({message.jump_url})")
                                await self.admin_channel.send(embed=embed)
                                # await self.admin_channel.send(f"Pinning {message.jump_url} in #{channel.name}")
                                break