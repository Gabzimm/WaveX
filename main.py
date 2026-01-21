import discord
from discord.ext import commands
import os
from flask import Flask
from threading import Thread

# ========== KEEP ALIVE (Render) ==========
app = Flask('')

@app.route('/')
def home():
    return "Bot está online!"

def run():
    app.run(host='0.0.0.0', port=10000)

def keep_alive():
    t = Thread(target=run)
    t.start()

keep_alive()
# =========================================

# Configuração do bot
intents = discord.Intents.default()
intents.members = True  # NECESSÁRIO para autorole
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)

# Dicionário para cargos (em memória - use database.py para persistente)
auto_roles = {}

@bot.event
async def on_ready():
    print(f'✅ {bot.user} está online!')
    print(f'📊 Servidores: {len(bot.guilds)}')
    await bot.change_presence(activity=discord.Game(name="!autorolehelp"))

# ========== EVENTO: Quando membro entrar ==========
@bot.event
async def on_member_join(member):
    guild_id = member.guild.id
    
    if guild_id in auto_roles:
        for role_id in auto_roles[guild_id]:
            role = member.guild.get_role(role_id)
            if role:
                try:
                    await member.add_roles(role)
                    print(f"👤 Cargo '{role.name}' dado para {member.name}")
                except:
                    print(f"❌ Erro ao dar cargo para {member.name}")

# ========== COMANDOS ==========
@bot.command(name="setautorole")
@commands.has_permissions(manage_roles=True)
async def set_autorole(ctx, role: discord.Role):
    guild_id = ctx.guild.id
    
    if guild_id not in auto_roles:
        auto_roles[guild_id] = []
    
    if role.id not in auto_roles[guild_id]:
        auto_roles[guild_id].append(role.id)
        
        embed = discord.Embed(
            title="✅ Autorole Configurado",
            description=f"Cargo **{role.name}** será dado a novos membros.",
            color=0x00ff00
        )
        await ctx.send(embed=embed)
    else:
        await ctx.send("❌ Este cargo já está configurado.")

@bot.command(name="removeautorole")
@commands.has_permissions(manage_roles=True)
async def remove_autorole(ctx, role: discord.Role):
    guild_id = ctx.guild.id
    
    if guild_id in auto_roles and role.id in auto_roles[guild_id]:
        auto_roles[guild_id].remove(role.id)
        
        embed = discord.Embed(
            title="✅ Autorole Removido",
            description=f"Cargo **{role.name}** removido.",
            color=0xff0000
        )
        await ctx.send(embed=embed)
    else:
        await ctx.send("❌ Cargo não encontrado na lista.")

@bot.command(name="listautoroles")
async def list_autoroles(ctx):
    guild_id = ctx.guild.id
    
    if guild_id in auto_roles and auto_roles[guild_id]:
        embed = discord.Embed(
            title="📋 Cargos Automáticos",
            color=0x0099ff
        )
        
        for role_id in auto_roles[guild_id]:
            role = ctx.guild.get_role(role_id)
            if role:
                embed.add_field(name="Cargo", value=role.mention, inline=False)
        
        await ctx.send(embed=embed)
    else:
        await ctx.send("ℹ️ Use `!setautorole @cargo` para configurar.")

@bot.command(name="testautorole")
@commands.has_permissions(manage_roles=True)
async def test_autorole(ctx, member: discord.Member):
    guild_id = ctx.guild.id
    
    if guild_id in auto_roles:
        given = []
        for role_id in auto_roles[guild_id]:
            role = ctx.guild.get_role(role_id)
            if role and role not in member.roles:
                await member.add_roles(role)
                given.append(role.name)
        
        if given:
            await ctx.send(f"✅ Cargos dados: {', '.join(given)}")
        else:
            await ctx.send("✅ Membro já tem todos os cargos.")
    else:
        await ctx.send("❌ Nenhum autorole configurado.")

@bot.command()
async def autorolehelp(ctx):
    embed = discord.Embed(
        title="🛠️ Comandos de Autorole",
        description="**Prefixo: !**",
        color=0x9b59b6
    )
    
    embed.add_field(name="!setautorole @cargo", value="Configura cargo automático", inline=False)
    embed.add_field(name="!removeautorole @cargo", value="Remove cargo automático", inline=False)
    embed.add_field(name="!listautoroles", value="Lista cargos configurados", inline=False)
    embed.add_field(name="!testautorole @usuário", value="Testa em um membro", inline=False)
    embed.add_field(name="!autorolehelp", value="Mostra esta mensagem", inline=False)
    
    await ctx.send(embed=embed)

@bot.command()
async def ping(ctx):
    await ctx.send(f'🏓 Pong! {round(bot.latency * 1000)}ms')

# ========== INICIAR BOT ==========
token = os.getenv('DISCORD_TOKEN')
if token:
    bot.run(token)
else:
    print("❌ ERROR: DISCORD_TOKEN não encontrado!")
    print("✅ Configure no Render: DISCORD_TOKEN=seu_token")
