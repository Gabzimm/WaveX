import discord
import os
from discord.ext import commands
from flask import Flask
from threading import Thread

# Parte para manter o bot ativo no Render (Web Service)
app = Flask('')

@app.route('/')
def home():
    return "Bot está online!"

def run():
    app.run(host='0.0.0.0', port=10000)

def keep_alive():
    t = Thread(target=run)
    t.start()

# Inicia o servidor web
keep_alive()

# Configuração do bot Discord
intents = discord.Intents.default()
intents.message_content = True  # Se precisar ler mensagens
bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'Bot {bot.user} está online!')

# Seus comandos aqui
@bot.command()
async def ping(ctx):
    await ctx.send('Pong!')

# Pega o token das variáveis de ambiente do Render
token = os.getenv('DISCORD_TOKEN')
bot.run(token)
