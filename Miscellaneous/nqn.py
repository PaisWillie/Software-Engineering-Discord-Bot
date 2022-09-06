from discord.ext import commands
from discord import utils, AllowedMentions

# new regex supports variable length look-behind
# https://pypi.org/project/regex/
import regex as re
from typing import Optional

from addons.prefixed_cog import prefixed_cog
from addons.embed_factory import EmbedFactory


def matches(text : str, pattern):
    '''
    find all instances of pattern expression matches within a string
    
    Args:
        text: string to be parsed (the 'haystack')
        pattern: compiled regex expression (the 'needle')
    Returns:
        list of all regex matches found
    '''

    def search():
        start_idx = 0
        while start_idx < len(text):
            match = pattern.search(text, start_idx)
            if not match:
                break
            
            yield match
            start_idx = match.end()
    
    return list(search())


@prefixed_cog
class NQN(commands.Cog):

    # assume no custom emoji namespace collisions with default emojis
    CUSTOM_EMOJI = re.compile("((?<!<a?))?:(?P<name>\w+):(?(1)|(?!\d+>))")
    # SERVER_EMOJI is unused for now, but could be useful later
    SERVER_EMOJI = re.compile("(?<!\\\)<a?:(?P<name>\w+):(\d+)>")
    MD_SNIPPET = re.compile("(?<!`)(`+)(?!`)([\\s\\S]+?)(?<!`)\\1(?!`)")

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def listnqn(self, ctx):
        '''
        send a message containing currently available NQN emotes
        '''
        server_emojis = set(ctx.guild.emojis)
        all_emojis = sorted(self.bot.emojis, key=lambda x: x.name)
        response = "".join(str(emoji) for emoji in all_emojis
            if emoji not in server_emojis or emoji.animated)
        await ctx.send(embed=EmbedFactory.info(title="NQN Emojis", message=response))

    def get_emoji_repr(self, emoji_name : str) -> Optional[str]:
        '''
        find discord.Emoji object if it exists within any guild we have access to
        if it does exist, return the rendered string representation of it
        assume only single bot instance guild rather than worry about name collision

        Returns:
            discord emoji string representation if it exists in (any) guild,
            otherwise None
        '''
        
        # emoji class dunder str method has format `<(a):name:id>`
        emoji = utils.find(lambda x: x.name.lower() == emoji_name.lower(), self.bot.emojis)
        return None if not emoji else str(emoji)

    def parse_message(self, original_message : str) -> Optional[str]:
        '''
        parses a discord message (string) and replaces animated emoji
        representations with the symbolic version 

        Returns:
            the modified message (string) if an emoji was found,
            otherwise None
        '''

        # O(n) time for each regex match search
        # each expression can require up to O(2^m) space (m = expression size)
        # but I don't suppose that's an issue

        emoji_matches = matches(original_message, NQN.CUSTOM_EMOJI)
        if not emoji_matches:
            # normal message; no need to continue
            return None

        snippet_matches = matches(original_message, NQN.MD_SNIPPET)
        current_snippet = 0

        parsed_message = ""
        last_end_idx = 0
        msg_has_emoji = False

        for emoji_match in emoji_matches:
            emoji_start, emoji_end = emoji_match.span()

            # handle situation where an emoji exists inside of a code snippet
            if current_snippet < len(snippet_matches):
                snippet_match = snippet_matches[current_snippet]
                snippet_start, snippet_end = snippet_match.span()
                
                # catch up to current emoji, no other snippets matter
                while snippet_end <= emoji_start:
                    current_snippet += 1
                    if current_snippet >= len(snippet_matches):
                        break
                    snippet_match = snippet_matches[current_snippet]
                    snippet_start, snippet_end = snippet_match.span()
                
                if snippet_start < emoji_start and emoji_end < snippet_end:
                    # emoji is inside of snippet, skip it and continue
                    parsed_message += original_message[last_end_idx:snippet_end]
                    last_end_idx = snippet_end
                    continue


            parsed_message += original_message[last_end_idx:emoji_start]
            last_end_idx = emoji_end

            # emoji_match pattern should contain a named group called "name"
            named_groups = emoji_match.groupdict()
            assert "name" in named_groups
            emoji_name = named_groups["name"]
            emoji_repr = self.get_emoji_repr(emoji_name)

            if emoji_repr:
                msg_has_emoji = True
                parsed_message += emoji_repr
            else:
                # couldn't find emoji, add it back as plain text
                parsed_message += ":" + emoji_name + ":"
        
        parsed_message += original_message[last_end_idx:]

        return parsed_message if msg_has_emoji else None


    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return

        # ignore replies
        if message.reference:
            return

        # ignore any mentions
        if message.channel_mentions or \
                message.role_mentions or \
                message.mention_everyone or \
                message.mentions:
            return
        
        # double pinging and other related problems are bluntly fixed here

        parsed_message = self.parse_message(message.content)

        if parsed_message:
            webhooks = await message.channel.webhooks()
            webhook = utils.get(webhooks, name = "NQN")
            if not webhook:
                webhook = await message.channel.create_webhook(name = "NQN")

            await webhook.send(
                parsed_message,
                username = message.author.nick if message.author.nick else message.author.name,
                avatar_url = message.author.avatar,
                allowed_mentions = AllowedMentions(
                    users = False,
                    everyone = False,
                    roles = False,
                    replied_user = False,
                ))
            await message.delete()
