import discord
from discord.ext import commands
from .CardGenerator import CardGenerator
from .HyrivalsApi import get_player_count
from discord.ext import tasks

HYRIVALS_IP = "play.hyrivals.gg"
HYRIVALS_PNG_URL = "https://hyrivals.gg/logo.png"

class HyrivalsBot(commands.Bot):
    user: discord.ClientUser

    def __init__(self, card_generator: CardGenerator, embed_color = 0xFFF, embed_error_color = 0xFF0000, server_id: str = "") -> None:
        intents = discord.Intents.default()
        intents.message_content = True

        self.card_generator = card_generator
        self.embed_color = embed_color
        self.embed_error_color = embed_error_color

        super().__init__(
            # No command prefixes, only slash commands
            command_prefix = [],
            help_command=None,
            intents = intents,
        )
        
        if server_id and server_id.isdigit():
            self.discord_guild = discord.Object(id=str(server_id))
        else:
            self.discord_guild = None
        
    async def on_ready(self) -> None:
        print(f'Logged in as {self.user}: <{self.user.id}>')

    # Bot's activity:
    @tasks.loop(seconds=60)
    async def update_activity(self):
        try:
            total_players = get_player_count()["total"]
            activity = f"🟢 {total_players} ONLINE"
            await self.change_presence(activity=discord.Game(name = activity))
            print(f"Activity updated to: {activity}")
        except Exception as e:
            print(f"Failed to update activity: {e}")
    
    @update_activity.before_loop
    async def before_update_activity(self):
        await self.wait_until_ready()

    async def setup_hook(self) -> None:
        await self.load_extension("hyrivals_bot.cogs.hyrivals_commands")

        if self.discord_guild:
            self.tree.copy_global_to(guild=self.discord_guild)

        synced = await self.tree.sync(guild=self.discord_guild)
        
        if self.discord_guild:
            print(f"Synced {len(synced)} commands to Guild: <{self.discord_guild.id}>")
        else:
            print(f"Synced {len(synced)} global commands")
        
        # Start the activity loop
        self.update_activity.start()

    def make_embed(self, title: str, msg: str, is_error = False) -> discord.Embed:
        color = self.embed_color if not is_error else self.embed_error_color

        embed = discord.Embed(title=title, description=msg, color=color)
        embed.set_author(name=HYRIVALS_IP, icon_url=HYRIVALS_PNG_URL)

        return embed