import discord
from discord.ext import commands
import datetime

LOG_KANAL_ID = 1515031747774120101
CEZA_LOG_ID = 1515031746935132243

class ModLog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def log_gonder(self, embed):
        kanal = self.bot.get_channel(LOG_KANAL_ID)
        if kanal:
            await kanal.send(embed=embed)

    async def ceza_log_gonder(self, embed):
        kanal = self.bot.get_channel(CEZA_LOG_ID)
        if kanal:
            await kanal.send(embed=embed)

    @commands.Cog.listener()
    async def on_member_ban(self, guild, user):
        embed = discord.Embed(
            title="🔨 Üye Banlandı",
            color=discord.Color.red(),
            timestamp=datetime.datetime.utcnow()
        )
        embed.set_thumbnail(url=user.display_avatar.url)
        embed.add_field(name="Kullanıcı", value=f"{user} ({user.id})", inline=False)
        embed.set_footer(text=f"Sunucu: {guild.name}")
        await self.ceza_log_gonder(embed)

    @commands.Cog.listener()
    async def on_member_unban(self, guild, user):
        embed = discord.Embed(
            title="✅ Ban Kaldırıldı",
            color=discord.Color.green(),
            timestamp=datetime.datetime.utcnow()
        )
        embed.set_thumbnail(url=user.display_avatar.url)
        embed.add_field(name="Kullanıcı", value=f"{user} ({user.id})", inline=False)
        embed.set_footer(text=f"Sunucu: {guild.name}")
        await self.ceza_log_gonder(embed)

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        embed = discord.Embed(
            title="👢 Üye Ayrıldı / Atıldı",
            color=discord.Color.orange(),
            timestamp=datetime.datetime.utcnow()
        )
        embed.set_thumbnail(url=member.display_avatar.url)
        embed.add_field(name="Kullanıcı", value=f"{member} ({member.id})", inline=False)
        embed.add_field(name="Sunucuya Katılma", value=member.joined_at.strftime("%d.%m.%Y") if member.joined_at else "Bilinmiyor", inline=False)
        embed.set_footer(text=f"Sunucu: {member.guild.name}")
        await self.log_gonder(embed)

    @commands.Cog.listener()
    async def on_message_delete(self, message):
        if message.author.bot:
            return
        embed = discord.Embed(
            title="🗑️ Mesaj Silindi",
            color=discord.Color.blurple(),
            timestamp=datetime.datetime.utcnow()
        )
        embed.set_thumbnail(url=message.author.display_avatar.url)
        embed.add_field(name="Kullanıcı", value=f"{message.author} ({message.author.id})", inline=False)
        embed.add_field(name="Kanal", value=message.channel.mention, inline=False)
        embed.add_field(name="Mesaj", value=message.content or "*[içerik yok]*", inline=False)
        await self.log_gonder(embed)

    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        if before.author.bot:
            return
        if before.content == after.content:
            return
        embed = discord.Embed(
            title="✏️ Mesaj Düzenlendi",
            color=discord.Color.yellow(),
            timestamp=datetime.datetime.utcnow()
        )
        embed.set_thumbnail(url=before.author.display_avatar.url)
        embed.add_field(name="Kullanıcı", value=f"{before.author} ({before.author.id})", inline=False)
        embed.add_field(name="Kanal", value=before.channel.mention, inline=False)
        embed.add_field(name="Önceki", value=before.content or "*[boş]*", inline=False)
        embed.add_field(name="Sonraki", value=after.content or "*[boş]*", inline=False)
        embed.add_field(name="Mesaj Linki", value=f"[Tıkla]({after.jump_url})", inline=False)
        await self.log_gonder(embed)

    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        if before.timed_out_until == after.timed_out_until:
            return
        if after.timed_out_until:
            embed = discord.Embed(
                title="🔇 Üye Susturuldu",
                color=discord.Color.yellow(),
                timestamp=datetime.datetime.utcnow()
            )
            embed.set_thumbnail(url=after.display_avatar.url)
            embed.add_field(name="Kullanıcı", value=f"{after} ({after.id})", inline=False)
            embed.add_field(name="Bitiş", value=after.timed_out_until.strftime("%d.%m.%Y %H:%M"), inline=False)
        else:
            embed = discord.Embed(
                title="🔊 Susturma Kaldırıldı",
                color=discord.Color.green(),
                timestamp=datetime.datetime.utcnow()
            )
            embed.set_thumbnail(url=after.display_avatar.url)
            embed.add_field(name="Kullanıcı", value=f"{after} ({after.id})", inline=False)
        await self.ceza_log_gonder(embed)

async def setup(bot):
    await bot.add_cog(ModLog(bot))
