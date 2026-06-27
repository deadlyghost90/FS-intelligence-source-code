import discord
import yt_dlp
import asyncio
from discord.ext import commands
from discord import app_commands
from discord.ui import Button, View

# --- UI CONTROLS ---
class PlayerControls(View):
    def __init__(self):
        super().__init__(timeout=None)

    # Removed custom_ids so Discord handles the UUIDs automatically
    @discord.ui.button(label="⏯️ Play/Pause", style=discord.ButtonStyle.primary)
    async def toggle_play(self, i: discord.Interaction, b: Button):
        vc = i.guild.voice_client
        if not vc: return await i.response.send_message("❌ Not connected.", ephemeral=True)
        
        if vc.is_paused():
            vc.resume()
            await i.response.send_message("▶️ Resumed", ephemeral=True)
        elif vc.is_playing():
            vc.pause()
            await i.response.send_message("⏸️ Paused", ephemeral=True)

    @discord.ui.button(label="⏭️ Skip", style=discord.ButtonStyle.secondary)
    async def skip(self, i: discord.Interaction, b: Button):
        vc = i.guild.voice_client
        if vc and vc.is_playing():
            vc.stop() 
            await i.response.send_message("⏭️ Track Skipped!", ephemeral=False)
        else:
            await i.response.send_message("❌ Nothing to skip.", ephemeral=True)

    @discord.ui.button(label="⏹️ Stop", style=discord.ButtonStyle.danger)
    async def stop(self, i: discord.Interaction, b: Button):
        vc = i.guild.voice_client
        if vc: 
            await vc.disconnect()
        await i.response.send_message("⏹️ Music stopped and cleared.", ephemeral=False)

    @discord.ui.button(label="🔉 Vol -", style=discord.ButtonStyle.secondary, row=1)
    async def vol_down(self, i: discord.Interaction, b: Button):
        vc = i.guild.voice_client
        if vc and vc.source:
            vc.source.volume = max(0.0, vc.source.volume - 0.2)
            await i.response.send_message(f"🔉 Volume: {int(vc.source.volume * 100)}%", ephemeral=True)

    @discord.ui.button(label="🔊 Vol +", style=discord.ButtonStyle.secondary, row=1)
    async def vol_up(self, i: discord.Interaction, b: Button):
        vc = i.guild.voice_client
        if vc and vc.source:
            vc.source.volume = min(2.0, vc.source.volume + 0.2)
            await i.response.send_message(f"🔊 Volume: {int(vc.source.volume * 100)}%", ephemeral=True)


# --- MEDIA COG ---
class Media(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.music_queues = {} 

    @app_commands.command(name="play", description="Atom-style high quality music player 🎵")
    async def play(self, i: discord.Interaction, query: str):
        # 1. Start thinking state
        await i.response.defer(thinking=True)
        
        if not i.user.voice: 
            return await i.edit_original_response(content="❌ Join a Voice Channel first!")

        # 2. Non-Blocking AI Search
        ydl_opts = {'format': 'bestaudio/best', 'noplaylist': True, 'quiet': True, 'default_search': 'auto'}
        
        def search_song():
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                return ydl.extract_info(f"ytsearch:{query}", download=False)['entries'][0]

        try:
            info = await asyncio.to_thread(search_song)
            url = info['url']
            title = info.get('title', 'Unknown Title')
            thumbnail = info.get('thumbnail', 'https://i.imgur.com/8Q5qQ1s.png')
            
            # FIX: Safely handle None duration
            raw_duration = info.get('duration')
            duration = int(raw_duration) if raw_duration else 0
            
            uploader = info.get('uploader', 'Unknown Artist')
        except Exception as e:
            error_msg = str(e)[:200]
            return await i.edit_original_response(content=f"❌ Error finding track: {error_msg}...")

        # 3. Connect to VC
        channel = i.user.voice.channel
        vc = i.guild.voice_client
        if not vc:
            vc = await channel.connect()
        elif vc.channel != channel:
            await vc.move_to(channel)

        # 4. Stop current if playing
        if vc.is_playing() or vc.is_paused():
            vc.stop()

        # 5. Play Audio with Volume Control
        ffmpeg_options = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}
        original_source = discord.FFmpegPCMAudio(url, **ffmpeg_options)
        
        volume_source = discord.PCMVolumeTransformer(original_source, volume=1.0)
        vc.play(volume_source)

        # 6. Professional Atom-Style Embed
        mins, secs = divmod(duration, 60)
        duration_str = f"⏱️ {mins}:{secs:02d}" if duration > 0 else "⏱️ Live Stream"
        
        embed = discord.Embed(title="🎵 Now Playing", description=f"**{title}**", color=discord.Color.brand_red())
        embed.set_thumbnail(url=thumbnail)
        embed.add_field(name="Channel", value=f"🎤 {uploader}", inline=True)
        embed.add_field(name="Duration", value=duration_str, inline=True)
        embed.set_footer(text=f"Requested by {i.user.display_name}", icon_url=i.user.display_avatar.url)

        # 7. Send UI (WITH CRASH PROTECTION)
        try:
            await i.edit_original_response(content="🎶 **Track Loaded Successfully!**", embed=embed, view=PlayerControls())
        except Exception as e:
            # Sirf pehle 200 characters print karega taake bot block na ho
            error_msg = str(e)[:200]
            print(f"[Media UI Error] {error_msg}")
            try:
                await i.edit_original_response(content="⚠️ Track is playing, but UI failed to load due to a network limit.")
            except:
                pass

async def setup(bot):
    await bot.add_cog(Media(bot))