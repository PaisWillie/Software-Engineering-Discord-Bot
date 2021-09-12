import discord
import asyncio
import os
import os.path
import smtplib
from enum import Enum

from random import randint
from email.message import EmailMessage
from VerifyMe.database import Database
from discord.ext import commands

from addons.prefixed_cog import prefixed_cog
from addons.embed_factory import EmbedFactory
from Miscellaneous.util import log


EMBED_GENERIC_ERROR = EmbedFactory.error()
EMBED_MACID_ALREADY_REGISTERED = EmbedFactory.error(message=
    "**This MacID is already registered to another Discord user.**\nPlease contact an Administrator if you believe this is a mistake.")
EMBED_TOO_MANY_TRIES = EmbedFactory.error(message=
    "**Failed too many times.**\nRestart the request by typing `~verify` in chat.")
EMBED_REQUEST_TIMED_OUT = EmbedFactory.error(message=
    "**Your request has timed out**\nRestart the request by typing `~verify` in chat.")
EMBED_OTP_FAIL = EmbedFactory.error(message=
    "**Failed to match OTP, try again.**\nRestart the request by typing `~verify` in chat.")

class OTP_RESULT(Enum):
    SUCCESS = 0
    TIMEOUT = 1
    TOO_MANY = 2

@prefixed_cog
class VerifyMe(commands.Cog):

    def __init__(self, bot, verify_message_id, unverified_role_id, verified_role_id, email_address, email_pass, server_id) -> None:
        self.bot = bot
        self.verify_message_id = verify_message_id
        self.unverified_role_id = unverified_role_id
        self.verified_role_id = verified_role_id
        self.email_address = email_address
        self.email_pass = email_pass
        self.server_id = server_id

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):

        if (payload.message_id != self.verify_message_id) or (
                payload.user_id == self.bot.user.id) or (
                payload.emoji.name != "CheckMark"):
            return

        await self.verify_user(payload.member)

    @commands.command()
    async def verify(self, ctx):
        await self.verify_user(ctx.author)

    async def check_otp(self, member, mac_id, check):
        OTP = ''.join(["{}".format(randint(0, 9)) for _ in range(0, 6)])

        with smtplib.SMTP('smtp.gmail.com', 587) as smtp:

            smtp.ehlo()
            smtp.starttls()
            smtp.ehlo()

            smtp.login(self.email_address, self.email_pass)

            # subject = f"{OTP} is your one-time verification code"
            # body = f"Your one-time verification code is {OTP}\n\nType this code into your direct message chat with the Software Engineering bot."
            # msg = f"Subject: {subject}\n\n{body}"

            msg = EmailMessage()
            msg['Subject'] = f"{OTP} is your one-time verification code"
            msg['From'] = "Software Engineering Bot"
            msg['To'] = f"{mac_id}@mcmaster.ca"
            msg.set_content(
                f"Here is your one-time verification code: {OTP}\n\nType this code into your direct message chat with the Software Engineering bot.")

            smtp.send_message(msg)

        await member.send(f"A one-time verification code has been emailed to you at `{mac_id}@mcmaster.ca`. Ensure you check your spam folder. Please type it in chat:")

        max_tries = 3
        for num_tries in range(1, max_tries+1):
            try:
                user_input = await self.bot.wait_for('message', check=check, timeout=300.0)
            except asyncio.TimeoutError:
                return OTP_RESULT.TIMEOUT

            if user_input.content != OTP:
                if num_tries != max_tries:
                    await member.send("Invalid input, please check your code again and type it in chat:")
            else:
                # verification should occur
                return OTP_RESULT.SUCCESS

        return OTP_RESULT.TOO_MANY

    async def verify_user(self, user):

        guild = self.bot.get_guild(self.server_id)
        verified_role = guild.get_role(self.verified_role_id)
        unverified_role = guild.get_role(self.unverified_role_id)
        member = await guild.fetch_member(user.id)

        if verified_role in member.roles:
            await member.send("You're already verified! Please contact an Administrator if you believe your current roles are a mistake.")
            return

        def check(message):
            return isinstance(message.channel, discord.channel.DMChannel) and message.author.id == member.id

        try:
            data = Database("VerifyMe/users.db")
        except FileNotFoundError as e:
            log(str(e))
            await member.send(embed=EMBED_GENERIC_ERROR)
            return

        await member.send("Type in your MacID in chat:")

        max_tries = 5
        for num_tries in range(1, max_tries+1):

            try:
                user_input = await self.bot.wait_for('message', check=check, timeout=120.0)
            except asyncio.TimeoutError:
                await member.send(embed=EMBED_REQUEST_TIMED_OUT)
                break

            mac_id = user_input.content.lower()

            # user exists in the database
            if mac_id in data:

                # database entry does not have an associated discord account
                if not data[mac_id]["discord_id"]:

                    verify_result = await self.check_otp(member=member, mac_id=mac_id, check=check)
                    if verify_result == OTP_RESULT.SUCCESS:

                        # actual verification of user happens here
                        # if the server and database become out of sync (perhaps by
                        # manually updating one but not the other), problems may occur

                        # in database
                        data[mac_id]["is_verified"] = 1
                        data[mac_id]["discord_name"] = str(member)
                        data[mac_id]["discord_id"] = str(member.id)
                        # in server
                        if unverified_role in member.roles:
                            await member.remove_roles(unverified_role)
                        await member.add_roles(verified_role)

                        # TODO: add other stream specific roles

                        await member.send("Success!")

                    else:
                        if verify_result == OTP_RESULT.TIMEOUT:
                            await member.send(embed=EMBED_REQUEST_TIMED_OUT)
                        elif verify_result == OTP_RESULT.TOO_MANY:
                            await member.send(embed=EMBED_OTP_FAIL)

                elif data[mac_id]["discord_id"] != member.id:
                    await member.send(embed=EMBED_MACID_ALREADY_REGISTERED)
                elif data[mac_id]["discord_id"] == member.id:
                    # If MacID matches, but user does not have Verified role for some reason
                    log(f"{mac_id} tried to verify, but discord id belongs to {member_id}")
                    await member.send(embed=EMBED_GENERIC_ERROR)
                
                return

            else:
                if num_tries != max_tries:
                    await member.send("MacID cannot be found, please re-type your MacID in chat:")
        
        else:
            # if got here, didn't break out of loop
            await member.send(embed=EMBED_TOO_MANY_TRIES)
