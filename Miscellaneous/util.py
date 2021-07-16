from datetime import datetime
from json import loads
from discord import Embed


def log(text: str) -> None:
    """
    Logs given text to file
    """
    now = datetime.now()
    ts = now.timestamp()
    f = open(f"Logs\{now.strftime('%d-%m-%Y')}.log", "a")

    text = str(ts)+"\t"+text+"\n"
    print(text.strip("\n"))

    f.write(text)
    f.close()


def parse_embed_json(json_file):
    embeds_json = loads(json_file)['embeds']

    for embed_json in embeds_json:
        embed = Embed().from_dict(embed_json)
        yield embed


async def send_embeds(ctx, file_path):
        with open(file_path, "r") as file:
            embeds = parse_embed_json(file.read())

            for embed in embeds:
                await ctx.send(embed=embed)