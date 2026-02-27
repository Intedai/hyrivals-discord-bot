import discord
from discord.ext import commands

class HyrivalsBot(commands.Bot):
    user: discord.ClientUser

    def __init__(self, server_id: str = "") -> None:
        intents = discord.Intents.default()
        intents.message_content = True

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

    async def setup_hook(self):
        await self.load_extension("hyrivals_bot.cogs.hyrivals")

        if self.discord_guild:
            self.tree.copy_global_to(guild=self.discord_guild)

        synced = await self.tree.sync(guild=self.discord_guild)
        
        if self.discord_guild:
            print(f"Synced {len(synced)} commands to Guild: <{self.discord_guild.id}>")
        else:
            print(f"Synced {len(synced)} global commands")