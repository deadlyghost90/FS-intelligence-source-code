import discord
from discord.ext import commands
from discord import app_commands
import platform
import time
import asyncio

# Bot ka uptime track karne ke liye
start_time = time.time()

class Utility(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # 1. ADVANCED PING
    @app_commands.command(name="ping", description="Check FS Intelligence latency")
    async def ping(self, i: discord.Interaction):
        latency = round(self.bot.latency * 1000)
        
        # Color dynamically change hoga latency ke hisaab se
        color = discord.Color.brand_green() if latency < 100 else discord.Color.orange()
        if latency > 250: color = discord.Color.red()

        embed = discord.Embed(title="🏓 Pong!", description=f"Connection Latency: **{latency}ms**", color=color)
        await i.response.send_message(embed=embed)

    # 2. ADVANCED USER INFO
    @app_commands.command(name="userinfo", description="Get advanced details about a member")
    async def userinfo(self, i: discord.Interaction, member: discord.Member = None):
        member = member or i.user
        
        # Format roles nicely, ignoring @everyone
        roles = [role.mention for role in member.roles if role.name != "@everyone"]
        roles_str = " ".join(roles) if roles else "No special roles"
        
        embed = discord.Embed(title=f"User Intelligence: {member.name}", color=member.color or discord.Color.blue())
        embed.set_thumbnail(url=member.display_avatar.url)
        embed.add_field(name="Identity (ID)", value=member.id, inline=True)
        embed.add_field(name="Server Nickname", value=member.display_name, inline=True)
        embed.add_field(name="Account Created", value=discord.utils.format_dt(member.created_at, "R"), inline=False)
        embed.add_field(name="Joined Server", value=discord.utils.format_dt(member.joined_at, "R"), inline=False)
        embed.add_field(name=f"Assigned Roles [{len(roles)}]", value=roles_str, inline=False)
        embed.set_footer(text=f"Requested by {i.user.name}", icon_url=i.user.display_avatar.url)
        
        await i.response.send_message(embed=embed)

    # 3. SERVER INFO (NEW)
    @app_commands.command(name="serverinfo", description="Get detailed information about this server")
    async def serverinfo(self, i: discord.Interaction):
        guild = i.guild
        embed = discord.Embed(title=f"Server Info - {guild.name}", color=discord.Color.gold())
        if guild.icon:
            embed.set_thumbnail(url=guild.icon.url)
        
        embed.add_field(name="Owner", value=guild.owner.mention, inline=True)
        embed.add_field(name="Server ID", value=guild.id, inline=True)
        embed.add_field(name="Created On", value=discord.utils.format_dt(guild.created_at, "D"), inline=False)
        embed.add_field(name="Members", value=f"👥 {guild.member_count}", inline=True)
        embed.add_field(name="Channels", value=f"💬 {len(guild.text_channels)} Text | 🔊 {len(guild.voice_channels)} Voice", inline=True)
        embed.add_field(name="Roles", value=str(len(guild.roles)), inline=True)
        
        await i.response.send_message(embed=embed)

    # 4. BOT STATS (NEW - Paradox Studio Branding)
    @app_commands.command(name="botinfo", description="View FS Intelligence system statistics")
    async def botinfo(self, i: discord.Interaction):
        uptime_seconds = int(time.time() - start_time)
        mins, secs = divmod(uptime_seconds, 60)
        hours, mins = divmod(mins, 60)
        uptime_str = f"{hours}h {mins}m {secs}s"

        embed = discord.Embed(title="🤖 FS Intelligence Systems", color=discord.Color.brand_red())
        embed.set_thumbnail(url=self.bot.user.display_avatar.url)
        embed.add_field(name="Lead Developer", value="**Ghost** (Paradox Studio)", inline=False)
        embed.add_field(name="Core Language", value=f"Python {platform.python_version()}", inline=True)
        embed.add_field(name="Library", value=f"discord.py v{discord.__version__}", inline=True)
        embed.add_field(name="System Uptime", value=f"⏱️ {uptime_str}", inline=False)
        embed.add_field(name="Network", value=f"Monitoring {len(self.bot.guilds)} server(s)", inline=True)
        
        await i.response.send_message(embed=embed)

    # 5. UPGRADED POLL
    @app_commands.command(name="poll", description="Create a clean Yes/No public poll")
    async def poll(self, i: discord.Interaction, question: str):
        embed = discord.Embed(title="📊 Community Poll", description=f"**{question}**", color=discord.Color.blurple())
        embed.set_footer(text=f"Poll created by {i.user.display_name}")
        
        # Ephemeral confirmation taake command type karne wala message chup jaye
        await i.response.send_message("✅ Poll created successfully!", ephemeral=True)
        
        msg = await i.channel.send(embed=embed)
        await msg.add_reaction("✅")
        await msg.add_reaction("❌")

    # 6. ANNOUNCE (NEW - Admin utility)
    @app_commands.command(name="announce", description="Send an official server announcement embed")
    @app_commands.describe(title="Title of announcement", message="Main announcement content")
    async def announce(self, i: discord.Interaction, title: str, message: str):
        if not i.user.guild_permissions.manage_messages:
            return await i.response.send_message("❌ You don't have permission to make announcements.", ephemeral=True)
            
        embed = discord.Embed(title=f"📢 {title}", description=message, color=discord.Color.red())
        embed.set_footer(text="Official Announcement")
        
        await i.response.send_message("✅ Announcement posted!", ephemeral=True)
        await i.channel.send(embed=embed)

    # 7. REMIND ME (NEW - Asynchronous Utility)
    @app_commands.command(name="remindme", description="Set a quick reminder (in minutes)")
    async def remindme(self, i: discord.Interaction, minutes: int, reminder: str):
        if minutes <= 0 or minutes > 1440:
            return await i.response.send_message("❌ Please set a time between 1 and 1440 minutes (24 hours).", ephemeral=True)
            
        await i.response.send_message(f"✅ Noted! I will remind you about **'{reminder}'** in {minutes} minute(s).", ephemeral=True)
        
        # Bot background mein wait karega (server block nahi hoga)
        await asyncio.sleep(minutes * 60)
        
        try:
            embed = discord.Embed(title="⏰ Reminder Alert!", description=f"You asked me to remind you:\n\n**{reminder}**", color=discord.Color.gold())
            await i.user.send(embed=embed)
        except discord.Forbidden:
            # Agar DMs band hain toh usi channel mein tag karega
            await i.channel.send(f"{i.user.mention} ⏰ Reminder: **{reminder}**")

    # 8. MEMBER COUNT (NEW)
    @app_commands.command(name="membercount", description="Show detailed member statistics")
    async def membercount(self, i: discord.Interaction):
        guild = i.guild
        bots = sum(1 for member in guild.members if member.bot)
        humans = guild.member_count - bots
        
        embed = discord.Embed(title=f"📈 Population: {guild.name}", color=discord.Color.teal())
        embed.add_field(name="Total Population", value=str(guild.member_count), inline=False)
        embed.add_field(name="Humans 🧑", value=str(humans), inline=True)
        embed.add_field(name="Bots 🤖", value=str(bots), inline=True)
        
        await i.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(Utility(bot))