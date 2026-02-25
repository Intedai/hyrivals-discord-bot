from .CardGenerator import CardGenerator, ASSETS_PATH
from .HyrivalsApi import PlayerNotFound

def main():
    card_gen = CardGenerator(
        card_bg_path = ASSETS_PATH / "card_bg.png",
        hyrivals_logo_path = ASSETS_PATH / "logo.png",
        font_path = ASSETS_PATH / "NunitoSans.ttf",
        font_size = 34,
        color = (249, 226, 76),
        pfp_bg_color = (0, 0, 0, 130),
        pfp_size = 256,
        border_size = 15,
        layout_lines = 6
    )
    try:
        user = input("Enter Hytale username: ")
        card_gen.generate_card(user).show()
    except PlayerNotFound:
        print("player not found")
