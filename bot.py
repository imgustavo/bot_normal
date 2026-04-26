import discord
from discord.ext import commands
import os
import asyncio
from flask import Flask
from threading import Thread

# ---- 1. CONFIGURACIÓN INICIAL ----
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='.', intents=intents)

tareas = {}
parciales = {}

# ---- 2. SERVIDOR WEB (SOLO SI USAS WEB SERVICE) ----
app = Flask('')

@app.route('/')
def home():
    return "Bot de Discord funcionando correctamente."

def run():
    port = int(os.getenv('PORT', 10000))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run)
    t.start()

# ---- 3. MANEJO DE ERRORES DE COMANDOS ----
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        # Mensaje de ayuda si faltan argumentos
        await ctx.send(f"⚠️ **Ups!** Te faltó información. Para usar `{ctx.prefix}{ctx.command.name}`, escribí:\n`{ctx.prefix}{ctx.command.qualified_name} {ctx.command.signature}`")
    elif isinstance(error, commands.CommandNotFound):
        # Ignorar comandos no existentes
        pass
    else:
        # Otro error inesperado
        await ctx.send(f"❌ Ocurrió un error: {error}")

# ---- 4. LÓGICA PRINCIPAL DE TUS COMANDOS ----
@bot.command(name='ayuda')
async def ayuda(ctx):
    # ... (tu código existente) ...
    embed = discord.Embed(title="...", description="...", color=discord.Color.blue())
    # ... agregar campos del embed ...
    await ctx.send(embed=embed)

@bot.command(name='tareas')
async def mostrar_tareas(ctx):
    usuario = str(ctx.author.id)
    if usuario in tareas and tareas[usuario]:
        lista = "\n".join([f"• {i+1}. {t}" for i, t in enumerate(tareas[usuario])])
        await ctx.send(f"📝 **Tus tareas:**\n{lista}")
    else:
        await ctx.send("📭 No tenés tareas pendientes.")

@bot.command(name='parciales')
async def mostrar_parciales(ctx):
    if parciales:
        lista = "\n".join([f"• **{materia}**: {fecha}" for materia, fecha in parciales.items()])
        await ctx.send(f"📅 **Próximos parciales:**\n{lista}")
    else:
        await ctx.send("📭 No hay parciales cargados.")

@bot.command(name='agregar_tarea')
async def agregar_tarea(ctx, *, tarea):
    usuario = str(ctx.author.id)
    if usuario not in tareas:
        tareas[usuario] = []
    tareas[usuario].append(tarea)
    await ctx.send(f"✅ Tarea agregada: **{tarea}**")

@bot.command(name='agregar_parcial')
async def agregar_parcial(ctx, materia, *, fecha):
    parciales[materia] = fecha
    await ctx.send(f"✅ Parcial de **{materia}** agregado para el **{fecha}**")

# ---- 5. INICIO DEL BOT ----
if __name__ == "__main__":
    token = os.getenv('DISCORD_TOKEN')
    if not token:
        print("Error: No se encontró la variable de entorno DISCORD_TOKEN.")
        exit(1)
    
    # Opcional: Activar servidor web solo si estás usando Web Service.
    # Si usas Background Worker, comenta o elimina la siguiente línea:
    # keep_alive()
    
    bot.run(token)