import discord
from discord import app_commands
from discord.ext import commands
from io import BytesIO
from hyrivals_bot.bot import HyrivalsBot
from hyrivals_bot.HyrivalsApi import get_player_count, PlayerNotFound

class HyrivalsCommands(commands.Cog):
    def __init__(self, bot: HyrivalsBot) -> None:
        self.bot = bot
    
    @app_commands.command(name="stats", description="Get player stats.")
    async def stats_card(self, interaction: discord.Interaction, player: str):
        await interaction.response.defer(thinking=True)
        try:
            with BytesIO() as image_binary:
                self.bot.card_generator.generate_card(player).save(image_binary, 'PNG')
                image_binary.seek(0)
                await interaction.followup.send(file=discord.File(fp=image_binary, filename=f"{player}.png"))
        except PlayerNotFound:
            await interaction.followup.send("Player not found")
        except Exception as e:
            await interaction.followup.send(f"Failed to get player stats.\nPython: {e}")
    
    @app_commands.command(name="vote", description="Get the daily vote links.")
    async def vote_links(self, interaction: discord.Interaction):
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
    async def player_count(self, interaction: discord.Interaction):
        await interaction.response.defer(thinking=True)

        try:
            data = get_player_count()
            data_representation = [
                ("Player count", data["total"]),
                ("Hub", data["hub"]),
                ("Duels", data["duels"]),
                ("KitPvp", data["kitpvp"])
            ]

            msg = "\n".join(f"🟢 {title}: {count}" for title, count in data_representation)
            embed = self.bot.make_embed("ONLINE PLAYERS", msg)

            await interaction.followup.send(embed=embed)
        except Exception as e:
            await interaction.followup.send(f"Failed to get player count.\nPython: {e}")

async def setup(bot: HyrivalsBot) -> None:
    await bot.add_cog(HyrivalsCommands(bot))
