import os
import discord
from discord.ext import commands

# --- CONFIG ---
BOT_TOKEN = "YOUR_TOKEN_HERE"

class GhostBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="!", intents=discord.Intents.all())

    async def setup_hook(self):
        # Yahan modules load ho rahe hain
        await self.load_extension("moderation")
        await self.load_extension("utility")
        await self.load_extension("ai_engine")
        await self.load_extension("media")
        await self.load_extension("fun")
        await self.load_extension("welcomer")
        await self.load_extension("order")
        await self.tree.sync()
        print("✅ All Modules Loaded Successfully.")

bot = GhostBot()
bot.run(BOT_TOKEN)
