from datetime import datetime
import os


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
