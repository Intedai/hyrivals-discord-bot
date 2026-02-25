from PIL import Image, ImageOps, ImageDraw, ImageFont
from urllib.request import urlopen, Request
from pathlib import Path
from hyrivals_bot.HyrivalsApi import get_stats

ASSETS_PATH = Path(__file__).resolve().parent.parent / "assets"

class CardGenerator:
    def __init__(
        self,
        card_bg_path: Path,
        hyrivals_logo_path: Path,
        font_path: Path,
        font_size: int,
        color: tuple[int, int, int],
        pfp_bg_color: tuple[int, int, int],
        pfp_size: int,
        border_size: int,
        layout_lines: int
    ) -> None:

        self.card_bg = Image.open(card_bg_path)
        self.card_bg = ImageOps.expand(self.card_bg, border_size, fill=color)
        self.card_width, self.card_height = self.card_bg.size

        # X values of the start and end and the dimensions of the stats box
        self.after_pfp = pfp_size+border_size*2
        self.before_border = self.card_width - border_size - 1
        self.box_width = self.before_border - self.after_pfp + 1
        self.box_height = self.card_bg.size[1] - border_size * 2

        self.hyrivals_logo = Image.open(hyrivals_logo_path)
        self.hyrivals_logo_width, self.hyrivals_logo_height = self.hyrivals_logo.size

        self.font = ImageFont.truetype(font_path, font_size)
        self.font.set_variation_by_name("ExtraBold")

        self.color = color
        self.pfp_bg_color = pfp_bg_color
        self.pfp_size = pfp_size
        self.border_size = border_size
        self.layout_lines = layout_lines

    def _get_skin_img(self, username: str) -> Image.Image:

        url = f"https://hyvatar.io/render/{username}?size={self.pfp_size}"
        return Image.open(urlopen(Request(url, headers={'User-Agent': 'Mozilla/5.0'})))

    def _make_pfp_img(self, username: str) -> Image.Image:

        pfp_img = Image.new("RGBA", (self.pfp_size,self.pfp_size), color=self.pfp_bg_color)
        skin_img = self._get_skin_img(username)
        pfp_img.alpha_composite(skin_img, (0,0))
        pfp_img.alpha_composite(self.hyrivals_logo, (0,self.pfp_size - self.hyrivals_logo_height))
        pfp_img = ImageOps.expand(pfp_img, self.border_size, fill=self.color)
        
        return pfp_img
    
    def _get_text_size(self, draw: ImageDraw.ImageDraw, text: str) -> tuple[int, int]:

        _, _, username_width, username_height = draw.textbbox((0, 0), text, font=self.font)
        return (username_width ,username_height)

    def _draw_text(self, draw: ImageDraw.ImageDraw, text: str, pos: tuple[int, int]):

        draw.text(pos,text,(0,0,0),font=self.font, stroke_width=self.border_size // 2 - 3,stroke_fill=self.color)
    
    def _build_layout(
        self,
        username: str,
        wins: int,
        losses: int,
        winrate: int,
        kills: int,
        deaths: int,
        kd: int,
        elo: int
    ) -> list:

        return [
            [([username], 'm')],
            [(["Duels"], 'm'), (["KitPVP"], 'm')],
            # Long line but easier to understand like that:
            [([f"Wins: {wins}", f"Losses: {losses}", f"Winrate: {winrate}"],'l'), ([f"Kills: {kills}", f"Deaths: {deaths}", f"K/D: {kd}"],'l')],
            [([f"Elo: {elo}"], 'm')]
        ]

    def _generate_card(
        self,
        username: str,
        wins: int,
        losses: int,
        winrate: int,
        kills: int,
        deaths: int,
        kd: int,
        elo: int
    ) -> Image.Image:

        username = username.upper()
        card_bg = self.card_bg.copy()
        pfp_img = self._make_pfp_img(username)

        card_bg.alpha_composite(pfp_img, (0,0))

        draw = ImageDraw.Draw(card_bg)

        layout = self._build_layout(username, wins, losses, winrate, kills, deaths, kd, elo)

        y_pos = self.border_size
        height_inc = self.box_height / self.layout_lines
        max_lines = 0

        for row in layout:
            cols = len(row)
            col_width = self.box_width // cols


            max_lines = max(len(col[0]) for col in row)

            for x_idx, (text_list, _) in enumerate(row):
                x_base = self.after_pfp + col_width * x_idx
                for y_idx, text in enumerate(text_list):
                    t_width, _ = self._get_text_size(draw, text)
                    x = x_base + (col_width - t_width) / 2
                    y = y_pos + height_inc * y_idx
                    self._draw_text(draw, text, (x, y))
            y_pos += height_inc * max_lines


        return card_bg
    
    def generate_card(self, username: str) -> Image.Image:

        player_duels = get_stats(username, "duels")
        player_kitpvp = get_stats(username, "kitpvp")

        kitpvp_kills = player_kitpvp["kills"]
        kitpvp_deaths = player_kitpvp["deaths"]
        # Round to 2 dig after decimal point and avoid dividing by 0
        kitpvp_kd = round(kitpvp_kills / (kitpvp_deaths if kitpvp_deaths > 0 else 1), 2)
        
        return self._generate_card(
            username,
            player_duels["wins"],
            player_duels["losses"],
            player_duels["winRate"],
            kitpvp_kills, kitpvp_deaths,
            kitpvp_kd, player_duels["elo"]
        )