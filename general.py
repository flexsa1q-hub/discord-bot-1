import discord
from discord.ext import commands
from discord import app_commands
import datetime
import random
import aiohttp

class General(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="ping")
    async def ping(self, ctx):
        """Check the bot's latency."""
        latency = round(self.bot.latency * 1000)
        await ctx.send(f"Pong! `{latency}ms`")

    @commands.command(name="info")
    async def info(self, ctx):
        """Display information about the server."""
        guild = ctx.guild
        embed = discord.Embed(
            title=f"{guild.name} Info",
            color=discord.Color.blurple(),
            timestamp=datetime.datetime.utcnow()
        )
        embed.set_thumbnail(url=guild.icon.url if guild.icon else None)
        embed.add_field(name="Owner", value=guild.owner.mention, inline=True)
        embed.add_field(name="Members", value=guild.member_count, inline=True)
        embed.add_field(name="Channels", value=len(guild.channels), inline=True)
        embed.add_field(name="Roles", value=len(guild.roles), inline=True)
        embed.add_field(name="Created", value=guild.created_at.strftime("%b %d, %Y"), inline=True)
        embed.set_footer(text=f"ID: {guild.id}")
        await ctx.send(embed=embed)

    @commands.command(name="avatar")
    async def avatar(self, ctx, member: discord.Member = None):
        """Display a user's avatar."""
        member = member or ctx.author
        embed = discord.Embed(
            title=f"{member.display_name}'s Avatar",
            color=discord.Color.blurple()
        )
        embed.set_image(url=member.display_avatar.url)
        await ctx.send(embed=embed)

    @commands.command(name="userinfo")
    async def userinfo(self, ctx, member: discord.Member = None):
        """Display information about a user."""
        member = member or ctx.author
        embed = discord.Embed(
            title=f"{member} Info",
            color=member.color,
            timestamp=datetime.datetime.utcnow()
        )
        embed.set_thumbnail(url=member.display_avatar.url)
        embed.add_field(name="ID", value=member.id, inline=True)
        embed.add_field(name="Nickname", value=member.nick or "None", inline=True)
        embed.add_field(name="Top Role", value=member.top_role.mention, inline=True)
        embed.add_field(name="Joined Server", value=member.joined_at.strftime("%b %d, %Y"), inline=True)
        embed.add_field(name="Account Created", value=member.created_at.strftime("%b %d, %Y"), inline=True)
        await ctx.send(embed=embed)

    @commands.command(name="bilgi", aliases=["yardım", "komutlar"])
    async def bilgi(self, ctx):
        """Tüm komutları listeler."""
        embed = discord.Embed(
            title="📋 Komut Listesi",
            color=0xFF8C00
        )

        embed.add_field(
            name="🛡️ Moderasyon",
            value=(
                "`!ban @kişi sebep` — Üyeyi banlar\n"
                "`!unban kullanıcı#0000` — Banı kaldırır\n"
                "`!kick @kişi sebep` — Üyeyi atar\n"
                "`!sil 10` — Mesajları siler (max 100)\n"
                "`!timeout @kişi dakika sebep` — Susturur\n"
                "`!untimeout @kişi` — Susturmayı kaldırır\n"
                "`!uyar @kişi sebep` — DM ile uyarı gönderir\n"
                "`!yavaşmod 5` — Yavaş mod ayarlar"
            ),
            inline=False
        )

        embed.add_field(
            name="🎉 Eğlence",
            value=(
                "`!8ball soru` — Sihirli 8 top\n"
                "`!roll 6` — Zar atar\n"
                "`!flip` — Yazı tura\n"
                "`!choose seçenek1, seçenek2` — Seçim yapar"
            ),
            inline=False
        )

        embed.add_field(
            name="ℹ️ Genel",
            value=(
                "`!bilgi` — Bu menü\n"
                "`!ping` — Bot gecikmesi\n"
                "`!info` — Sunucu bilgisi\n"
                "`!userinfo @kişi` — Kullanıcı bilgisi\n"
                "`!avatar @kişi` — Profil fotoğrafı"
            ),
            inline=False
        )

        embed.set_footer(text=f"{ctx.guild.name} • Prefix: !")
        await ctx.send(embed=embed)

    @app_commands.command(name="ping", description="Check the bot's latency")
    async def slash_ping(self, interaction: discord.Interaction):
        latency = round(self.bot.latency * 1000)
        await interaction.response.send_message(f"Pong! `{latency}ms`")

    @app_commands.command(name="pfp", description="Re:Zero karakterlerinden rastgele profil resmi göster")
    @app_commands.allowed_installs(guilds=True, users=True)
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    async def slash_pfp(self, interaction: discord.Interaction):
        await interaction.response.defer()

        # Re:Zero anime MAL ID: 31240
        REZERO_IDS = [116679, 116678, 116680, 116681, 116682, 116683, 116684, 116685, 116686, 116687]

        query = """
        query {
          Media(id: 21355, type: ANIME) {
            characters(sort: FAVOURITES_DESC, perPage: 25) {
              nodes {
                name { full }
                image { large }
              }
            }
          }
        }
        """

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    "https://graphql.anilist.co",
                    json={"query": query},
                    headers={"Content-Type": "application/json"}
                ) as resp:
                    data = await resp.json()

            karakterler = data["data"]["Media"]["characters"]["nodes"]
            karakterler = [k for k in karakterler if k.get("image", {}).get("large")]

            if not karakterler:
                await interaction.followup.send("❌ Resim bulunamadı, tekrar dene!")
                return

            secilen = random.choice(karakterler)
            karakter_adi = secilen["name"]["full"]
            resim_url = secilen["image"]["large"]

            embed = discord.Embed(
                title=f"Re:Zero — {karakter_adi}",
                color=0xFF8C00
            )
            embed.set_image(url=resim_url)
            embed.set_footer(text="Re:Zero Starting Life in Another World")
            await interaction.followup.send(embed=embed)

        except Exception as e:
            await interaction.followup.send(f"❌ Bir hata oluştu, tekrar dene!")

    @app_commands.command(name="avatar", description="Bir kullanıcının profil fotoğrafını göster")
    @app_commands.allowed_installs(guilds=True, users=True)
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    async def slash_avatar(self, interaction: discord.Interaction, kullanıcı: discord.User = None):
        hedef = kullanıcı or interaction.user
        embed = discord.Embed(
            title=f"{hedef.display_name} — Profil Fotoğrafı",
            color=0xFF8C00
        )
        embed.set_image(url=hedef.display_avatar.url)
        embed.add_field(name="İndir", value=f"[PNG]({hedef.display_avatar.with_format('png').url}) | [JPG]({hedef.display_avatar.with_format('jpg').url}) | [WebP]({hedef.display_avatar.with_format('webp').url})")
        await interaction.response.send_message(embed=embed)

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return

        temiz = message.content.lower().strip()

        if temiz in ["sa", "s.a", "s.a.", "selamün aleyküm", "selamun aleyküm",
                     "selamün aleykum", "selam aleyküm"]:
            embed = discord.Embed(
                description="🌙 **Ve Aleyküm Selam ve Rahmetullahi ve Berekatüh** ☪️",
                color=0x2ecc71
            )
            await message.channel.send(embed=embed)

async def setup(bot):
    await bot.add_cog(General(bot))
