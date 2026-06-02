from os import getenv
from dotenv import load_dotenv
from .CardGenerator import CardGenerator, ASSETS_PATH
from .HyrivalsApi import PlayerNotFound
from .bot import HyrivalsBot
from .utils import load_config, hex_to_rgb

def main():
    load_dotenv()

    bot_token = getenv("BOT_TOKEN")
    
    if not bot_token:
        raise ValueError("BOT_TOKEN is not set in the .env file")
    
    conf = load_config("config.toml")
    
    server_id = conf["discord"]["server_id"]
    bot_color = conf["colors"]["bot_color"]
    error_color = conf["colors"]["error_color"]
    pfp_bg_color = conf["colors"]["pfp_background_color"]
    pfp_opacity = conf["colors"]["pfp_opacity"]

    if not isinstance(server_id, str):
        raise ValueError("server_id must be a string")
    
    card_gen = CardGenerator(
        card_bg_path = ASSETS_PATH / "card_bg.png",
        hyrivals_logo_path = ASSETS_PATH / "logo.png",
        font_path = ASSETS_PATH / "NunitoSans.ttf",
        font_size = 34,
        color = hex_to_rgb(bot_color),
        pfp_bg_color = hex_to_rgb(pfp_bg_color),
        pfp_opacity = pfp_opacity,
        pfp_size = 256,
        border_size = 15,
        layout_lines = 6
    )

    bot = HyrivalsBot(card_gen, bot_color, error_color, bot_token)
    bot.run(token = bot_token)