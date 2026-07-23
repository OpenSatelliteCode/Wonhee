"""
Bot de Discord: Wonhee
Genera una tarjeta de bienvenida (foto de perfil en círculo + texto) para
cada persona que entra al servidor de "Empresas de Kpop".
"""

import io
import os

import discord
from discord.ext import commands
from PIL import Image, ImageDraw, ImageFont

# ---------- CONFIG ----------
TOKEN = os.getenv("DISCORD_TOKEN", "PON_TU_TOKEN_AQUI")

# Si quieres que salude en un canal específico, pon su nombre aquí.
# Si lo dejas en None, va a buscar el canal "de bienvenidas" del server
# (el que Discord marca como system_channel) o el primer canal de texto.
CANAL_BIENVENIDA = None  # ej: "bienvenidas"

TEXTO_TARJETA = "EMPRESAS DE KPOP ::!"
FONT_PATH = os.path.join(os.path.dirname(__file__), "fonts", "Diskopia.ttf")
# -----------------------------

intents = discord.Intents.default()
intents.members = True  # necesario pa detectar cuando alguien entra

bot = commands.Bot(command_prefix="!", intents=intents)


def generar_tarjeta(avatar_bytes: bytes) -> io.BytesIO:
    """Crea la tarjeta: foto de perfil en círculo + texto abajo, fondo blanco."""
    ANCHO, ALTO = 1000, 1000
    DIAMETRO_AVATAR = 550

    canvas = Image.new("RGB", (ANCHO, ALTO), "white")

    # --- Avatar en círculo ---
    avatar = Image.open(io.BytesIO(avatar_bytes)).convert("RGBA")
    avatar = avatar.resize((DIAMETRO_AVATAR, DIAMETRO_AVATAR))

    mascara = Image.new("L", (DIAMETRO_AVATAR, DIAMETRO_AVATAR), 0)
    draw_mask = ImageDraw.Draw(mascara)
    draw_mask.ellipse((0, 0, DIAMETRO_AVATAR, DIAMETRO_AVATAR), fill=255)

    avatar_circular = Image.new("RGBA", (DIAMETRO_AVATAR, DIAMETRO_AVATAR))
    avatar_circular.paste(avatar, (0, 0), mascara)

    pos_x = (ANCHO - DIAMETRO_AVATAR) // 2
    pos_y = 80
    canvas.paste(avatar_circular, (pos_x, pos_y), avatar_circular)

    # --- Texto abajo ---
    draw = ImageDraw.Draw(canvas)
    tam_fuente = 60
    font = ImageFont.truetype(FONT_PATH, tam_fuente)

    bbox = draw.textbbox((0, 0), TEXTO_TARJETA, font=font)
    ancho_texto = bbox[2] - bbox[0]
    texto_x = (ANCHO - ancho_texto) // 2
    texto_y = pos_y + DIAMETRO_AVATAR + 60

    draw.text((texto_x, texto_y), TEXTO_TARJETA, font=font, fill="black")

    buffer = io.BytesIO()
    canvas.save(buffer, "PNG")
    buffer.seek(0)
    return buffer


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

    avatar_bytes = await member.display_avatar.read()
    tarjeta = generar_tarjeta(avatar_bytes)

    archivo = discord.File(tarjeta, filename="bienvenida.png")
    await canal.send(content=f"Bienvenido {member.mention} 🎤", file=archivo)


bot.run(TOKEN)
