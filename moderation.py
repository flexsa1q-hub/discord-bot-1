import discord
from discord.ext import commands
import datetime

class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def mod_embed(self, title, description, color):
        embed = discord.Embed(
            title=title,
            description=description,
            color=color,
            timestamp=datetime.datetime.utcnow()
        )
        return embed

    @commands.command(name="ban")
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, member: discord.Member, *, reason="Sebep belirtilmedi"):
        """Bir üyeyi sunucudan banlar."""
        await member.ban(reason=reason)
        embed = self.mod_embed(
            "🔨 Üye Banlandı",
            f"{member.mention} banlandı.",
            discord.Color.red()
        )
        embed.add_field(name="Sebep", value=reason, inline=False)
        embed.add_field(name="Yetkili", value=ctx.author.mention, inline=False)
        embed.set_thumbnail(url=member.display_avatar.url)
        await ctx.send(embed=embed)

    @commands.command(name="unban")
    @commands.has_permissions(ban_members=True)
    async def unban(self, ctx, *, user: str):
        """Banlı bir kullanıcının banını kaldırır."""
        banned_users = [entry async for entry in ctx.guild.bans()]
        name, discriminator = user.split("#") if "#" in user else (user, None)
        for ban_entry in banned_users:
            u = ban_entry.user
            if (discriminator and u.name == name and u.discriminator == discriminator) or \
               (not discriminator and u.name == name):
                await ctx.guild.unban(u)
                embed = self.mod_embed(
                    "✅ Ban Kaldırıldı",
                    f"`{u}` kullanıcısının banı kaldırıldı.",
                    discord.Color.green()
                )
                embed.add_field(name="Yetkili", value=ctx.author.mention)
                await ctx.send(embed=embed)
                return
        await ctx.send("❌ Bu kullanıcı ban listesinde bulunamadı.")

    @commands.command(name="kick")
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx, member: discord.Member, *, reason="Sebep belirtilmedi"):
        """Bir üyeyi sunucudan atar."""
        await member.kick(reason=reason)
        embed = self.mod_embed(
            "👢 Üye Atıldı",
            f"{member.mention} sunucudan atıldı.",
            discord.Color.orange()
        )
        embed.add_field(name="Sebep", value=reason, inline=False)
        embed.add_field(name="Yetkili", value=ctx.author.mention, inline=False)
        embed.set_thumbnail(url=member.display_avatar.url)
        await ctx.send(embed=embed)

    @commands.command(name="sil", aliases=["clear", "purge"])
    @commands.has_permissions(manage_messages=True)
    async def sil(self, ctx, miktar: int = 10):
        """Belirtilen sayıda mesajı siler (max 100)."""
        miktar = min(miktar, 100)
        deleted = await ctx.channel.purge(limit=miktar + 1)
        embed = self.mod_embed(
            "🗑️ Mesajlar Silindi",
            f"`{len(deleted) - 1}` mesaj silindi.",
            discord.Color.blurple()
        )
        embed.add_field(name="Yetkili", value=ctx.author.mention)
        msg = await ctx.send(embed=embed)
        await msg.delete(delay=4)

    @commands.command(name="mute", aliases=["timeout", "sus"])
    @commands.has_permissions(moderate_members=True)
    async def timeout(self, ctx, member: discord.Member, dakika: int = 5, *, reason="Sebep belirtilmedi"):
        """Bir üyeyi belirtilen dakika kadar susturur."""
        duration = datetime.timedelta(minutes=dakika)
        await member.timeout(duration, reason=reason)
        embed = self.mod_embed(
            "🔇 Üye Susturuldu",
            f"{member.mention} `{dakika}` dakika susturuldu.",
            discord.Color.yellow()
        )
        embed.add_field(name="Sebep", value=reason, inline=False)
        embed.add_field(name="Yetkili", value=ctx.author.mention, inline=False)
        embed.set_thumbnail(url=member.display_avatar.url)
        await ctx.send(embed=embed)

    @commands.command(name="unmute", aliases=["untimeout", "sussuz"])
    @commands.has_permissions(moderate_members=True)
    async def untimeout(self, ctx, member: discord.Member):
        """Bir üyenin susturmasını kaldırır."""
        await member.timeout(None)
        embed = self.mod_embed(
            "🔊 Susturma Kaldırıldı",
            f"{member.mention} artık konuşabilir.",
            discord.Color.green()
        )
        embed.add_field(name="Yetkili", value=ctx.author.mention)
        await ctx.send(embed=embed)

    @commands.command(name="uyar", aliases=["warn"])
    @commands.has_permissions(manage_messages=True)
    async def uyar(self, ctx, member: discord.Member, *, reason="Sebep belirtilmedi"):
        """Bir üyeye DM ile uyarı gönderir."""
        try:
            dm_embed = self.mod_embed(
                "⚠️ Uyarı Aldın",
                f"**{ctx.guild.name}** sunucusunda uyarıldın.",
                discord.Color.yellow()
            )
            dm_embed.add_field(name="Sebep", value=reason)
            await member.send(embed=dm_embed)
            dm_gitti = True
        except discord.Forbidden:
            dm_gitti = False

        embed = self.mod_embed(
            "⚠️ Üye Uyarıldı",
            f"{member.mention} uyarıldı." + (" (DM gönderilemedi)" if not dm_gitti else ""),
            discord.Color.yellow()
        )
        embed.add_field(name="Sebep", value=reason, inline=False)
        embed.add_field(name="Yetkili", value=ctx.author.mention, inline=False)
        await ctx.send(embed=embed)

    @commands.command(name="yavaşmod", aliases=["slowmode"])
    @commands.has_permissions(manage_channels=True)
    async def yavasmod(self, ctx, saniye: int = 0):
        """Kanalda yavaş mod ayarlar (0 = kapalı)."""
        await ctx.channel.edit(slowmode_delay=saniye)
        if saniye == 0:
            await ctx.send("✅ Yavaş mod kapatıldı.")
        else:
            await ctx.send(f"✅ Yavaş mod `{saniye}` saniye olarak ayarlandı.")

    @ban.error
    @kick.error
    @sil.error
    @timeout.error
    async def mod_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("❌ Bu komutu kullanmak için yetkin yok.")
        elif isinstance(error, commands.MemberNotFound):
            await ctx.send("❌ Kullanıcı bulunamadı.")
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(f"❌ Eksik argüman: `{error.param.name}`")

async def setup(bot):
    await bot.add_cog(Moderation(bot))
