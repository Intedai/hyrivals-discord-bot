import discord
from discord import app_commands
from discord.ext import commands
from io import BytesIO
from typing import Literal
from hyrivals_bot.bot import HyrivalsBot
from hyrivals_bot.HyrivalsApi import get_player_count, PlayerNotFound, get_leaderboard

class HyrivalsCommands(commands.Cog):
    def __init__(self, bot: HyrivalsBot) -> None:
        self.bot = bot
    
    @app_commands.command(name="stats", description="Get player stats.")
    async def stats_card(self, interaction: discord.Interaction, player: str) -> None:
        await interaction.response.defer(thinking=True)
        title = "PLAYER STATS"
        try:
            with BytesIO() as image_binary:
                self.bot.card_generator.generate_card(player).save(image_binary, 'PNG')
                image_binary.seek(0)
                await interaction.followup.send(file=discord.File(fp=image_binary, filename=f"{player}.png"))
        except PlayerNotFound:
            await interaction.followup.send(embed=self.bot.make_embed(
                title,
                "Player not found.",
                is_error=True
            ))
        except Exception as e:
            await interaction.followup.send(embed=self.bot.make_embed(
                title,
                f"Failed to get player stats.\nPython: {e}",
                is_error=True
            ))
    
    @app_commands.command(name="vote", description="Get the daily vote links.")
    async def vote_links(self, interaction: discord.Interaction) -> None:
        links = [
            ("Hytale Online Servers", "https://hytaleonlineservers.com/server-hyrivals-live-pvp-arena.344"),
            ("Hytale Server List", "https://hytaleserverlist.me/server/hyrivals.49013"),
            ("Hytale Hub", "https://hytalehub.com/groups/hyrivals.241/feeds"),
            ("Hytale Serverlist", "https://hytale-serverlist.com/servers/server-details/6965b2170d30cb04d56dbe10"),
            ("Top Games", "https://top-games.net/hytale/hyrivals"),
            ("Hytale Servers", "https://hytaleservers.org/server/hyrivals.45"),
            ("Hytale Universe", "https://hytale-universe.com/?server=gZLnk5HVwbmWm9TrNd7X")
        ]
        
        msg = "\n".join(f"* [{name}]({link})" for name, link in links)

        embed = self.bot.make_embed("DAILY VOTE LINKS", msg)
        
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="online", description="Show detailed player count.")
    async def player_count(self, interaction: discord.Interaction) -> None:
        await interaction.response.defer(thinking=True)
        title = "ONLINE PLAYERS"
        try:
            data = get_player_count()
            data_representation = [
                ("Player count", data["total"]),
                ("Hub", data["hub"]),
                ("Duels", data["duels"]),
                ("KitPvp", data["kitpvp"])
            ]

            msg = "\n".join(f"🟢 {title}: {count}" for title, count in data_representation)

            await interaction.followup.send(embed=self.bot.make_embed(title, msg))
        except Exception as e:
            await interaction.followup.send(embed=self.bot.make_embed(
                title,
                f"Failed to get player count.\nPython: {e}",
                is_error=True
            ))

    class LeaderboardButtons(discord.ui.View):
        def __init__(self, *, interaction: discord.Interaction, start_page: int, max_page: int, embed_func: callable, timeout: float = 180.0):
            self.page = start_page
            self.max_page = max_page
            self.embed_func = embed_func
            self.paginate_btns = lambda : self.update_buttons(self.page == 1, self.page == self.max_page)
            self.command_executor = interaction.user
            self.message = None

            super().__init__(timeout=timeout)

        async def interaction_check(self, interaction: discord.Interaction) -> bool:
            if interaction.user != self.command_executor:
                await interaction.response.send_message("You should run /leaderboard on your own!", ephemeral=True)
                return False
            return True

        async def on_timeout(self) -> None:
            self.update_buttons(True, True)
            if self.message:
                await self.message.edit(view=self)
    
        @discord.ui.button(emoji="◀️", style=discord.ButtonStyle.blurple, disabled=True)
        async def back(self, interaction: discord.Interaction, button: discord.ui.Button):
            await interaction.response.defer()

            self.page = max(self.page - 1, 1)
            self.paginate_btns()

            await interaction.edit_original_response(embed=self.embed_func(self.page), view=self)

        @discord.ui.button(emoji="▶️", style=discord.ButtonStyle.blurple)
        async def forward(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
            await interaction.response.defer()

            self.page = min(self.page + 1,self.max_page)
            self.paginate_btns()

            await interaction.edit_original_response(embed=self.embed_func(self.page), view=self)

        def update_buttons(self, back_disabled: bool, forward_disabled: bool) -> None:
            for child in self.children:
                if isinstance(child, discord.ui.Button) and str(child.emoji) == "◀️":
                    child.disabled = back_disabled
                elif isinstance(child, discord.ui.Button) and str(child.emoji) == "▶️":
                    child.disabled = forward_disabled

    @app_commands.command(name="leaderboard", description="Hyrivals ranked leaderboard.")
    async def leaderboard(self, interaction: discord.Interaction, mode: Literal["duels", "kitpvp"]) -> None:
        await interaction.response.defer(thinking=True)
        title = "LEADERBOARD"
        max_page: int

        def leader_board_embed(page: int) -> discord.Embed:
            leaderboard = get_leaderboard(page, 10, mode)
            nonlocal max_page
            max_page = leaderboard["pagination"]["totalPages"]

            if mode == "duels":
                entries = "\n".join(
                    f"**{entry["rank"]}. {entry["username"]}** ELO: {entry["elo"]} | RANK: {entry["eloRank"]} | WINS: {entry["wins"]}/{entry["gamesPlayed"]}"
                    for entry in leaderboard["entries"]
                )
            else:
                entries = "\n".join(
                    f"**{entry["rank"]}. {entry["username"]}** KD: {entry["kd"]} | KILLS: {entry["kills"]} | DEATHS: {entry["deaths"]}"
                    for entry in leaderboard["entries"]
                )                

            embed = self.bot.make_embed(title, msg=entries)
            embed.set_footer(text=f"PAGE: [ {leaderboard["pagination"]["page"]} / {max_page} ]") 
            
            return embed

        try:
            await interaction.followup.send(embed=leader_board_embed(1), view = (btns := self.LeaderboardButtons(
                interaction=interaction,
                start_page=1,
                max_page=max_page,
                embed_func=leader_board_embed
            )))
            btns.message = await interaction.original_response()
        except Exception as e:
            await interaction.followup.send(embed=self.bot.make_embed(
                title,
                f"Failed to get leaderboard.\nPython: {e}",
                is_error=True
            ))


async def setup(bot: HyrivalsBot) -> None:
    await bot.add_cog(HyrivalsCommands(bot))
