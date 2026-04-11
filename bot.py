import discord
from discord.ext import commands
import os

# Configurar el bot con prefijo "."
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='.', intents=intents)

# Diccionario para almacenar datos (en un proyecto real usarías una base de datos)
tareas = {}
parciales = {}

@bot.event
async def on_ready():
    print(f'✅ Bot conectado como {bot.user}')

@bot.command(name='ayuda')
async def ayuda(ctx):
    """Muestra todos los comandos disponibles"""
    embed = discord.Embed(
        title="📚 Comandos disponibles",
        description="Estos son los comandos que podés usar:",
        color=discord.Color.blue()
    )
    embed.add_field(name=".ayuda", value="Muestra este mensaje de ayuda", inline=False)
    embed.add_field(name=".tareas", value="Muestra la lista de tareas pendientes", inline=False)
    embed.add_field(name=".parciales", value="Muestra las fechas de parciales", inline=False)
    embed.add_field(name=".agregar_tarea [tarea]", value="Agrega una nueva tarea", inline=False)
    embed.add_field(name=".agregar_parcial [materia] [fecha]", value="Agrega un parcial", inline=False)
    
    await ctx.send(embed=embed)

@bot.command(name='tareas')
async def mostrar_tareas(ctx):
    """Muestra todas las tareas"""
    usuario = str(ctx.author.id)
    
    if usuario in tareas and tareas[usuario]:
        lista = "\n".join([f"• {i+1}. {t}" for i, t in enumerate(tareas[usuario])])
        await ctx.send(f"📝 **Tus tareas:**\n{lista}")
    else:
        await ctx.send("📭 No tenés tareas pendientes. Usá `.agregar_tarea [tarea]` para agregar una.")

@bot.command(name='parciales')
async def mostrar_parciales(ctx):
    """Muestra todos los parciales"""
    if parciales:
        lista = "\n".join([f"• **{materia}**: {fecha}" for materia, fecha in parciales.items()])
        await ctx.send(f"📅 **Próximos parciales:**\n{lista}")
    else:
        await ctx.send("📭 No hay parciales cargados. Usá `.agregar_parcial [materia] [fecha]` para agregar uno.")

@bot.command(name='agregar_tarea')
async def agregar_tarea(ctx, *, tarea):
    """Agrega una nueva tarea (solo para el usuario)"""
    usuario = str(ctx.author.id)
    
    if usuario not in tareas:
        tareas[usuario] = []
    
    tareas[usuario].append(tarea)
    await ctx.send(f"✅ Tarea agregada: **{tarea}**")

@bot.command(name='agregar_parcial')
async def agregar_parcial(ctx, materia, *, fecha):
    """Agrega un parcial para toda la facultad"""
    parciales[materia] = fecha
    await ctx.send(f"✅ Parcial de **{materia}** agregado para el **{fecha}**")

# Servidor web falso para mantener a Render feliz
from flask import Flask
import threading

app = Flask('')

@app.route('/')
def home():
    return "Bot de Discord activo!"

def run():
    port = int(os.getenv('PORT', 10000))
    app.run(host='0.0.0.0', port=port)

threading.Thread(target=run).start()

# Ejecutar el bot
bot.run(os.getenv('DISCORD_TOKEN'))
