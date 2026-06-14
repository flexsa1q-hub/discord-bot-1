import discord
from discord.ext import commands
import os
import asyncio
from flask import Flask
from threading import Thread

app = Flask(__name__)

@app.route("/")
def home():
    return "Bot çalışıyor!", 200

def run_server():
    app.run(host="0.0.0.0", port=5000)

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

KANAL_ID = 1515031746935132246

COGS = [
    "cogs.general",
    "cogs.moderation",
    "cogs.fun",
    "cogs.modlog",
]

@bot.event
async def on_ready():
    print(f"{bot.user} aktif!")
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} slash command(s)")
    except Exception as e:
        print(f"Failed to sync commands: {e}")


@bot.event
async def on_member_join(member):
    try:
        kanal = bot.get_channel(KANAL_ID) or await bot.fetch_channel(KANAL_ID)

        embed = discord.Embed(
            title="🌷 A R T A K S 🌷",
            description=(
                f"🌸 Hoş geldin {member.mention}!\n\n"
                "🦂 <#1515031746935132241> göz atmayı unutma.\n\n"
                "🦂 <#1515031746935132248> kanalında topluluğumuzla tanışabilir, sohbet edip eğlenebilirsin.\n\n"
                "🦂 <#1515043749061853277> herhangi bir sorun yaşarsan ticket sistemini kullanarak yetkililere ulaşabilirsin.\n\n"
                "🔥 Aramıza hoş geldin, keyifli sohbetler ve iyi eğlenceler! ❤️"
            ),
            color=0xFF8C00
        )

        embed.set_thumbnail(url=member.display_avatar.url)
        embed.set_image(url="https://cdn.discordapp.com/attachments/1462597209118740490/1515353358905507970/shaula-shaula-re-zero-ezgif.com-video-to-gif-converter.gif")

        await kanal.send(embed=embed)
        print(f"Hoş geldin mesajı gönderildi: {member}")
    except Exception as e:
        print(f"Hoş geldin mesajı gönderilemedi: {e}")


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        return
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("Bu komutu kullanmak için yetkin yok.")
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(f"Eksik argüman: `{error.param.name}`")
    else:
        await ctx.send(f"Bir hata oluştu: {error}")
        raise error


async def load_cogs():
    for cog in COGS:
        try:
            await bot.load_extension(cog)
            print(f"Loaded cog: {cog}")
        except Exception as e:
            print(f"Failed to load cog {cog}: {e}")


async def main():
    token = os.getenv("DISCORD_TOKEN")
    if not token:
        raise ValueError("DISCORD_TOKEN environment variable is not set.")
    async with bot:
        await load_cogs()
        await bot.start(token)


if __name__ == "__main__":
    Thread(target=run_server, daemon=True).start()
    asyncio.run(main())
