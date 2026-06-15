from discord.ext import commands
import discord
from datetime import datetime, timezone
import asyncio

TICKET_KATEGORI_ADI = "Ticketlar"
DESTEK_ROL_ADI = "Yetkili"
GIF_URL = "https://cdn.discordapp.com/attachments/1515043749061853277/1516160310589915156/ezgif-3b47b6b34f760692.gif"
PANEL_GIF_URL = "https://cdn.discordapp.com/attachments/1515043749061853277/1516160310589915156/ezgif-3b47b6b34f760692.gif"


async def kategori_bul_veya_olustur(guild: discord.Guild) -> discord.CategoryChannel:
    kategori = discord.utils.get(guild.categories, name=TICKET_KATEGORI_ADI)
    if not kategori:
        kategori = await guild.create_category(TICKET_KATEGORI_ADI)
    return kategori


async def ticket_olustur(guild: discord.Guild, uye: discord.Member) -> discord.TextChannel | None:
    kanal_adi = f"ticket-{uye.name.lower().replace(' ', '-')}"
    mevcut = discord.utils.get(guild.text_channels, name=kanal_adi)
    if mevcut:
        return None

    kategori = await kategori_bul_veya_olustur(guild)
    yetkililer = discord.utils.get(guild.roles, name=DESTEK_ROL_ADI)

    izinler = {
        guild.default_role: discord.PermissionOverwrite(read_messages=False),
        uye: discord.PermissionOverwrite(read_messages=True, send_messages=True),
        guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True),
    }
    if yetkililer:
        izinler[yetkililer] = discord.PermissionOverwrite(read_messages=True, send_messages=True)

    kanal = await guild.create_text_channel(
        name=kanal_adi,
        category=kategori,
        overwrites=izinler,
        topic=f"Ticket | {uye}",
    )

    embed = discord.Embed(
        title="🎫 Destek Talebi Oluşturuldu",
        description=(
            f"Merhaba {uye.mention}! Destek ekibimiz en kısa sürede sana yardımcı olacak.\n\n"
            "Lütfen sorununu veya talebini buraya yaz."
        ),
        color=0xFF8C00,
        timestamp=datetime.now(timezone.utc),
    )
    embed.set_image(url=GIF_URL)
    embed.set_footer(text="ARTAKS")
    await kanal.send(embed=embed, view=TicketCloseView())
    return kanal


