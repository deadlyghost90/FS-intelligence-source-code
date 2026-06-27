import discord
from discord.ext import commands, tasks
from discord import app_commands
import firebase_admin
from firebase_admin import credentials, db

# ==========================================
# 1. FIREBASE INITIALIZATION
# ==========================================
if not firebase_admin._apps:
    cred = credentials.Certificate("firebase-adminsdk.json") 
    firebase_admin.initialize_app(cred, {
        'databaseURL': 'https://heroflix-d64ac-default-rtdb.firebaseio.com'
    })

# ==========================================
# CONFIGURATION
# ==========================================
CHANNEL_ID = 1513867464637939823  # Notification Channel
ADMIN_LINK = "https://litchimcweb.vercel.app/litchi4321234.html"

# ==========================================
# 2. INTERACTIVE ORDER BUTTONS (DISCORD TO FIREBASE)
# ==========================================
class OrderControls(discord.ui.View):
    def __init__(self, order_id: str):
        super().__init__(timeout=None) # Timeout None taake buttons hamesha kaam karein
        self.order_id = order_id

    # Check Permissions (Only Admins can click)
    async def interaction_check(self, i: discord.Interaction) -> bool:
        if not i.user.guild_permissions.administrator:
            await i.response.send_message("❌ Security Alert: Only Administrators can manage orders.", ephemeral=True)
            return False
        return True

    @discord.ui.button(label="Mark Completed", style=discord.ButtonStyle.success, emoji="✅")
    async def complete_order(self, i: discord.Interaction, button: discord.ui.Button):
        try:
            # Update Database
            db.reference(f'orders/{self.order_id}').update({'status': 'Completed'})
            
            # Disable buttons & Edit Message
            for child in self.children:
                child.disabled = True
            
            embed = i.message.embeds[0]
            embed.color = discord.Color.green()
            embed.set_footer(text=f"Order Completed by {i.user.name}", icon_url=i.user.display_avatar.url)
            
            await i.response.edit_message(embed=embed, view=self)
            await i.followup.send(f"✅ Order `{self.order_id}` successfully marked as completed!", ephemeral=True)
        except Exception as e:
            await i.response.send_message(f"❌ Database Error: {e}", ephemeral=True)

    @discord.ui.button(label="Delete Order", style=discord.ButtonStyle.danger, emoji="🗑️")
    async def delete_order(self, i: discord.Interaction, button: discord.ui.Button):
        try:
            # Delete from Database
            db.reference(f'orders/{self.order_id}').delete()
            
            # Disable buttons & Edit Message
            for child in self.children:
                child.disabled = True
                
            embed = i.message.embeds[0]
            embed.color = discord.Color.dark_grey()
            embed.title = "🗑️ ORDER DELETED"
            embed.set_footer(text=f"Order Deleted by {i.user.name}", icon_url=i.user.display_avatar.url)
            
            await i.response.edit_message(embed=embed, view=self)
            await i.followup.send(f"🗑️ Order `{self.order_id}` has been erased from the database.", ephemeral=True)
        except Exception as e:
            await i.response.send_message(f"❌ Database Error: {e}", ephemeral=True)


# ==========================================
# 3. MAIN LIVE ORDERS COG
# ==========================================
class LiveOrders(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.seen_orders = set()
        self.first_run = True
        self.check_orders.start()

    def cog_unload(self):
        self.check_orders.cancel()

    # --- THE LIVE SCANNER ---
    @tasks.loop(seconds=10) 
    async def check_orders(self):
        await self.bot.wait_until_ready()
        channel = self.bot.get_channel(CHANNEL_ID)
        if not channel: return

        try:
            ref = db.reference('orders')
            orders = ref.get()

            if orders:
                for order_id, data in orders.items():
                    if order_id not in self.seen_orders:
                        # Pehli baar run hone par purane orders ko skip karega
                        if self.first_run:
                            self.seen_orders.add(order_id)
                        else:
                            self.seen_orders.add(order_id)
                            
                            # Naya Pending Order aane par action
                            if data.get('status') == "Pending":
                                await self.send_order_embed(channel, order_id, data)
                
                if self.first_run:
                    print("[LitchiMC System] Live Order Scanner Initialized.")
                self.first_run = False
                
        except Exception as e:
            print(f"⚠️ Firebase Connection Error: {e}")

    # --- EMBED GENERATOR ---
    async def send_order_embed(self, channel, order_id, data):
        # Masking the Card Details for Security
        raw_card = data.get('cardNumber', 'N/A')
        masked_card = f"**** **** **** {raw_card[-4:]}" if len(raw_card) >= 4 else raw_card

        embed = discord.Embed(
            title="🚨 NEW PREMIUM ORDER 🚨",
            description=f"A new purchase request has been submitted to LitchiMC.\n\n🔗 **[Open Web Terminal]({ADMIN_LINK})**",
            color=discord.Color.red()
        )
        
        embed.add_field(name="🎮 Player Identity", value=f"`{data.get('mc_username', 'Unknown')}`", inline=True)
        embed.add_field(name="📦 Item Requested", value=f"**{data.get('item', 'Unknown')}**", inline=True)
        embed.add_field(name="💰 Amount", value=f"**{data.get('price', 'Unknown')}**", inline=True)
        
        embed.add_field(name="📧 Contact Email", value=f"{data.get('email', 'Guest')}", inline=False)
        
        # Payment Info Box
        payment_info = f"**Method:** Stripe / Card\n**Card Number:** `{masked_card}`\n**Transaction ID:** `{order_id[-8:]}`"
        embed.add_field(name="💳 Payment Details (Masked)", value=payment_info, inline=False)
        
        embed.set_footer(text="LitchiMC Auto-Checkout System", icon_url=self.bot.user.display_avatar.url)
        
        # Send Message with Interactive Buttons
        await channel.send(embed=embed, view=OrderControls(order_id))

    # ==========================================
    # 4. MANUAL ADMIN COMMANDS
    # ==========================================
    @app_commands.command(name="pending_orders", description="[ADMIN] Check all unfulfilled orders in database")
    async def pending_orders(self, i: discord.Interaction):
        if not i.user.guild_permissions.administrator:
            return await i.response.send_message("❌ Access Denied.", ephemeral=True)

        await i.response.defer(ephemeral=True)
        
        try:
            orders = db.reference('orders').get()
            pending_list = []
            
            if orders:
                for order_id, data in orders.items():
                    if data.get('status') == "Pending":
                        pending_list.append(f"• **{data.get('mc_username')}** requested **{data.get('item')}** (`{order_id[-6:]}`)")
            
            if not pending_list:
                return await i.followup.send("✅ No pending orders. The queue is completely clear!")

            embed = discord.Embed(title="🛒 Pending Orders Queue", description="\n".join(pending_list), color=discord.Color.orange())
            await i.followup.send(embed=embed)
            
        except Exception as e:
            await i.followup.send(f"❌ Database Read Error: {e}")

async def setup(bot):
    await bot.add_cog(LiveOrders(bot))