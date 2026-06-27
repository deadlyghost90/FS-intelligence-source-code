import discord
from discord.ext import commands
from discord import app_commands
from datetime import timedelta

# Tumhari Discord ID (The Ghost Override)
OWNER_ID = 1485266122772316171

class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # --- HELPER FUNCTION ---
    async def no_perms(self, i: discord.Interaction):
        embed = discord.Embed(title="Access Denied", description="You lack the required administrator permissions to execute this action.", color=discord.Color.red())
        await i.response.send_message(embed=embed, ephemeral=True)

    # --- CORE MODERATION ---
    @app_commands.command(name="ban", description="Permanently ban a member from the server")
    async def ban(self, i: discord.Interaction, member: discord.Member, reason: str = "No reason provided"):
        # Ghost Override: Agar User Owner ID nahi hai aur Perms bhi nahi hain, tab block karo
        if not i.user.guild_permissions.ban_members and i.user.id != OWNER_ID: 
            return await self.no_perms(i)
        
        # Ghost Override: Ghost kisi ko bhi ban kar sakta hai, chahe uski rank kitni bhi badi ho
        if member.top_role >= i.user.top_role and i.user.id != OWNER_ID and i.user != i.guild.owner:
            return await i.response.send_message("You cannot ban someone with a higher or equal role!", ephemeral=True)
        
        await member.ban(reason=reason)
        embed = discord.Embed(title="Member Banned", description=f"**{member.name}** has been permanently removed.", color=discord.Color.dark_red())
        embed.add_field(name="Reason", value=reason)
        embed.set_footer(text=f"Action by: {i.user.display_name}")
        await i.response.send_message(embed=embed)

    @app_commands.command(name="kick", description="Kick a member from the server")
    async def kick(self, i: discord.Interaction, member: discord.Member, reason: str = "No reason provided"):
        if not i.user.guild_permissions.kick_members and i.user.id != OWNER_ID: 
            return await self.no_perms(i)
            
        if member.top_role >= i.user.top_role and i.user.id != OWNER_ID and i.user != i.guild.owner:
            return await i.response.send_message("You cannot kick someone with a higher or equal role!", ephemeral=True)

        await member.kick(reason=reason)
        embed = discord.Embed(title="Member Kicked", description=f"**{member.name}** has been kicked from the server.", color=discord.Color.orange())
        embed.add_field(name="Reason", value=reason)
        await i.response.send_message(embed=embed)

    @app_commands.command(name="warn", description="Issue a formal warning to a member")
    async def warn(self, i: discord.Interaction, member: discord.Member, reason: str):
        if not i.user.guild_permissions.manage_messages and i.user.id != OWNER_ID: 
            return await self.no_perms(i)
        
        # Try to DM the user
        try:
            dm_embed = discord.Embed(title=f"Warning from {i.guild.name}", description=f"You have been warned for: **{reason}**", color=discord.Color.gold())
            await member.send(embed=dm_embed)
        except:
            pass # Ignore if DMs are closed

        embed = discord.Embed(title="Member Warned", description=f"**{member.mention}** has received a warning.", color=discord.Color.gold())
        embed.add_field(name="Reason", value=reason)
        await i.response.send_message(embed=embed)

    # --- TIMEOUT SYSTEM ---
    @app_commands.command(name="timeout", description="Mute/Timeout a member for a specific duration")
    async def timeout(self, i: discord.Interaction, member: discord.Member, minutes: int, reason: str = "Rule violation"):
        if not i.user.guild_permissions.moderate_members and i.user.id != OWNER_ID: 
            return await self.no_perms(i)
            
        if member.top_role >= i.user.top_role and i.user.id != OWNER_ID and i.user != i.guild.owner:
            return await i.response.send_message("You cannot timeout this user!", ephemeral=True)

        duration = timedelta(minutes=minutes)
        await member.timeout(duration, reason=reason)
        
        embed = discord.Embed(title="Member Timeout", description=f"**{member.name}** has been muted for {minutes} minutes.", color=discord.Color.dark_theme())
        embed.add_field(name="Reason", value=reason)
        await i.response.send_message(embed=embed)

    @app_commands.command(name="untimeout", description="Remove a timeout from a member")
    async def untimeout(self, i: discord.Interaction, member: discord.Member):
        if not i.user.guild_permissions.moderate_members and i.user.id != OWNER_ID: 
            return await self.no_perms(i)
        
        await member.timeout(None, reason="Manual Untimeout")
        embed = discord.Embed(title="Timeout Removed", description=f"**{member.name}** can now speak again.", color=discord.Color.green())
        await i.response.send_message(embed=embed)

    # --- CHANNEL MANAGEMENT ---
    @app_commands.command(name="clear", description="Bulk delete messages in the channel")
    async def clear(self, i: discord.Interaction, amount: int):
        if not i.user.guild_permissions.manage_messages and i.user.id != OWNER_ID: 
            return await self.no_perms(i)
        
        await i.response.defer(ephemeral=True) # Prevent interaction failure for large purges
        deleted = await i.channel.purge(limit=amount)
        
        embed = discord.Embed(title="Channel Purged", description=f"Successfully swept **{len(deleted)}** messages.", color=discord.Color.teal())
        await i.followup.send(embed=embed, ephemeral=True)

    @app_commands.command(name="lock", description="Lock the current channel")
    async def lock(self, i: discord.Interaction):
        if not i.user.guild_permissions.manage_channels and i.user.id != OWNER_ID: 
            return await self.no_perms(i)
        
        await i.channel.set_permissions(i.guild.default_role, send_messages=False)
        embed = discord.Embed(title="Channel Locked", description="This channel has been locked by an administrator.", color=discord.Color.red())
        await i.response.send_message(embed=embed)

    @app_commands.command(name="unlock", description="Unlock the current channel")
    async def unlock(self, i: discord.Interaction):
        if not i.user.guild_permissions.manage_channels and i.user.id != OWNER_ID: 
            return await self.no_perms(i)
        
        await i.channel.set_permissions(i.guild.default_role, send_messages=True)
        embed = discord.Embed(title="Channel Unlocked", description="This channel is now open for chatting.", color=discord.Color.green())
        await i.response.send_message(embed=embed)

    @app_commands.command(name="slowmode", description="Set a slowmode delay for the channel")
    async def slowmode(self, i: discord.Interaction, seconds: int):
        if not i.user.guild_permissions.manage_channels and i.user.id != OWNER_ID: 
            return await self.no_perms(i)
        
        await i.channel.edit(slowmode_delay=seconds)
        embed = discord.Embed(title="Slowmode Updated", description=f"Slowmode is now set to **{seconds} seconds**.", color=discord.Color.blue())
        await i.response.send_message(embed=embed)

   
    # --- ROLE MANAGEMENT ---
    @app_commands.command(name="addrole", description="Assign a role to a member")
    async def addrole(self, i: discord.Interaction, member: discord.Member, role: discord.Role):
        if not i.user.guild_permissions.manage_roles and i.user.id != OWNER_ID: 
            return await self.no_perms(i)
            
        if role >= i.user.top_role and i.user.id != OWNER_ID and i.user != i.guild.owner:
            return await i.response.send_message("You cannot give a role higher than your own!", ephemeral=True)

        await member.add_roles(role)
        embed = discord.Embed(title="Role Added", description=f"**{member.name}** was given the {role.mention} role.", color=discord.Color.green())
        await i.response.send_message(embed=embed)

    @app_commands.command(name="removerole", description="Remove a role from a member")
    async def removerole(self, i: discord.Interaction, member: discord.Member, role: discord.Role):
        if not i.user.guild_permissions.manage_roles and i.user.id != OWNER_ID: 
            return await self.no_perms(i)
            
        if role >= i.user.top_role and i.user.id != OWNER_ID and i.user != i.guild.owner:
            return await i.response.send_message("You cannot remove a role higher than your own!", ephemeral=True)

        await member.remove_roles(role)
        embed = discord.Embed(title="Role Removed", description=f"**{member.name}** no longer has the {role.mention} role.", color=discord.Color.orange())
        await i.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(Moderation(bot))