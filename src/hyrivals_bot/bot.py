import discord
from discord.ext import commands
from .CardGenerator import CardGenerator

HYRIVALS_IP = "play.hyrivals.gg"
HYRIVALS_PNG_URL = "https://hyrivals.gg/logo.png"

class HyrivalsBot(commands.Bot):
    user: discord.ClientUser

    def __init__(self, card_generator: CardGenerator, embed_color = 0xFFF, server_id: str = "") -> None:
        intents = discord.Intents.default()
        intents.message_content = True

        self.card_generator = card_generator
        self.embed_color = embed_color

        super().__init__(
            command_prefix = "!",
            intents = intents,
            activity = discord.Game(name="/test for now")
        )
        
        if server_id and server_id.isdigit():
            self.discord_guild = discord.Object(id=str(server_id))
        else:
            self.discord_guild = None

    async def on_ready(self) -> None:
        print(f'Logged in as {self.user}: <{self.user.id}>')

    async def setup_hook(self) -> None:
        await self.load_extension("hyrivals_bot.cogs.hyrivals_commands")

        if self.discord_guild:
            self.tree.copy_global_to(guild=self.discord_guild)

        synced = await self.tree.sync(guild=self.discord_guild)
        
        if self.discord_guild:
            print(f"Synced {len(synced)} commands to Guild: <{self.discord_guild.id}>")
        else:
            print(f"Synced {len(synced)} global commands")

    def make_embed(self, title: str, msg: str) -> discord.Embed:
        embed = discord.Embed(title=title, description=msg, color=self.embed_color)
        embed.set_author(name=HYRIVALS_IP, icon_url=HYRIVALS_PNG_URL)

        return embed