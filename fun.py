import discord
import random
import asyncio
from discord.ext import commands
from discord import app_commands
from discord.ui import Button, View

# --- GIF DICTIONARIES (Professional Anime & Thematic GIFs) ---
ACTION_GIFS = {
    "hug": ["https://media.giphy.com/media/od5H3PmEG5EVq/giphy.gif", "https://media.giphy.com/media/3M4NpbLCTxBqU/giphy.gif"],
    "kiss": ["https://media.giphy.com/media/G3va31oEEnIkM/giphy.gif", "https://media.giphy.com/media/FqWAhOpmIeXp6/giphy.gif"],
    "slap": ["https://media.giphy.com/media/Zau0yrl17uzdK/giphy.gif", "https://media.giphy.com/media/jLeyZWgtwgr2U/giphy.gif"],
    "pat": ["https://media.giphy.com/media/L2z7dnOduqEow/giphy.gif", "https://media.giphy.com/media/10VjiVoa9rWC4M/giphy.gif"],
    "kill": ["https://media.giphy.com/media/11HeubLHnQJSAU/giphy.gif", "https://media.giphy.com/media/OThoA1wBv559C/giphy.gif"],
    "marry": ["https://media.giphy.com/media/xT0xezwG1rG6tGz4xG/giphy.gif", "https://media.giphy.com/media/m3864rBwwBToc/giphy.gif"],
    "bite": ["https://media.giphy.com/media/132R5wIiyRNGkE/giphy.gif", "https://media.giphy.com/media/OqQvwj5veebG8/giphy.gif"],
    "cry": ["https://media.giphy.com/media/8YutMatqkTfEE/giphy.gif", "https://media.giphy.com/media/ROF8OQvDmxXIQ/giphy.gif"],
    "dance": ["https://media.giphy.com/media/mXnO9IiWWarkI/giphy.gif", "https://media.giphy.com/media/14g1qJEjiKCiGc/giphy.gif"],
    "blush": ["https://media.giphy.com/media/1GTZA4flUzQI0/giphy.gif", "https://media.giphy.com/media/8YZpVrJhtP7m1SroK2/giphy.gif"]
}

SYS_GIFS = {
    "hack": "https://media.giphy.com/media/YQitE4YNQxWuM/giphy.gif",
    "ship_high": "https://media.giphy.com/media/26BRv0ThflsHCqDrG/giphy.gif",
    "ship_low": "https://media.giphy.com/media/EZICHGrSD5QE/giphy.gif",
    "8ball": "https://media.giphy.com/media/efahzan109oWdMRKnH/giphy.gif",
    "roll": "https://media.giphy.com/media/3oKIPnAiaCRiSzaTFC/giphy.gif",
    "flip": "https://media.giphy.com/media/m3ZpIlxs2Pfv2/giphy.gif",
    "rps_win": "https://media.giphy.com/media/9wGjpl8z1CJ5m/giphy.gif",
    "rps_lose": "https://media.giphy.com/media/xT9DPBMumj2Q0hlI3K/giphy.gif",
    "rps_tie": "https://media.giphy.com/media/3o7TKM84kQZz06XQTC/giphy.gif",
    "roast": "https://media.giphy.com/media/RdKjAkFTNZkWUGyRXF/giphy.gif"
}

# --- INTERACTIVE RPS VIEW ---
class RPSView(View):
    def __init__(self, user):
        super().__init__(timeout=60)
        self.user = user
        self.choices = ["Rock", "Paper", "Scissors"]

    async def play_round(self, i: discord.Interaction, user_choice: str):
        if i.user != self.user:
            return await i.response.send_message("This is not your game!", ephemeral=True)
            
        bot_choice = random.choice(self.choices)
        result = ""
        gif_url = ""

        if user_choice == bot_choice:
            result = "It's a Tie!"
            gif_url = SYS_GIFS["rps_tie"]
        elif (user_choice == "Rock" and bot_choice == "Scissors") or \
             (user_choice == "Paper" and bot_choice == "Rock") or \
             (user_choice == "Scissors" and bot_choice == "Paper"):
            result = "You Win!"
            gif_url = SYS_GIFS["rps_win"]
        else:
            result = "I Win!"
            gif_url = SYS_GIFS["rps_lose"]

        embed = discord.Embed(title="Rock Paper Scissors", color=discord.Color.blurple())
        embed.add_field(name="You Chose", value=user_choice, inline=True)
        embed.add_field(name="FS Intelligence Chose", value=bot_choice, inline=True)
        embed.add_field(name="Result", value=f"**{result}**", inline=False)
        embed.set_image(url=gif_url)
        
        # Disable buttons after play
        for item in self.children:
            item.disabled = True
            
        await i.response.edit_message(embed=embed, view=self)

    @discord.ui.button(label="Rock", style=discord.ButtonStyle.primary)
    async def rock(self, i: discord.Interaction, button: Button):
        await self.play_round(i, "Rock")

    @discord.ui.button(label="Paper", style=discord.ButtonStyle.success)
    async def paper(self, i: discord.Interaction, button: Button):
        await self.play_round(i, "Paper")

    @discord.ui.button(label="Scissors", style=discord.ButtonStyle.danger)
    async def scissors(self, i: discord.Interaction, button: Button):
        await self.play_round(i, "Scissors")


