import discord
from discord.ext import commands
from discord import app_commands
import random

EIGHT_BALL_RESPONSES = [
    "Kesinlikle evet.", "Şüphesiz.", "Evet, kesinlikle.",
    "Bence evet.", "Büyük ihtimalle.", "Görünüşe göre evet.",
    "Evet.", "İşaretler evet diyor.", "Şimdilik cevap veremem.",
    "Tekrar sor.", "Şu an söylemek istemiyorum.", "Tahmin edemiyorum.",
    "Konsantre ol ve tekrar sor.", "Güvenme.", "Hayır.",
    "Kaynaklarım hayır diyor.", "Pek iyi görünmüyor.", "Çok şüpheliyim.",
]

class TasKagitMakasView(discord.ui.View):
    def __init__(self, oyuncu: discord.User):
        super().__init__(timeout=30)
        self.oyuncu = oyuncu
        self.bitti = False

    def sonuc_hesapla(self, oyuncu_secim, bot_secim):
        kazanma = {"taş": "makas", "makas": "kağıt", "kağıt": "taş"}
        if oyuncu_secim == bot_secim:
            return "berabere"
        elif kazanma[oyuncu_secim] == bot_secim:
            return "kazandı"
        else:
            return "kaybetti"

    async def oyna(self, interaction: discord.Interaction, oyuncu_secim: str):
        if interaction.user.id != self.oyuncu.id:
            await interaction.response.send_message("Bu senin oyunun değil!", ephemeral=True)
            return
        if self.bitti:
            return

        self.bitti = True
        for item in self.children:
            item.disabled = True

        emojiler = {"taş": "🪨", "kağıt": "📄", "makas": "✂️"}
        bot_secim = random.choice(["taş", "kağıt", "makas"])
        sonuc = self.sonuc_hesapla(oyuncu_secim, bot_secim)

        if sonuc == "kazandı":
            renk = discord.Color.green()
            baslik = "🏆 Kazandın!"
        elif sonuc == "kaybetti":
            renk = discord.Color.red()
            baslik = "😔 Kaybettin!"
        else:
            renk = discord.Color.yellow()
            baslik = "🤝 Berabere!"

        embed = discord.Embed(title=baslik, color=renk)
        embed.add_field(name="Senin seçimin", value=f"{emojiler[oyuncu_secim]} {oyuncu_secim.capitalize()}", inline=True)
        embed.add_field(name="Botun seçimi", value=f"{emojiler[bot_secim]} {bot_secim.capitalize()}", inline=True)

        await interaction.response.edit_message(embed=embed, view=self)

    @discord.ui.button(label="🪨 Taş", style=discord.ButtonStyle.secondary)
    async def tas(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.oyna(interaction, "taş")

    @discord.ui.button(label="📄 Kağıt", style=discord.ButtonStyle.secondary)
    async def kagit(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.oyna(interaction, "kağıt")

    @discord.ui.button(label="✂️ Makas", style=discord.ButtonStyle.secondary)
    async def makas(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.oyna(interaction, "makas")

    async def on_timeout(self):
        for item in self.children:
            item.disabled = True


class Fun(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="tkm", aliases=["taşkağıtmakas", "rps"])
    async def tkm(self, ctx):
        """Taş Kağıt Makas oyunu."""
        embed = discord.Embed(
            title="🎮 Taş Kağıt Makas",
            description="Seçimini yap!",
            color=0xFF8C00
        )
        view = TasKagitMakasView(ctx.author)
        await ctx.send(embed=embed, view=view)

    @app_commands.command(name="tkm", description="Taş Kağıt Makas oyna")
    @app_commands.allowed_installs(guilds=True, users=True)
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    async def slash_tkm(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="🎮 Taş Kağıt Makas",
            description="Seçimini yap!",
            color=0xFF8C00
        )
        view = TasKagitMakasView(interaction.user)
        await interaction.response.send_message(embed=embed, view=view)

    @commands.command(name="8ball", aliases=["eightball"])
    async def eight_ball(self, ctx, *, question: str):
        """Sihirli 8 top."""
        response = random.choice(EIGHT_BALL_RESPONSES)
        embed = discord.Embed(color=discord.Color.purple())
        embed.add_field(name="Soru", value=question, inline=False)
        embed.add_field(name="Cevap", value=response, inline=False)
        await ctx.send(embed=embed)

    @commands.command(name="roll")
    async def roll(self, ctx, sides: int = 6):
        """Zar atar."""
        result = random.randint(1, sides)
        await ctx.send(f"**{result}** geldi! (d{sides})")

    @commands.command(name="flip")
    async def flip(self, ctx):
        """Yazı tura."""
        result = random.choice(["Yazı", "Tura"])
        await ctx.send(f"Madeni para **{result}** geldi!")

    @commands.command(name="choose")
    async def choose(self, ctx, *, options: str):
        """Virgülle ayrılmış seçeneklerden birini seçer."""
        choices = [o.strip() for o in options.split(",") if o.strip()]
        if len(choices) < 2:
            await ctx.send("En az 2 seçenek gir, virgülle ayır.")
            return
        pick = random.choice(choices)
        await ctx.send(f"Seçim: **{pick}**")

    @commands.command(name="say")
    @commands.has_permissions(manage_messages=True)
    async def say(self, ctx, *, message: str):
        """Botu konuşturur."""
        await ctx.message.delete()
        await ctx.send(message)

async def setup(bot):
    await bot.add_cog(Fun(bot))
