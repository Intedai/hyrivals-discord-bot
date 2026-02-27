import discord
from discord import app_commands
from discord.ext import commands
from hyrivals_bot.bot import HyrivalsBot

class HyrivalsCommands(commands.Cog):
    def __init__(self, bot: HyrivalsBot) -> None:
        self.bot = bot
    
    @app_commands.command(name="test", description="test.")
    async def test(self, interaction: discord.Interaction):
        await interaction.response.send_message("Test")

async def setup(bot: HyrivalsBot) -> None:
    await bot.add_cog(HyrivalsCommands(bot))