class TicketCloseView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(
        label="Ticketi Kapat",
        style=discord.ButtonStyle.danger,
        emoji="🔒",
        custom_id="ticket:kapat",
    )
    async def kapat(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not interaction.channel.name.startswith("ticket-"):
            await interaction.response.send_message("❌ Bu bir ticket kanalı değil.", ephemeral=True)
            return
        embed = discord.Embed(description="🔒 Ticket 5 saniye içinde kapatılacak...", color=0xFF4444)
        await interaction.response.send_message(embed=embed)
        await asyncio.sleep(5)
        await interaction.channel.delete(reason=f"Ticket kapatıldı — {interaction.user}")


class TicketView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(
        label="Destek Talebi Oluştur",
        style=discord.ButtonStyle.primary,
        emoji="📋",
        custom_id="ticket:olustur",
    )
    async def olustur(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer(ephemeral=True)
        kanal = await ticket_olustur(interaction.guild, interaction.user)
        if kanal is None:
            kanal_adi = f"ticket-{interaction.user.name.lower().replace(' ', '-')}"
            mevcut = discord.utils.get(interaction.guild.text_channels, name=kanal_adi)
            await interaction.followup.send(
                f"❌ Zaten açık bir ticketin var: {mevcut.mention}", ephemeral=True
            )
        else:
            await interaction.followup.send(
                f"✅ Ticketin oluşturuldu: {kanal.mention}", ephemeral=True
            )

    @discord.ui.button(
        label="Nasıl oluşturabilirim?",
        style=discord.ButtonStyle.danger,
        emoji="❓",
        custom_id="ticket:nasil",
    )
    async def nasil(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed = discord.Embed(
            title="❓ Destek Talebi Nasıl Açılır?",
            description=(
                "**1.** 📋 **Destek Talebi Oluştur** butonuna bas.\n"
                "**2.** Sana özel bir kanal oluşturulacak.\n"
                "**3.** O kanalda sorununu veya talebini yaz.\n"
                "**4.** Yetkililer en kısa sürede sana yardımcı olacak.\n\n"
                "Ticketi kapatmak için `!ticketkapat` yazabilirsin."
            ),
            color=0x5865F2,
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)


class Tickets(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def cog_load(self):
        self.bot.add_view(TicketView())
        self.bot.add_view(TicketCloseView())

    # ── PANEL GÖNDER ──────────────────────────────────────────────────────────
    @commands.command(name="ticketpanel", aliases=["tpanel"])
    @commands.has_permissions(manage_channels=True)
    async def ticket_panel(self, ctx):
        await ctx.message.delete()
        embed = discord.Embed(
            title="❓ | Destek talebi nasıl açabilirim?",
            description=(
                "Aşağıdaki **Destek Talebi Oluştur** butonuna basarak destek talebi oluşturabilirsin!"
            ),
            color=0xFF8C00,
        )
        embed.set_image(url=PANEL_GIF_URL)
        embed.set_footer(text="ARTAKS")
        await ctx.send(embed=embed, view=TicketView())

    # ── KOMUT İLE TİCKET ──────────────────────────────────────────────────────
    @commands.command(name="ticket")
    async def ticket_ac(self, ctx):
        kanal = await ticket_olustur(ctx.guild, ctx.author)
        if kanal is None:
            kanal_adi = f"ticket-{ctx.author.name.lower().replace(' ', '-')}"
            mevcut = discord.utils.get(ctx.guild.text_channels, name=kanal_adi)
            await ctx.send(f"❌ Zaten açık bir ticketin var: {mevcut.mention}", delete_after=5)
        else:
            await ctx.send(f"✅ Ticketin açıldı: {kanal.mention}", delete_after=5)

    # ── TİCKET KAPAT ──────────────────────────────────────────────────────────
    @commands.command(name="ticketkapat", aliases=["tclose"])
    async def ticket_kapat(self, ctx):
        if not ctx.channel.name.startswith("ticket-"):
            await ctx.send("❌ Bu komut sadece ticket kanallarında kullanılabilir.", delete_after=5)
            return
        embed = discord.Embed(description="🔒 Ticket 5 saniye içinde kapatılacak...", color=0xFF4444)
        await ctx.send(embed=embed)
        await asyncio.sleep(5)
        await ctx.channel.delete(reason=f"Ticket kapatıldı — {ctx.author}")

    # ── TİCKETE KİŞİ EKLE ─────────────────────────────────────────────────────
    @commands.command(name="ticketekle", aliases=["tadd"])
    @commands.has_permissions(manage_channels=True)
    async def ticket_ekle(self, ctx, uye: discord.Member):
        if not ctx.channel.name.startswith("ticket-"):
            await ctx.send("❌ Bu komut sadece ticket kanallarında kullanılabilir.", delete_after=5)
            return
        await ctx.channel.set_permissions(uye, read_messages=True, send_messages=True)
        await ctx.send(f"✅ {uye.mention} tickete eklendi.")

    # ── TİCKETTEN KİŞİ ÇIKAR ─────────────────────────────────────────────────
    @commands.command(name="ticketcikar", aliases=["tremove"])
    @commands.has_permissions(manage_channels=True)
    async def ticket_cikar(self, ctx, uye: discord.Member):
        if not ctx.channel.name.startswith("ticket-"):
            await ctx.send("❌ Bu komut sadece ticket kanallarında kullanılabilir.", delete_after=5)
            return
        await ctx.channel.set_permissions(uye, read_messages=False, send_messages=False)
        await ctx.send(f"✅ {uye.mention} ticketten çıkarıldı.")

    # ── HATA ──────────────────────────────────────────────────────────────────
    @ticket_panel.error
    @ticket_ekle.error
    @ticket_cikar.error
    async def ticket_hata(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("❌ Bu komutu kullanmak için yetkin yok.", delete_after=5)
        elif isinstance(error, commands.MemberNotFound):
            await ctx.send("❌ Kullanıcı bulunamadı.", delete_after=5)


async def setup(bot):
    await bot.add_cog(Tickets(bot))
