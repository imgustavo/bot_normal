import discord
from discord.ext import commands
import sqlite3
import os
from datetime import datetime

# Configurar el bot
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='.', intents=intents)

# ========== CONFIGURACIÓN DE BASE DE DATOS ==========
def init_db():
    """Inicializa la base de datos y crea las tablas si no existen"""
    conn = sqlite3.connect('facultad.db')
    c = conn.cursor()
    
    # Tabla de tareas (GLOBALES - todos los alumnos ven las mismas)
    c.execute('''CREATE TABLE IF NOT EXISTS tareas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        tarea TEXT NOT NULL,
        fecha_creacion TEXT NOT NULL,
        fecha_entrega TEXT,
        completada INTEGER DEFAULT 0,
        creada_por TEXT
    )''')
    
    # Tabla de eventos académicos (parciales y finales)
    c.execute('''CREATE TABLE IF NOT EXISTS eventos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        tipo TEXT NOT NULL,  -- "parcial" o "final"
        materia TEXT NOT NULL,
        fecha TEXT NOT NULL,
        hora TEXT,
        aula TEXT,
        descripcion TEXT
    )''')
    
    conn.commit()
    conn.close()

# ========== FUNCIONES PARA TAREAS ==========
def agregar_tarea_db(tarea, fecha_entrega=None, creada_por=""):
    """Guarda una tarea global"""
    conn = sqlite3.connect('facultad.db')
    c = conn.cursor()
    c.execute("""INSERT INTO tareas (tarea, fecha_creacion, fecha_entrega, creada_por) 
                 VALUES (?, ?, ?, ?)""",
              (tarea, datetime.now().strftime("%d/%m/%Y %H:%M"), fecha_entrega, creada_por))
    conn.commit()
    conn.close()

def obtener_tareas_db(solo_pendientes=True):
    """Obtiene todas las tareas globales"""
    conn = sqlite3.connect('facultad.db')
    c = conn.cursor()
    if solo_pendientes:
        c.execute("SELECT id, tarea, fecha_creacion, fecha_entrega, creada_por FROM tareas WHERE completada = 0 ORDER BY id DESC")
    else:
        c.execute("SELECT id, tarea, fecha_creacion, fecha_entrega, creada_por, completada FROM tareas ORDER BY id DESC")
    tareas = c.fetchall()
    conn.close()
    return tareas

def completar_tarea_db(tarea_id):
    """Marca una tarea como completada"""
    conn = sqlite3.connect('facultad.db')
    c = conn.cursor()
    c.execute("UPDATE tareas SET completada = 1 WHERE id = ?", (tarea_id,))
    conn.commit()
    conn.close()
    return c.rowcount > 0

def eliminar_tarea_db(tarea_id):
    """Elimina una tarea"""
    conn = sqlite3.connect('facultad.db')
    c = conn.cursor()
    c.execute("DELETE FROM tareas WHERE id = ?", (tarea_id,))
    conn.commit()
    conn.close()
    return c.rowcount > 0

# ========== FUNCIONES PARA PARCIALES Y FINALES ==========
def agregar_evento_db(tipo, materia, fecha, hora="", aula="", descripcion=""):
    """Agrega un parcial o final"""
    conn = sqlite3.connect('facultad.db')
    c = conn.cursor()
    c.execute("""INSERT INTO eventos (tipo, materia, fecha, hora, aula, descripcion) 
                 VALUES (?, ?, ?, ?, ?, ?)""",
              (tipo, materia, fecha, hora, aula, descripcion))
    conn.commit()
    conn.close()

def obtener_eventos_db(tipo=None):
    """Obtiene todos los eventos (parciales y/o finales)"""
    conn = sqlite3.connect('facultad.db')
    c = conn.cursor()
    if tipo:
        c.execute("SELECT id, materia, fecha, hora, aula, descripcion FROM eventos WHERE tipo = ? ORDER BY fecha", (tipo,))
    else:
        c.execute("SELECT id, tipo, materia, fecha, hora, aula, descripcion FROM eventos ORDER BY fecha")
    eventos = c.fetchall()
    conn.close()
    return eventos

def eliminar_evento_db(evento_id):
    """Elimina un evento"""
    conn = sqlite3.connect('facultad.db')
    c = conn.cursor()
    c.execute("DELETE FROM eventos WHERE id = ?", (evento_id,))
    conn.commit()
    conn.close()
    return c.rowcount > 0

