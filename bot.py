import discord
from discord.ext import commands, tasks
import os

from dotenv import load_dotenv
from util.db import get_all_trackers, update_uuid_data
from util.requests import Web

from constants import bot_owner_id

load_dotenv()

TOKEN = os.getenv('TOKEN')

class Bot(commands.Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.command_prefix = "!"
        self.load_cogs()

        self.owner_id = bot_owner_id
        self.web = Web()

    async def on_ready(self):
        print(f'Logged in as {self.user}')

        self.track_bestiary.start()
        print("Started Bestiary Tracking")

    def load_cogs(self):
        for filename in os.listdir('./cogs'):
            if filename.endswith('.py'):
                self.load_extension(f'cogs.{filename[:-3]}')
                print(f'Loaded {filename[:-3]}')

    @tasks.loop(seconds=60)
    async def track_bestiary(self):
        trackers = get_all_trackers()
        for tracker in trackers:

            uuid = tracker["uuid"]
            profile = await self.web.get_selected_profile(tracker["uuid"])

            if not profile:
                continue

            player_data = profile["members"][uuid]

            bestiary_data = player_data.get("bestiary", {}).get("kills", {})

            scatha_kills = bestiary_data.get("scatha_10", 0)
            worm_kills = bestiary_data.get("worm_5", 0)

            update_uuid_data(uuid, scatha_kills, worm_kills)


        print("Tracking Bestiary")



activity = discord.CustomActivity(name="scatha on top.")

intents = discord.Intents.default()
intents.members = True

bot = Bot(command_prefix="!", activity=activity, intents=intents)
bot.run(TOKEN)
