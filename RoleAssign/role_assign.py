import discord
from discord.ext import commands
from discord.raw_models import RawReactionActionEvent


class RoleAssign(commands.Cog):

    def __init__(self, bot, role_assign_message: int, role_assign_channel: int, emoji_ids, admin_id: int, stream_message_id: int, specialty_message_id: int, miscellaneous_message_id: int) -> None:
        self.bot = bot
        self.role_assign_message = role_assign_message
        self.emoji_ids = emoji_ids
        self.role_assign_channel = role_assign_channel
        self.admin_id = admin_id

        # TODO: Add message IDs for stream, specialties, misc, 
        self.stream_message_id = stream_message_id
        self.specialty_message_id = specialty_message_id
        self.miscellaneous_message_id = miscellaneous_message_id

    # TODO: Check for unverified and verified roles
    # TODO: Prevent verified roles from reacting and unreacting to lose role

    @commands.command()
    async def setuproles(self, ctx):

        if ctx.author.id != self.admin_id:
            return

        channel = self.bot.get_channel(self.role_assign_channel)
        message = await channel.fetch_message(self.role_assign_message)

        setup_emojis = ('SE', 'CE', "BlankI", 'MG', 'SC',
                        'BM', "BlankII", 'UP', 'TA', "BlankIII", "CheckMark")

        for emoji_name in setup_emojis:

            emoji = self.bot.get_emoji(self.emoji_ids[emoji_name])
            await message.add_reaction(emoji)

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):

        # TODO: Check if verified, if so, remove reaction and return None

        if (payload.message_id != self.role_assign_message) or (
                payload.user_id == self.bot.user.id):
            return
        # TODO: Remove CheckMark when verification is implemented
        blanks = ["BlankI", "BlankII", "BlankIII", "CheckMark"]
        streams = ['SE', 'CE']
        specialties = ['MG', 'SC', 'BM']
        misc = ['UP', 'TA']

        guild = self.bot.get_guild(payload.guild_id)
        member = await guild.fetch_member(payload.user_id)

        # TODO: If reacted a blank, remove reaction and return None
        if payload.emoji.name in blanks:
            channel = self.bot.get_channel(payload.channel_id)
            message = await channel.fetch_message(payload.message_id)
            emoji = self.bot.get_emoji(self.emoji_ids[payload.emoji.name])
            user = await self.bot.fetch_user(payload.user_id)

            await message.remove_reaction(emoji, user)

        elif payload.emoji.name in streams:
            await self.add_stream(payload, guild, member)

        elif payload.emoji.name in specialties:
            await self.add_specialty(payload, guild, member)

        elif payload.emoji.name in misc:
            await self.add_misc(payload, guild, member)

        else:
            print(
                f"{payload.member.name} reacted with the invalid emoji, '{payload.emoji.name}'")

    async def add_stream(self, payload: RawReactionActionEvent, guild, member):

        role_names = {'SE': "Software Student", 'CE': "Computer Student"}

        role = discord.utils.get(
            guild.roles, name=role_names[payload.emoji.name])

        if member is not None and role is not None:
            await member.add_roles(role)
            print(f"Assigned {role.name} to {member.name}")

            channel = self.bot.get_channel(payload.channel_id)
            message = await channel.fetch_message(payload.message_id)
            user = await self.bot.fetch_user(payload.user_id)

            roles_to_remove = list(role_names.keys())
            roles_to_remove.remove(payload.emoji.name)

            for current_emoji in roles_to_remove:

                emoji = self.bot.get_emoji(self.emoji_ids[current_emoji])

                await message.remove_reaction(emoji, user)

        elif member is not None:
            print(f"Failed to give Unknown Role to {member.name}")

        elif role is not None:
            print(f"Failed to give {role.name} to Unknown Member")

        else:
            print(f"Failed to give Unknown Role to Unknown Member")

    async def add_specialty(self, payload: RawReactionActionEvent, guild, member):

        role_names = {'MG': "Management", 'SC': "Society", 'BM': "Biomedical"}

        role = discord.utils.get(
            guild.roles, name=role_names[payload.emoji.name])

        if member is not None and role is not None:
            await member.add_roles(role)
            print(f"Assigned {role.name} to {member.name}")

            channel = self.bot.get_channel(payload.channel_id)
            message = await channel.fetch_message(payload.message_id)
            user = await self.bot.fetch_user(payload.user_id)

            roles_to_remove = list(role_names.keys())
            roles_to_remove.remove(payload.emoji.name)

            for current_emoji in roles_to_remove:

                emoji = self.bot.get_emoji(self.emoji_ids[current_emoji])

                await message.remove_reaction(emoji, user)

        elif member is not None:
            print(f"Failed to give Unknown Role to {member.name}")

        elif role is not None:
            print(f"Failed to give {role.name} to Unknown Member")

        else:
            print(f"Failed to give Unknown Role to Unknown Member")

    async def add_misc(self, payload: RawReactionActionEvent, guild, member):

        role_names = {'UP': "Upper Year", 'TA': "TA"}

        role = discord.utils.get(
            guild.roles, name=role_names[payload.emoji.name])

        if member is not None and role is not None:
            await member.add_roles(role)
            print(f"Assigned {role.name} to {member.name}")

        elif member is not None:
            print(f"Failed to give Unknown Role to {member.name}")

        elif role is not None:
            print(f"Failed to give {role.name} to Unknown Member")

        else:
            print(f"Failed to give Unknown Role to Unknown Member")

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload):

        # TODO: Check if verified, if so, add reaction back and return None

        if payload.message_id != self.role_assign_message:
            return

        if payload.user_id == self.bot.user.id:
            return

        role_names = {'SE': "Software Student",
                      'CE': "Computer Student",
                      'MG': "Management",
                      'SC': "Society",
                      'BM': "Biomedical",
                      'UP': "Upper Year",
                      'TA': "TA"}

        if payload.emoji.name in role_names:

            guild = self.bot.get_guild(payload.guild_id)
            member = await guild.fetch_member(payload.user_id)

            role = discord.utils.get(
                guild.roles, name=role_names[payload.emoji.name])
            await member.remove_roles(role)

            print(f"Removed {role.name} from {member.name}")