# Inicializar la base de datos
init_db()

# ========== COMANDOS DEL BOT ==========

@bot.event
async def on_ready():
    print(f'✅ Bot conectado como {bot.user}')
    print(f'📁 Base de datos: facultad.db')

@bot.command(name='ayuda')
async def ayuda(ctx):
    """Muestra todos los comandos disponibles"""
    embed = discord.Embed(
        title="📚 Comandos de la Facultad",
        description="Todos los comandos disponibles:",
        color=discord.Color.blue()
    )
    embed.add_field(name="📝 **Tareas**", value="`.tareas` - Ver tareas pendientes\n`.agregar_tarea [tarea]` - Agregar tarea (admin)\n`.completar_tarea [número]` - Marcar tarea como hecha\n`.eliminar_tarea [número]` - Eliminar tarea (admin)", inline=False)
    embed.add_field(name="📅 **Parciales y Finales**", value="`.parciales` - Ver todos los parciales y finales\n`.agregar_parcial [materia] [fecha]` - Agregar parcial (admin)\n`.agregar_final [materia] [fecha]` - Agregar final (admin)\n`.eliminar_evento [número]` - Eliminar evento (admin)", inline=False)
    embed.add_field(name="ℹ️ **General**", value="`.ayuda` - Mostrar este mensaje", inline=False)
    embed.set_footer(text="Los comandos .agregar_* y .eliminar_* son solo para administradores")
    
    await ctx.send(embed=embed)

# ========== COMANDOS DE TAREAS ==========

@bot.command(name='tareas')
async def mostrar_tareas(ctx):
    """Muestra todas las tareas pendientes (globales)"""
    tareas = obtener_tareas_db(solo_pendientes=True)
    
    if tareas:
        mensaje = "📝 **TAREAS PENDIENTES DE LA FACULTAD**\n\n"
        for i, (tid, tarea, fecha_creacion, fecha_entrega, creada_por) in enumerate(tareas, 1):
            mensaje += f"**{i}.** {tarea}\n"
            mensaje += f"   📅 Creada: {fecha_creacion}\n"
            if fecha_entrega:
                mensaje += f"   ⏰ Entrega: {fecha_entrega}\n"
            if creada_por:
                mensaje += f"   👤 Agregada por: {creada_por}\n"
            mensaje += "\n"
        
        mensaje += "💡 Para marcar una tarea como completada: `.completar_tarea [número]`"
        await ctx.send(mensaje)
    else:
        await ctx.send("📭 ¡No hay tareas pendientes! 🎉")

@bot.command(name='agregar_tarea')
async def agregar_tarea(ctx, *, tarea):
    """Agrega una nueva tarea global (solo admins)"""
    if not ctx.author.guild_permissions.administrator:
        await ctx.send("❌ Solo los administradores pueden agregar tareas.")
        return
    
    # Permitir formato: "tarea | fecha_entrega"
    partes = tarea.split("|")
    descripcion = partes[0].strip()
    fecha_entrega = partes[1].strip() if len(partes) > 1 else None
    
    agregar_tarea_db(descripcion, fecha_entrega, ctx.author.display_name)
    await ctx.send(f"✅ Tarea agregada: **{descripcion}**\n📌 Para todos los alumnos")

@bot.command(name='completar_tarea')
async def completar_tarea(ctx, numero: int):
    """Marca una tarea como completada (cualquier alumno puede hacerlo)"""
    tareas = obtener_tareas_db(solo_pendientes=True)
    
    if not tareas:
        await ctx.send("📭 No hay tareas pendientes.")
        return
    
    if numero < 1 or numero > len(tareas):
        await ctx.send(f"❌ Número inválido. Tenés {len(tareas)} tarea(s) pendiente(s). Usá `.tareas` para verlas.")
        return
    
    tarea_id = tareas[numero - 1][0]
    tarea_texto = tareas[numero - 1][1]
    
    if completar_tarea_db(tarea_id):
        await ctx.send(f"✅ **{ctx.author.display_name}** completó la tarea: *{tarea_texto}* 🎉")
    else:
        await ctx.send("❌ Hubo un error al completar la tarea.")

