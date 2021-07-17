from discord.ext import commands

class TempVoice(commands.Cog):
    
    def __init__(self, bot, vc_channel) -> None:
        self.bot = bot
        self.vc_channel = vc_channel
        self.channels : list[str] = []

    @commands.Cog.listener()
    async def on_voice_state_update(self,member, before, after):

        await self.check_channels(member, before.channel, after.channel)

    async def create_channel(self, member, category):

        # Generates new group channel with group #
        new_channel = await category.create_voice_channel(f"{member.name}'s Channel")

        # Adds newly generated channel id to lists
        self.channels.append(new_channel.id)

        # Move user to newly created voice channel
        await member.move_to(new_channel)

        print(f"{new_channel.name} created")


    async def check_after_channels(self, member, after_channel):

        # Checks if channel joined the "Create a VC" channel
        if after_channel.id == self.vc_channel:
            print(f'{member.name} joined the "Create a VC" channel')
            await self.create_channel(member, after_channel.category)


    async def check_before_channels(self, before_channel):

        # Check if channel should be deleted and is empty
        if before_channel.id in self.channels and len(self.bot.get_channel(before_channel.id).members) == 0:
            self.channels.remove(before_channel.id)

            # Delete empty channel
            await self.bot.get_channel(before_channel.id).delete()

            print(f"{before_channel.name} deleted")


    async def check_channels(self, member, before_channel, after_channel):

        # Checks if channel left exists
        if before_channel is not None:
            await self.check_before_channels(before_channel)

        # Checks if channel joined exists
        if after_channel is not None:
            await self.check_after_channels(member, after_channel)
