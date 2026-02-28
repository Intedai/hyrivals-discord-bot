from os import getenv
from dotenv import load_dotenv
from .CardGenerator import CardGenerator, ASSETS_PATH
from .HyrivalsApi import PlayerNotFound
from .bot import HyrivalsBot

def main():
    load_dotenv()

    BOT_TOKEN = getenv("BOT_TOKEN")
    SERVER_ID = getenv("SERVER_ID")

    if not BOT_TOKEN:
        raise ValueError("BOT_TOKEN is not set in the .env file")

    bot_color = (249, 226, 76)
    bot_color_int = bot_color[0] << 16 | bot_color[1] << 8 | bot_color[2]
    error_color_int = 0xCC322A

    card_gen = CardGenerator(
        card_bg_path = ASSETS_PATH / "card_bg.png",
        hyrivals_logo_path = ASSETS_PATH / "logo.png",
        font_path = ASSETS_PATH / "NunitoSans.ttf",
        font_size = 34,
        color = bot_color,
        pfp_bg_color = (0, 0, 0, 130),
        pfp_size = 256,
        border_size = 15,
        layout_lines = 6
    )

    bot = HyrivalsBot(card_gen, bot_color_int, error_color_int, SERVER_ID)
    bot.run(token=BOT_TOKEN)