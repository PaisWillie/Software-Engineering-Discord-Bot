from discord.ext import commands
from discord import utils, AllowedMentions

class NQN(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # FIXME: this method is very error-prone
    def parse_message(self, original_message):
        msg_has_emoji = False

        parsed_message = ""
        
        in_emoji = False

        idx = 0
        message_length = len(original_message)

        while idx < message_length:
            char = original_message[idx]

            # TODO: improve this check
            # worst case O(N^2) if something like '<' * 2000
            if char == '<':
                server_emoji = "<"
                next_char = char
                while idx + len(server_emoji) < message_length and next_char != '>':
                    next_char = original_message[idx + len(server_emoji)]
                    server_emoji += next_char
                
                if server_emoji.endswith(">"):
                    parts = server_emoji[1:-1].split(":")
                    if len(parts) == 3:
                        animated, emoji_name, emoji_id = parts
                        emoji = utils.get(self.bot.emojis, name = emoji_name)
                        if emoji and str(emoji) == server_emoji:
                            idx += len(server_emoji)
                            continue
            
            if char == ':':
                if not in_emoji:
                    in_emoji = True
                    start_idx = idx
                else:
                    in_emoji = False
                    end_idx = idx
                    
                    if end_idx - start_idx < 2:
                        in_emoji = True
                        start_idx = idx
                        parsed_message += char
                    else:
                        # get emoji name from message without colons
                        emoji_name = original_message[start_idx + 1:end_idx]
                        emoji = utils.get(self.bot.emojis, name = emoji_name)
                        if emoji:
                            msg_has_emoji = True
                            parsed_message += str(emoji)
                        else:
                            parsed_message += ":" + emoji_name + ":"
            
            else:
                if not in_emoji:
                    parsed_message += char
            idx += 1
        
        return parsed_message if msg_has_emoji else None


    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return

        parsed_message = self.parse_message(message.content)

        if parsed_message:
            webhooks = await message.channel.webhooks()
            webhook = utils.get(webhooks, name = "NQN")
            if not webhook:
                webhook = await message.channel.create_webhook(name = "NQN")

            await webhook.send(
                parsed_message,
                username = message.author.name,
                avatar_url = message.author.avatar_url,
                allowed_mentions = AllowedMentions(
                    users = False,
                    everyone = False,
                    roles = False,
                    replied_user = False,
                ))
            await message.delete()
