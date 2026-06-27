import discord
import logging
import asyncio
from gtts import gTTS
from discord.ext import commands
from discord import app_commands
from huggingface_hub import InferenceClient

# Token
HF_TOKEN = "Your-Hf-Token-here"
ai_client = InferenceClient(provider="together", token=HF_TOKEN)

# Ghost's System Prompt
SYSTEM_PROMPT = """your-instruction-here"""

class ArtificialIntelligence(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.conversation_history = {}

    # ==========================================
    # 1. JARVIS STYLE VOICE ENGINE
    # ==========================================
    async def speak_as_fs(self, guild, text):
        try:
            vc = guild.voice_client
            if vc and vc.is_connected():
                tts = gTTS(text=text, lang='en', tld='co.uk') 
                tts.save("fs_voice.mp3")
                source = discord.FFmpegPCMAudio("fs_voice.mp3")
                
                while vc.is_playing():
                    await asyncio.sleep(1)
                
                vc.play(source)
        except Exception as e:
            logging.error(f"Voice Error: {e}")

    # ==========================================
    # 2. AUTO-REPLY TO MENTIONS
    # ==========================================
    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot: return

        if self.bot.user.mentioned_in(message) and message.author.id != self.bot.user.id:
            user_name = "Master Ghost" if message.author.id == 1485266122772316171 else message.author.display_name
            msg = f"FS Intelligence at your service, {user_name}. How may I assist you?"
            
            embed = discord.Embed(description=f"🌐 **{msg}**", color=discord.Color.teal())
            await message.channel.send(embed=embed)
            await self.speak_as_fs(message.guild, msg)

    # ==========================================
    # 3. ADVANCED AI COMMANDS
    # ==========================================
    @app_commands.command(name="ask", description="Ask FS Intelligence anything (Voice enabled) 🧠")
    async def ask(self, i: discord.Interaction, question: str):
        await i.response.defer(thinking=True)
        user_id = i.user.id
        
        if user_id not in self.conversation_history:
            self.conversation_history[user_id] = [{"role": "system", "content": SYSTEM_PROMPT}]
            
        self.conversation_history[user_id].append({"role": "user", "content": question})
        
        if len(self.conversation_history[user_id]) > 7:
            self.conversation_history[user_id] = [self.conversation_history[user_id][0]] + self.conversation_history[user_id][-6:]

        try:
            def fetch_ai():
                return ai_client.chat_completion(model="Qwen/Qwen2.5-7B-Instruct", messages=self.conversation_history[user_id])
            
            res = await asyncio.to_thread(fetch_ai)
            response = res.choices[0].message.content
            
            self.conversation_history[user_id].append({"role": "assistant", "content": response})

            embed = discord.Embed(title="FS Intelligence Core", description=response[:4000], color=discord.Color.blue())
            embed.set_footer(text=f"Query by {i.user.display_name}")
            
            await i.edit_original_response(embed=embed)
            
            clean_text_for_voice = response.replace("*", "").replace("`", "").replace("_", "")
            await self.speak_as_fs(i.guild, clean_text_for_voice[:200])
            
        except Exception as e:
            error_msg = str(e)[:200]
            print(f"[AI Ask Error] {error_msg}")
            try:
                await i.edit_original_response(content="❌ System Malfunction. (Possible Rate Limit by Host)")
            except:
                pass

    @app_commands.command(name="code", description="Generate or fix code using FS Intelligence 💻")
    async def code(self, i: discord.Interaction, language: str, prompt: str):
        await i.response.defer(thinking=True)
        
        sys_prompt = f"You are an expert {language} developer. Write the code efficiently. DO NOT write long explanations. Just provide the code and a 1 line summary."
        
        try:
            def fetch_code():
                return ai_client.chat_completion(
                    model="Qwen/Qwen2.5-7B-Instruct", 
                    messages=[
                        {"role": "system", "content": sys_prompt},
                        {"role": "user", "content": prompt}
                    ]
                )
            
            res = await asyncio.to_thread(fetch_code)
            response = res.choices[0].message.content
            
            await i.edit_original_response(content=f"**FS Intelligence Code Generator:**\n{response[:1900]}")
        except Exception as e:
            error_msg = str(e)[:200]
            print(f"[AI Code Error] {error_msg}")
            try:
                await i.edit_original_response(content="❌ Compilation Error. (Possible Rate Limit by Host)")
            except:
                pass

    @app_commands.command(name="translate", description="Translate text to English 🌍")
    async def translate(self, i: discord.Interaction, text: str):
        await i.response.defer(thinking=True)
        try:
            prompt = f"Translate the following text to Professional English. If it is already in English, correct its grammar. Text: '{text}'"
            
            def fetch_translate():
                return ai_client.chat_completion(model="Qwen/Qwen2.5-7B-Instruct", messages=[{"role": "user", "content": prompt}])
                
            res = await asyncio.to_thread(fetch_translate)
            
            embed = discord.Embed(title="Translation Engine", color=discord.Color.green())
            embed.add_field(name="Original", value=text, inline=False)
            embed.add_field(name="English", value=res.choices[0].message.content, inline=False)
            
            await i.edit_original_response(embed=embed)
        except Exception as e:
            error_msg = str(e)[:200]
            print(f"[AI Translate Error] {error_msg}")
            try:
                await i.edit_original_response(content="❌ Translation failed due to network limit.")
            except:
                pass

    # ==========================================
    # 4. AI MODERATION
    # ==========================================
    @app_commands.command(name="report", description="Report a message to FS Intelligence for analysis ⚖️")
    async def report(self, i: discord.Interaction, message_id: str):
        await i.response.defer(thinking=True, ephemeral=True)
        try:
            reported_msg = await i.channel.fetch_message(int(message_id))
            prompt = f"Analyze this reported message: '{reported_msg.content}'. Is it highly toxic, racist, or dangerous hate speech? Reply exactly with 'TOXIC' or 'CLEAN'. Then give a 1 sentence reason."
            
            def fetch_report():
                return ai_client.chat_completion(model="Qwen/Qwen2.5-7B-Instruct", messages=[{"role": "user", "content": prompt}])
                
            res = await asyncio.to_thread(fetch_report)
            analysis = res.choices[0].message.content.upper()
            
            if "TOXIC" in analysis:
                await reported_msg.delete()
                
                embed = discord.Embed(title="⚠️ Threat Eliminated", description=f"A message by **{reported_msg.author.name}** was removed.", color=discord.Color.red())
                embed.add_field(name="AI Analysis", value=res.choices[0].message.content.replace('TOXIC', '').strip())
                await i.channel.send(embed=embed)
                
                await i.edit_original_response(content="Threat neutralized.")
                await self.speak_as_fs(i.guild, "Hostile communication detected and eliminated.")
            else:
                await i.edit_original_response(content="✅ **Report Result:** FS Intelligence has deemed this message safe.")
        except discord.NotFound:
            await i.edit_original_response(content="❌ Error: Message ID not found in this channel.")
        except Exception as e:
            error_msg = str(e)[:200]
            print(f"[AI Report Error] {error_msg}")
            try:
                await i.edit_original_response(content="❌ Analysis Error. (Possible Rate Limit by Host)")
            except:
                pass

    @app_commands.command(name="clear_memory", description="Wipes your conversation history with FS Intelligence 🗑️")
    async def clear_memory(self, i: discord.Interaction):
        user_id = i.user.id
        if user_id in self.conversation_history:
            del self.conversation_history[user_id]
            await i.response.send_message("✅ Your conversation data has been wiped from my databanks.", ephemeral=True)
        else:
            await i.response.send_message("❌ No data found for your user ID.", ephemeral=True)

async def setup(bot):
    await bot.add_cog(ArtificialIntelligence(bot))