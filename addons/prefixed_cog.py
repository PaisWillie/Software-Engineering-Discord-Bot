import yaml
from discord.ext.commands.cog import CogMeta

# TODO: config.yaml file should not need to be opened here.
# default_prefix should be passed in through main, or something
# like a global 'config_reader' singleton could solve this
with open("config.yaml") as file:
    config = yaml.load(file, Loader=yaml.FullLoader)
available_prefixes = config["bot_prefixes"]
default_prefix = available_prefixes[0]


def prefixed_cog(cls : CogMeta) -> CogMeta:
    '''
    Decorates a class extending `discord.ext.commands.Cog` and overrides
    the default cog_check coroutine. This effectively allows for the bot
    to have multiple prefixes, with each cog listening for only it's own
    respective prefix. If no prefix is specified in the constructor then
    the first prefix in the list of prefixes is used (as declared above).

    :example:
    >>> @prefixed_cog
    ... class MyCog(commands.Cog):
    ...     def __init__(self, bot)
    ...         self.bot = bot
    ... 
    >>> MyCog(bot=bot, prefix=".")
    
    '''

    cls_init = cls.__init__
    def __init__(self, prefix = default_prefix, *args, **kwargs):
        if prefix not in available_prefixes:
            raise ValueError("The specified prefix is not a allowed in config.bot_prefixes.")
        cls_init(self, *args, **kwargs)
        self.prefix = prefix

    async def cog_check(self, ctx):
        return ctx.prefix == self.prefix

    cls.__init__ = __init__
    cls.cog_check = cog_check
    return cls