import discord
from discord.ext import commands

class NasilAcilir(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(
        label="Destek Talebi Oluştur",
        style=discord.ButtonStyle.primary,
        custom_id="ticket_ac",
        emoji="📋"
    )
    async def ticket_ac(self, interaction: discord.Interaction, button: discord.ui.Button):
        guild = interaction.guild
        user = interaction.user

        mevcut = discord.utils.get(guild.text_channels, name=f"ticket-{user.name.lower()}")
        if mevcut:
            await interaction.response.send_message(
                f"❌ Zaten açık bir ticketin var! {mevcut.mention}",
                ephemeral=True
            )
            return

        kategori = discord.utils.get(guild.categories, name="🎫 Ticketlar")
        if not kategori:
            kategori = await guild.create_category("🎫 Ticketlar")

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            user: discord.PermissionOverwrite(
                read_messages=True,
                send_messages=True,
                attach_files=True,
                embed_links=True
            ),
            guild.me: discord.PermissionOverwrite(
                read_messages=True,
                send_messages=True,
                manage_channels=True
            )
        }

        for rol in guild.roles:
            if rol.permissions.manage_messages and rol != guild.default_role:
                overwrites[rol] = discord.PermissionOverwrite(
                    read_messages=True,
                    send_messages=True
                )

        kanal = await guild.create_text_channel(
            name=f"ticket-{user.name.lower()}",
            category=kategori,
            overwrites=overwrites,
            topic=str(user.id),
            reason=f"Ticket: {user}"
        )

        embed = discord.Embed(
            title="🎫 Destek Talebi Açıldı",
            description=(
                f"Merhaba {user.mention}! Destek talebin oluşturuldu.\n\n"
                f"Yetkililer en kısa sürede sana yardımcı olacak.\n"
                f"Ticketi kapatmak için aşağıdaki butona bas."
            ),
            color=0xFFB6C1
        )
        embed.set_thumbnail(url=user.display_avatar.url)
        embed.set_footer(text="A R T A K S • Destek Sistemi")

        await kanal.send(
            content=f"{user.mention}",
            embed=embed,
            view=KapatButon()
        )

        await interaction.response.send_message(
            f"✅ Ticketin açıldı! → {kanal.mention}",
            ephemeral=True
        )

    @discord.ui.button(
        label="Nasıl oluşturabilirim?",
        style=discord.ButtonStyle.secondary,
        custom_id="ticket_nasil",
        emoji="❓"
    )
    async def nasil(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message(
            "📋 **Destek talebi açmak için:**\n"
            "Yukarıdaki mavi **Destek Talebi Oluştur** butonuna bas!\n"
            "Sana özel bir kanal açılacak ve yetkililer yardımcı olacak.",
            ephemeral=True
        )


class KapatButon(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(
        label="Ticketi Kapat",
        style=discord.ButtonStyle.red,
        custom_id="ticket_kapat",
        emoji="🔒"
    )
    async def kapat(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not interaction.user.guild_permissions.manage_channels and \
           interaction.user.id != int(interaction.channel.topic or 0):
            await interaction.response.send_message(
                "❌ Bu ticketi kapatma yetkin yok!",
                ephemeral=True
            )
            return

        embed = discord.Embed(
            title="🔒 Ticket Kapatılıyor...",
            description=f"{interaction.user.mention} tarafından kapatıldı.",
            color=discord.Color.red()
        )
        await interaction.response.send_message(embed=embed)
        await interaction.channel.delete(reason=f"Ticket kapatıldı: {interaction.user}")


class Ticket(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        bot.add_view(NasilAcilir())
        bot.add_view(KapatButon())

    @commands.command(name="ticketpanel")
    @commands.has_permissions(manage_channels=True)
    async def ticketpanel(self, ctx):
        embed = discord.Embed(
            title="❓ | Destek talebi nasıl açabilirim?",
            description=(
                "Aşağıdaki **Destek Talebi Oluştur** "
                "butonuna basarak destek talebi oluşturabilirsin!"
            ),
            color=0x5865F2
        )
        embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/1515043749061853277/1515382445380206734/ezgif-3b47b6b34f760692.gif")
        embed.set_footer(text="A R T A K S")

        await ctx.send(embed=embed, view=NasilAcilir())
        await ctx.message.delete()

    @commands.command(name="ticketkapat")
    @commands.has_permissions(manage_channels=True)
    async def ticketkapat(self, ctx):
        if not ctx.channel.name.startswith("ticket-"):
            await ctx.send("❌ Bu bir ticket kanalı değil!", delete_after=3)
            return
        embed = discord.Embed(
            title="🔒 Ticket Kapatıldı",
            description=f"{ctx.author.mention} tarafından kapatıldı.",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)
        await ctx.channel.delete(reason=f"Ticket kapatıldı: {ctx.author}")

    @commands.command(name="ticketekle")
    @commands.has_permissions(manage_channels=True)
    async def ticketekle(self, ctx, uye: discord.Member):
        if not ctx.channel.name.startswith("ticket-"):
            await ctx.send("❌ Bu bir ticket kanalı değil!", delete_after=3)
            return
        await ctx.channel.set_permissions(uye, read_messages=True, send_messages=True)
        await ctx.send(f"✅ {uye.mention} tickete eklendi.")

    @commands.command(name="ticketcikar")
    @commands.has_permissions(manage_channels=True)
    async def ticketcikar(self, ctx, uye: discord.Member):
        if not ctx.channel.name.startswith("ticket-"):
            await ctx.send("❌ Bu bir ticket kanalı değil!", delete_after=3)
            return
        await ctx.channel.set_permissions(uye, overwrite=None)
        await ctx.send(f"✅ {uye.mention} ticketten çıkarıldı.")


async def setup(bot):
    await bot.add_cog(Ticket(bot))