class Fun(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # --- ACTION COMMANDS (ALL WITH GIFS) ---
    async def send_action_embed(self, i: discord.Interaction, action: str, member: discord.Member, text: str, color: discord.Color):
        if member == i.user and action not in ["cry", "dance", "blush"]:
            return await i.response.send_message(f"You can't {action} yourself, lonely soul!", ephemeral=True)
            
        description = f"**{i.user.display_name}** {text}" if action in ["cry", "dance", "blush"] else f"**{i.user.display_name}** {text} **{member.display_name}**!"
        embed = discord.Embed(description=description, color=color)
        embed.set_image(url=random.choice(ACTION_GIFS[action]))
        await i.response.send_message(embed=embed)

    @app_commands.command(name="kiss", description="Kiss someone!")
    async def kiss(self, i: discord.Interaction, member: discord.Member):
        await self.send_action_embed(i, "kiss", member, "kissed", discord.Color.pink())

    @app_commands.command(name="hug", description="Give someone a warm hug!")
    async def hug(self, i: discord.Interaction, member: discord.Member):
        await self.send_action_embed(i, "hug", member, "hugged", discord.Color.green())

    @app_commands.command(name="slap", description="Slap someone!")
    async def slap(self, i: discord.Interaction, member: discord.Member):
        await self.send_action_embed(i, "slap", member, "slapped", discord.Color.red())

    @app_commands.command(name="pat", description="Pat someone on the head!")
    async def pat(self, i: discord.Interaction, member: discord.Member):
        await self.send_action_embed(i, "pat", member, "patted", discord.Color.teal())

    @app_commands.command(name="kill", description="Eliminate a target!")
    async def kill(self, i: discord.Interaction, member: discord.Member):
        await self.send_action_embed(i, "kill", member, "just assassinated", discord.Color.dark_red())

    @app_commands.command(name="marry", description="Propose to someone!")
    async def marry(self, i: discord.Interaction, member: discord.Member):
        await self.send_action_embed(i, "marry", member, "proposed to", discord.Color.gold())
        
    @app_commands.command(name="bite", description="Bite someone!")
    async def bite(self, i: discord.Interaction, member: discord.Member):
        await self.send_action_embed(i, "bite", member, "bit", discord.Color.dark_orange())

    @app_commands.command(name="cry", description="Cry your heart out.")
    async def cry(self, i: discord.Interaction):
        await self.send_action_embed(i, "cry", i.user, "is crying...", discord.Color.blue())

    @app_commands.command(name="dance", description="Bust a move!")
    async def dance(self, i: discord.Interaction):
        await self.send_action_embed(i, "dance", i.user, "is dancing!", discord.Color.purple())

    @app_commands.command(name="blush", description="Awww, you're blushing!")
    async def blush(self, i: discord.Interaction):
        await self.send_action_embed(i, "blush", i.user, "is blushing...", discord.Color.magenta())

    # --- MINIGAMES & BOREDOM CURES (WITH GIFS) ---
    @app_commands.command(name="rps", description="Play Rock, Paper, Scissors with me!")
    async def rps(self, i: discord.Interaction):
        embed = discord.Embed(title="Rock Paper Scissors", description="Choose your weapon below!", color=discord.Color.blurple())
        await i.response.send_message(embed=embed, view=RPSView(i.user))

    @app_commands.command(name="hack", description="Fake hack a user for fun!")
    async def hack(self, i: discord.Interaction, member: discord.Member):
        await i.response.send_message(f"Initializing hack sequence on {member.mention}...")
        msg = await i.original_response()
        
        await asyncio.sleep(1.5)
        await msg.edit(content=f"Bypassing {member.display_name}'s firewall...")
        await asyncio.sleep(1.5)
        await msg.edit(content="Stealing Discord tokens and browser history...")
        await asyncio.sleep(2.0)
        await msg.edit(content="Selling data to the dark web...")
        await asyncio.sleep(1.5)
        
        embed = discord.Embed(title="Hack Complete!", description=f"{member.mention} is now officially broke.", color=discord.Color.green())
        embed.set_image(url=SYS_GIFS["hack"])
        await msg.edit(content=None, embed=embed)

    @app_commands.command(name="ship", description="Calculate love compatibility")
    async def ship(self, i: discord.Interaction, person1: discord.Member, person2: discord.Member):
        percent = random.randint(0, 100)
        bar = "█" * (percent // 10) + "░" * (10 - (percent // 10))
        
        embed = discord.Embed(title="Love Ship Calculator", color=discord.Color.pink())
        embed.add_field(name=f"{person1.display_name} + {person2.display_name}", value=f"**{percent}%**\n`{bar}`", inline=False)
        
        if percent > 50:
            embed.set_image(url=SYS_GIFS["ship_high"])
            embed.set_footer(text="A great match!")
        else:
            embed.set_image(url=SYS_GIFS["ship_low"])
            embed.set_footer(text="Yikes... maybe stay friends.")
            
        await i.response.send_message(embed=embed)

    # --- CLASSIC FUN COMMANDS (ALL GIF-POWERED) ---
    @app_commands.command(name="8ball", description="Ask the magic 8ball")
    async def eightball(self, i: discord.Interaction, question: str):
        responses = ["Yes, definitely.", "Without a doubt.", "Most likely.", "Ask again later.", "My reply is no.", "Very doubtful."]
        embed = discord.Embed(title="Magic 8-Ball", color=discord.Color.dark_theme())
        embed.add_field(name="Question", value=question, inline=False)
        embed.add_field(name="Answer", value=random.choice(responses), inline=False)
        embed.set_image(url=SYS_GIFS["8ball"])
        await i.response.send_message(embed=embed)

    @app_commands.command(name="roll", description="Roll a dice")
    async def roll(self, i: discord.Interaction):
        embed = discord.Embed(title="Dice Roll", description=f"You rolled a **{random.randint(1, 6)}**!", color=discord.Color.light_grey())
        embed.set_image(url=SYS_GIFS["roll"])
        await i.response.send_message(embed=embed)

    @app_commands.command(name="flip", description="Flip a coin")
    async def flip(self, i: discord.Interaction):
        embed = discord.Embed(title="Coin Flip", description=f"It's **{random.choice(['Heads', 'Tails'])}**!", color=discord.Color.gold())
        embed.set_image(url=SYS_GIFS["flip"])
        await i.response.send_message(embed=embed)

    # --- NEW RATING & ROAST COMMANDS ---
    @app_commands.command(name="howgay", description="Check someone's gay rate")
    async def howgay(self, i: discord.Interaction, member: discord.Member = None):
        member = member or i.user
        rate = random.randint(0, 100)
        embed = discord.Embed(title="Gay Rate Machine", description=f"{member.mention} is **{rate}%** gay 🌈", color=discord.Color.magenta())
        await i.response.send_message(embed=embed)

    @app_commands.command(name="simprate", description="Check someone's simp rate")
    async def simprate(self, i: discord.Interaction, member: discord.Member = None):
        member = member or i.user
        rate = random.randint(0, 100)
        embed = discord.Embed(title="Simp Rate Machine", description=f"{member.mention} is **{rate}%** simp 🥺", color=discord.Color.pink())
        await i.response.send_message(embed=embed)

    @app_commands.command(name="iq", description="Test your IQ")
    async def iq(self, i: discord.Interaction, member: discord.Member = None):
        member = member or i.user
        rate = random.randint(10, 200)
        embed = discord.Embed(title="IQ Test", description=f"{member.mention}'s IQ is **{rate}** 🧠", color=discord.Color.blue())
        await i.response.send_message(embed=embed)

    @app_commands.command(name="roast", description="Roast a user brutally")
    async def roast(self, i: discord.Interaction, member: discord.Member):
        roasts = [
            "You bring everyone so much joy... when you leave the room.",
            "I'd agree with you but then we'd both be wrong.",
            "You're like a cloud. When you disappear, it's a beautiful day.",
            "I have neither the time nor the crayons to explain this to you.",
            "You are the reason shampoo has instructions."
        ]
        embed = discord.Embed(title="Roasted!", description=f"{member.mention}, {random.choice(roasts)}", color=discord.Color.orange())
        embed.set_image(url=SYS_GIFS["roast"])
        await i.response.send_message(embed=embed)
        
    @app_commands.command(name="joke", description="Tells a random joke")
    async def joke(self, i: discord.Interaction):
        jokes = [
            "Why don't skeletons fight each other? They don't have the guts.",
            "What do you call fake spaghetti? An impasta!",
            "Why did the math book look sad? Because of all of its problems.",
            "What do you call a factory that makes okay products? A satisfactory."
        ]
        embed = discord.Embed(title="Here's a joke for you:", description=random.choice(jokes), color=discord.Color.teal())
        await i.response.send_message(embed=embed)

    @app_commands.command(name="avatar", description="Get a user's avatar")
    async def avatar(self, i: discord.Interaction, member: discord.Member = None):
        member = member or i.user
        embed = discord.Embed(title=f"{member.display_name}'s Avatar", color=member.color)
        embed.set_image(url=member.display_avatar.url)
        await i.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(Fun(bot))