@bot.command(name='eliminar_tarea')
async def eliminar_tarea(ctx, numero: int):
    """Elimina una tarea (solo admins)"""
    if not ctx.author.guild_permissions.administrator:
        await ctx.send("❌ Solo los administradores pueden eliminar tareas.")
        return
    
    tareas = obtener_tareas_db(solo_pendientes=True)
    
    if not tareas:
        await ctx.send("📭 No hay tareas para eliminar.")
        return
    
    if numero < 1 or numero > len(tareas):
        await ctx.send(f"❌ Número inválido. Usá `.tareas` para ver la lista.")
        return
    
    tarea_id = tareas[numero - 1][0]
    tarea_texto = tareas[numero - 1][1]
    
    if eliminar_tarea_db(tarea_id):
        await ctx.send(f"✅ Tarea eliminada: *{tarea_texto}*")

# ========== COMANDOS DE PARCIALES Y FINALES ==========

@bot.command(name='parciales')
async def mostrar_eventos(ctx):
    """Muestra todos los parciales y finales"""
    eventos = obtener_eventos_db()
    
    if eventos:
        embed = discord.Embed(
            title="📅 CALENDARIO ACADÉMICO",
            description="Parciales y Finales",
            color=discord.Color.gold()
        )
        
        for evento in eventos:
            event_id, tipo, materia, fecha, hora, aula, descripcion = evento
            
            # Emoji según el tipo
            emoji = "📝" if tipo == "parcial" else "🎓"
            titulo = f"{emoji} **{tipo.upper()}** - {materia}"
            
            valor = f"📆 **Fecha:** {fecha}\n"
            if hora:
                valor += f"⏰ **Hora:** {hora}\n"
            if aula:
                valor += f"🏛️ **Aula:** {aula}\n"
            if descripcion:
                valor += f"📌 {descripcion}\n"
            valor += f"\n`ID: {event_id}`"
            
            embed.add_field(name=titulo, value=valor, inline=False)
        
        embed.set_footer(text='Usá .eliminar_evento [ID] para eliminar (solo admins)')
        await ctx.send(embed=embed)
    else:
        await ctx.send("📭 No hay parciales ni finales cargados.")

@bot.command(name='agregar_parcial')
async def agregar_parcial(ctx, materia, *, fecha):
    """Agrega un parcial (solo admins)"""
    if not ctx.author.guild_permissions.administrator:
        await ctx.send("❌ Solo los administradores pueden agregar parciales.")
        return
    
    agregar_evento_db("parcial", materia, fecha)
    await ctx.send(f"✅ Parcial de **{materia}** agregado para el **{fecha}**")

@bot.command(name='agregar_final')
async def agregar_final(ctx, materia, *, fecha):
    """Agrega un final (solo admins)"""
    if not ctx.author.guild_permissions.administrator:
        await ctx.send("❌ Solo los administradores pueden agregar finales.")
        return
    
    agregar_evento_db("final", materia, fecha)
    await ctx.send(f"✅ Final de **{materia}** agregado para el **{fecha}**")

@bot.command(name='eliminar_evento')
async def eliminar_evento(ctx, evento_id: int):
    """Elimina un evento por su ID (solo admins)"""
    if not ctx.author.guild_permissions.administrator:
        await ctx.send("❌ Solo los administradores pueden eliminar eventos.")
        return
    
    if eliminar_evento_db(evento_id):
        await ctx.send(f"✅ Evento eliminado correctamente.")
    else:
        await ctx.send("❌ No se encontró un evento con ese ID. Usá `.parciales` para ver los IDs.")

# ========== COMANDO EXTRA: TAREAS COMPLETADAS ==========
@bot.command(name='historial')
async def ver_historial(ctx):
    """Muestra todas las tareas (incluyendo completadas) - solo admins"""
    if not ctx.author.guild_permissions.administrator:
        await ctx.send("❌ Solo administradores pueden ver el historial completo.")
        return
    
    tareas = obtener_tareas_db(solo_pendientes=False)
    
    if tareas:
        completadas = [t for t in tareas if t[5] == 1]
        pendientes = [t for t in tareas if t[5] == 0]
        
        mensaje = "📊 **ESTADÍSTICAS DE TAREAS**\n\n"
        mensaje += f"✅ Completadas: {len(completadas)}\n"
        mensaje += f"⏳ Pendientes: {len(pendientes)}\n"
        mensaje += f"📋 Total: {len(tareas)}\n"
        
        await ctx.send(mensaje)
    else:
        await ctx.send("No hay tareas registradas.")

# Ejecutar el bot
bot.run(os.getenv('DISCORD_TOKEN'))
