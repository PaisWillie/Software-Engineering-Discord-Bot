import discord
import asyncio
import json
import os
import os.path
import smtplib

from random import randint
from email.message import EmailMessage

from discord.ext import commands


class VerifyMe(commands.Cog):

    def __init__(self, bot, verify_message_id, verified_role_id, email_address, email_pass, server_id) -> None:
        self.bot = bot
        self.verify_message_id = verify_message_id
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
            msg.set_content(f"Here is your one-time verification code: {OTP}\n\nType this code into your direct message chat with the Software Engineering bot.")

            smtp.send_message(msg)

        await member.send(f"A one-time verification code has been emailed to you at `{mac_id}@mcmaster.ca`. Ensure you check your spam folder. Please type it in chat:")

        user_input = None

        while not user_input:

            try:
                user_input = await self.bot.wait_for('message', check=check, timeout=300.0)
            except asyncio.TimeoutError:
                await member.send("Your request has timed out. Restart the request by typing `~verify` in chat.")
                return

            if user_input.content != OTP:
                await member.send("Invalid input, please check your code again and type it in chat:")
                msg = None

        return True

    async def verify_user(self, user):

        guild = self.bot.get_guild(self.server_id)
        role = guild.get_role(self.verified_role_id)
        member = await guild.fetch_member(user.id)

        if role in member.roles:
            await member.send("You're already verified! Please contact an Administrator if you believe your current roles are a mistake.")
            return

        def check(message):
            return isinstance(message.channel, discord.channel.DMChannel) and message.author.id == member.id

        if not os.path.isfile('VerifyMe/data.json'):
            print("data.json file could not be found")
            await member.send("An error has occured. Please contact an Administrator")
            return

        # Reading data from JSON file
        with open('VerifyMe/data.json', 'r') as file:
            data = json.loads(file.read())

        await member.send("Type in your MacID in chat:")

        user_input = None
        
        while not user_input:

            try:
                user_input = await self.bot.wait_for('message', check=check, timeout=120.0)
            except asyncio.TimeoutError:
                await member.send("Your request has timed out. Restart the request by typing `~verify` in chat.")
                return

            mac_id = user_input.content.lower()

            if mac_id in data:

                # await member.send("MacID found!")

                if not data[mac_id]["discord_id"]:

                    if await self.check_otp(member=member, mac_id=mac_id, check=check):
                        await member.send("Success!")

                elif data[mac_id]["discord_id"] != member.id:
                    await member.send("This MacID is already registered to another Discord user. Please contact an Administrator if you believe this is a mistake.")
                elif data[mac_id]["discord_id"] == member.id:
                    # If MacID matches, but user does not have Verified role for some reason
                    pass

            else:
                await member.send("MacID cannot be found, please re-type your MacID in chat:")
                msg = None

        # Writing data to JSON file
        with open('VerifyMe/data.json', 'w') as file:
            json.dump(data, file)
