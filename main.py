import os
import platform
import sys
import discord
import yaml

from discord.ext.commands import Bot
from dotenv import load_dotenv

from TempVoice.temp_voice import TempVoice
from AbuBot.course_cmds import GetCourses
# from RoleAssign.role_assign import RoleAssign
from PinMe.pin_me import PinMe
from VerifyMe.verify_me import VerifyMe
from Miscellaneous.auto_heart import AutoHeart
from Miscellaneous.emoji import Emoji
from Miscellaneous.nqn import NQN

if not os.path.isfile("config.yaml"):
    sys.exit("'config.yaml' not found! Please add it and try again.")
else:
    with open("config.yaml") as file:
        config = yaml.load(file, Loader=yaml.FullLoader)

intents = discord.Intents().all()
bot = Bot(command_prefix=config["bot_prefixes"], intent=intents)


@bot.event
async def on_command_completion(ctx):
    full_command_name = ctx.command.qualified_name
    split = full_command_name.split(" ")
    executed_command = str(split[0])

    try:
        print(f"\nExecuted {executed_command} command in {ctx.guild.name} (ID: {ctx.message.guild.id}) by "
              f"{ctx.message.author} (ID: {ctx.message.author.id})\n")
    except AttributeError:
        print(f"\nExecuted {executed_command} command in DMs by "
              f"{ctx.message.author} (ID: {ctx.message.author.id})\n")


@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.playing, name="on a Raspberry Pi"))

    print("\n-------------------")
    print(f"Bot Token: {os.getenv('BOT_TOKEN')}")
    # print(f"Create a VC channel ID: {config['create_channel_id']}")
    # print(f"Role Assign message ID: {config['role_assign_message_id']}")
    print(f"Discord.py API version: {discord.__version__}")
    print(f"Python version: {platform.python_version()}")
    print(f"Running on: {platform.system()} {platform.release()} ({os.name})")
    print("-------------------\n")


@bot.event
async def on_message(message):

    # Ignore messages made by the bot
    if(message.author == bot.user):
        return

    await bot.process_commands(message)

load_dotenv()

bot.add_cog(TempVoice(bot=bot, vc_channel=config["create_channel_id"]))
bot.add_cog(GetCourses(bot=bot, prefix="."))
bot.add_cog(PinMe(bot=bot, ignore_channels=config["ignore_pin_channels"],
                  admin_channel_id=config["admin_channel_id"], server_id=config["server_id"], verified_role_id=config["verified_role_id"]))
bot.add_cog(VerifyMe(bot=bot, verify_message_id=config["verify_message_id"], unverified_role_id=config["unverified_role_id"], verified_role_id=config["verified_role_id"], email_address=os.getenv('EMAIL_USER'), email_pass=os.getenv('EMAIL_PASS'), server_id=config["server_id"]))
bot.add_cog(AutoHeart(bot=bot, introductions_channel_id=config["introductions_channel_id"]))
bot.add_cog(Emoji(bot=bot))
bot.add_cog(NQN(bot=bot))

# emoji_ids = {'SE': config["se_emoji_id"],
#              'CE': config["ce_emoji_id"],
#              'MG': config["mg_emoji_id"],
#              'SC': config["sc_emoji_id"],
#              'BM': config["bm_emoji_id"],
#              'UP': config["up_emoji_id"],
#              'TA': config["ta_emoji_id"],
#              "BlankI": config["blank_1_id"],
#              "BlankII": config["blank_2_id"],
#              "BlankIII": config["blank_3_id"],
#              "CheckMark": config["check_mark_id"], }
# bot.add_cog(RoleAssign(
#     bot=bot,
#     role_assign_message=config["role_assign_message_id"],
#     role_assign_channel=config["role_assign_channel_id"],
#     emoji_ids=emoji_ids,
#     admin_id=config["admin"]))

bot.run(os.getenv('BOT_TOKEN'))
