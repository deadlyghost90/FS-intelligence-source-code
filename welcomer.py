import discord
from discord.ext import commands
from discord import app_commands
import random

class Welcomer(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # Temporary storage (In a real bot, use SQLite/JSON/MongoDB)
        self.configs = {} 
        
        # Professional Welcome Banners/GIFs (You can replace these URLs with your own LitchiMC banners)
        self.welcome_images = [
            "https://i.imgur.com/8Q5qQ1s.png", # Placeholder
            "https://media.giphy.com/media/l0MYC0LajbaPoEADu/giphy.gif" # Welcome GIF
        ]

    # --- HELPER FUNCTION ---
    def replace_variables(self, text: str, member: discord.Member):
        """Replaces variables like {user} with actual data"""
        return text.replace("{user}", member.mention) \
                   .replace("{user_name}", member.name) \
                   .replace("{server}", member.guild.name) \
                   .replace("{member_count}", str(member.guild.member_count))

    # ==========================================
    # 1. SETUP COMMANDS (ADMIN ONLY)
    # ==========================================
    @app_commands.command(name="set_welcome", description="Configure the welcome channel and message 📝")
    @app_commands.describe(
        channel="The channel where welcome messages will be sent",
        message="Use {user}, {user_name}, {server}, and {member_count} as variables"
    )
    async def set_welcome(self, i: discord.Interaction, channel: discord.TextChannel, message: str):
        if not i.user.guild_permissions.administrator: 
            return await i.response.send_message("❌ Access Denied: Administrator permissions required.", ephemeral=True)
        
        if i.guild.id not in self.configs:
            self.configs[i.guild.id] = {}
            
        self.configs[i.guild.id]["welcome_channel"] = channel.id
        self.configs[i.guild.id]["welcome_text"] = message
        
        display_msg = (message[:100] + '...') if len(message) > 100 else message
        
        embed = discord.Embed(title="✅ Welcome System Configured", color=discord.Color.green())
        embed.add_field(name="Channel", value=channel.mention, inline=False)
        embed.add_field(name="Message Preview", value=f"`{display_msg}`", inline=False)
        embed.set_footer(text="Tip: Use /test_welcome to see exactly how it looks!")
        
        await i.response.send_message(embed=embed)

    @app_commands.command(name="set_goodbye", description="Configure the goodbye/leave channel and message 👋")
    async def set_goodbye(self, i: discord.Interaction, channel: discord.TextChannel, message: str):
        if not i.user.guild_permissions.administrator: 
            return await i.response.send_message("❌ Access Denied: Administrator permissions required.", ephemeral=True)
        
        if i.guild.id not in self.configs:
            self.configs[i.guild.id] = {}
            
        self.configs[i.guild.id]["goodbye_channel"] = channel.id
        self.configs[i.guild.id]["goodbye_text"] = message
        
        await i.response.send_message(f"✅ **Goodbye System Set!**\nChannel: {channel.mention}\nText: `{message[:100]}`", ephemeral=True)

    @app_commands.command(name="set_autorole", description="Set a role to be given automatically when someone joins 🎭")
    async def set_autorole(self, i: discord.Interaction, role: discord.Role):
        if not i.user.guild_permissions.manage_roles: 
            return await i.response.send_message("❌ Access Denied: Manage Roles permission required.", ephemeral=True)
            
        # Security Check: Bot cannot give a role higher than its own
        if role >= i.guild.me.top_role:
            return await i.response.send_message("❌ I cannot assign this role because it is higher than or equal to my highest role.", ephemeral=True)

        if i.guild.id not in self.configs:
            self.configs[i.guild.id] = {}
            
        self.configs[i.guild.id]["autorole"] = role.id
        await i.response.send_message(f"✅ **Auto-Role Set!** New members will automatically receive {role.mention}.", ephemeral=True)

    # ==========================================
    # 2. TESTING TOOL
    # ==========================================
    @app_commands.command(name="test_welcome", description="Simulate a member joining to test your setup 🛠️")
    async def test_welcome(self, i: discord.Interaction):
        if not i.user.guild_permissions.administrator: 
            return await i.response.send_message("❌ Access Denied.", ephemeral=True)
            
        guild_id = i.guild.id
        if guild_id not in self.configs or "welcome_channel" not in self.configs[guild_id]:
            return await i.response.send_message("❌ Welcome system is not configured yet. Use `/set_welcome` first.", ephemeral=True)
            
        # Forcibly trigger the on_member_join event using the command caller
        await i.response.send_message("✅ Simulating welcome event...", ephemeral=True)
        self.bot.dispatch("member_join", i.user)

    # ==========================================
    # 3. EVENT LISTENERS
    # ==========================================
    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        guild_id = member.guild.id
        
        # Check if guild has configs
        if guild_id in self.configs:
            
            # --- Auto-Role Logic ---
            if "autorole" in self.configs[guild_id]:
                role_id = self.configs[guild_id]["autorole"]
                role = member.guild.get_role(role_id)
                if role:
                    try:
                        await member.add_roles(role, reason="Auto-Role on Join")
                    except discord.Forbidden:
                        pass # Ignore if bot lacks perms at execution time

            # --- Welcome Message Logic ---
            if "welcome_channel" in self.configs[guild_id]:
                channel_id = self.configs[guild_id]["welcome_channel"]
                channel = member.guild.get_channel(channel_id)
                
                if channel:
                    raw_text = self.configs[guild_id]["welcome_text"]
                    msg = self.replace_variables(raw_text, member)
                    
                    embed = discord.Embed(
                        title=f"Welcome to {member.guild.name}!", 
                        description=msg, 
                        color=discord.Color.gold()
                    )
                    
                    if member.avatar: 
                        embed.set_thumbnail(url=member.avatar.url)
                        
                    # Add a random banner from the list
                    embed.set_image(url=random.choice(self.welcome_images))
                    embed.set_footer(text=f"You are member #{member.guild.member_count}!")
                    
                    # Send message (Mentioning user outside embed ensures they get a ping notification)
                    await channel.send(content=member.mention, embed=embed)

    @commands.Cog.listener()
    async def on_member_remove(self, member: discord.Member):
        guild_id = member.guild.id
        
        if guild_id in self.configs and "goodbye_channel" in self.configs[guild_id]:
            channel_id = self.configs[guild_id]["goodbye_channel"]
            channel = member.guild.get_channel(channel_id)
            
            if channel:
                raw_text = self.configs[guild_id]["goodbye_text"]
                msg = self.replace_variables(raw_text, member)
                
                embed = discord.Embed(
                    title="Someone Left", 
                    description=msg, 
                    color=discord.Color.dark_gray()
                )
                if member.avatar: 
                    embed.set_thumbnail(url=member.avatar.url)
                    
                await channel.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Welcomer(bot))