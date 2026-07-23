"""
Bot de Discord: Wonhee
Saluda automáticamente a cada persona que entra al servidor.
"""

import os
import discord
from discord.ext import commands

# ---------- CONFIG ----------
TOKEN = os.getenv("DISCORD_TOKEN", "MTUyOTk1ODg4ODUxMjgxNTIyNA.GCRBqi.mBWwNpapKtGaPDqh_X9AHA9GvWApTLMYldxG2c")

# Si quieres que salude en un canal específico, pon su nombre aquí.
# Si lo dejas en None, va a buscar el canal "de bienvenidas" del server
# (el que Discord marca como system_channel) o el primer canal de texto.
CANAL_BIENVENIDA = None  # ej: "bienvenidas"
# -----------------------------

intents = discord.Intents.default()
intents.members = True  # necesario pa detectar cuando alguien entra

bot = commands.Bot(command_prefix="!", intents=intents)


@bot.event
async def on_ready():
    print(f"✅ {bot.user} está conectado y listo pa saludar como se debe.")


@bot.event
async def on_member_join(member: discord.Member):
    guild = member.guild

    # Buscar canal destino
    canal = None
    if CANAL_BIENVENIDA:
        canal = discord.utils.get(guild.text_channels, name=CANAL_BIENVENIDA)

    if canal is None:
        canal = guild.system_channel or next(
            (c for c in guild.text_channels if c.permissions_for(guild.me).send_messages),
            None,
        )

    if canal is None:
        return  # no hay a dónde mandar el mensaje, ni pex

    mensajes = [
        f"🎉 ¡Órale {member.mention}, bienvenido a **{guild.name}**! Wonhee te está vigilando 👀",
        f"🥳 Llegó {member.mention} al chat, ¡bienvenido wey!",
        f"👋 {member.mention} acaba de aterrizar en **{guild.name}**. ¡No te pierdas!",
    ]
    import random
    await canal.send(random.choice(mensajes))


bot.run(TOKEN)
