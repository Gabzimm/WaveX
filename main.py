import discord
from discord.ext import commands
from flask import Flask
from threading import Thread
import os
import sys
import asyncio
from datetime import datetime

print("🚀 Iniciando bot de cargo automático...")
print(f"Python version: {sys.version}")

# ==================== CONFIGURAÇÃO ====================

# Configurar intents
intents = discord.Intents.default()
intents.members = True
intents.message_content = True
intents.guilds = True

# Criar bot
bot = commands.Bot(
    command_prefix='!',
    intents=intents,
    help_command=None
)

# ==================== SERVIDOR WEB PARA KEEP-ALIVE ====================
app = Flask('')

@app.route('/')
def home():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>🤖 Bot de Cargo Automático</title>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            body {
                font-family: 'Arial', sans-serif;
                text-align: center;
                padding: 20px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                min-height: 100vh;
                display: flex;
                align-items: center;
                justify-content: center;
            }
            .container {
                background: rgba(0,0,0,0.8);
                padding: 30px;
                border-radius: 15px;
                max-width: 600px;
                width: 90%;
                box-shadow: 0 10px 30px rgba(0,0,0,0.3);
            }
            .status {
                font-size: 24px;
                margin: 20px 0;
                padding: 15px;
                border-radius: 10px;
                background: #28a745;
                animation: pulse 2s infinite;
            }
            @keyframes pulse {
                0% { transform: scale(1); }
                50% { transform: scale(1.05); }
                100% { transform: scale(1); }
            }
            .info {
                background: rgba(255,255,255,0.1);
                padding: 15px;
                border-radius: 10px;
                margin: 15px 0;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🤖 Bot de Cargo Automático</h1>
            <div class="status">🟢 ONLINE 24/7</div>
            <div class="info">
                <p><strong>Função:</strong> Atribuir cargo <strong>𝗩𝗶𝘀𝗶𝘁𝗮𝗻𝘁𝗲</strong> automaticamente</p>
                <p><strong>Servidores:</strong> {}</p>
                <p><strong>Última verificação:</strong> {}</p>
            </div>
            <p>Este bot está hospedado no Render.com e monitorado por UptimeRobot</p>
            <p><small>ID: {}</small></p>
        </div>
    </body>
    </html>
    """.format(len(bot.guilds), 
               datetime.now().strftime('%d/%m/%Y %H:%M:%S'),
               bot.user.id if bot.user else 'Carregando...')

@app.route('/health')
def health():
    return {"status": "online", "timestamp": datetime.now().isoformat()}, 200

@app.route('/ping')
def ping():
    return "pong", 200

def run_web_server():
    app.run(host='0.0.0.0', port=8080)

def start_keep_alive():
    print("🌐 Iniciando servidor web na porta 8080...")
    t = Thread(target=run_web_server, daemon=True)
    t.start()
    print("✅ Servidor web pronto!")
    print("📡 URLs disponíveis:")
    print("   • Status: http://localhost:8080/")
    print("   • Health check: http://localhost:8080/health")
    print("   • Ping: http://localhost:8080/ping")

# ==================== EVENTOS DO BOT ====================

@bot.event
async def on_ready():
    """Quando o bot está pronto"""
    print("=" * 60)
    print(f"🤖 BOT CONECTADO COM SUCESSO!")
    print(f"🏷️ Nome: {bot.user}")
    print(f"🆔 ID: {bot.user.id}")
    print(f"📡 Ping: {round(bot.latency * 1000)}ms")
    print(f"🏠 Servidores: {len(bot.guilds)}")
    print("=" * 60)
    
    # Listar servidores
    if bot.guilds:
        print("📋 Servidores conectados:")
        for guild in bot.guilds:
            print(f"   • {guild.name} (ID: {guild.id}) - {guild.member_count} membros")
    else:
        print("⚠️ Bot não está em nenhum servidor ainda!")
        print("💡 Adicione o bot usando o link de convite")
    
    # Status personalizado
    await bot.change_presence(
        activity=discord.Activity(
            type=discord.ActivityType.watching,
            name=f"👥 {sum(g.member_count for g in bot.guilds)} membros"
        )
    )
    
    print("✅ Bot pronto para receber novos membros!")
    print("=" * 60)

@bot.event
async def on_member_join(member: discord.Member):
    """Atribui cargo automático quando alguém entra"""
    print(f"\n{'='*50}")
    print(f"👤 NOVO MEMBRO DETECTADO!")
    print(f"   Nome: {member.name}")
    print(f"   ID: {member.id}")
    print(f"   Servidor: {member.guild.name}")
    print(f"   Data: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    
    try:
        # Buscar cargo
        visitante_role = discord.utils.get(member.guild.roles, name="𝗩𝗶𝘀𝗶𝘁𝗮𝗻𝘁𝗲")
        
        if not visitante_role:
            print("   ⚠️ Cargo '𝗩𝗶𝘀𝗶𝘁𝗮𝗻𝘁𝗲' não encontrado. Tentando criar...")
            
            try:
                visitante_role = await member.guild.create_role(
                    name="𝗩𝗶𝘀𝗶𝘁𝗮𝗻𝘁𝗲",
                    color=discord.Color.light_grey(),
                    reason="Criado automaticamente pelo bot",
                    permissions=discord.Permissions.none()
                )
                print(f"   ✅ Cargo criado com sucesso!")
            except Exception as e:
                print(f"   ❌ Erro ao criar cargo: {e}")
                return
                
        # Verificar permissões
        bot_member = member.guild.me
        if not bot_member.guild_permissions.manage_roles:
            print("   ❌ Bot não tem permissão para gerenciar cargos!")
            return
        
        # Atribuir cargo
        await member.add_roles(visitante_role)
        print(f"   ✅ Cargo atribuído com sucesso!")
        print(f"   📊 Total de membros: {member.guild.member_count}")
        
        # Tentar enviar mensagem de boas-vindas
        try:
            canal_entrada = discord.utils.get(member.guild.text_channels, name="entrada")
            if not canal_entrada:
                canal_entrada = discord.utils.get(member.guild.text_channels, name="geral")
            
            if canal_entrada and canal_entrada.permissions_for(bot_member).send_messages:
                embed = discord.Embed(
                    title=f"👋 Bem-vindo(a), {member.name}!",
                    description=f"Seja bem-vindo(a) ao **{member.guild.name}**!\nVocê recebeu o cargo {visitante_role.mention}",
                    color=discord.Color.green()
                )
                await canal_entrada.send(embed=embed)
                print(f"   💬 Mensagem enviada em #{canal_entrada.name}")
        except:
            pass  # Ignorar erro se não conseguir enviar mensagem
            
    except Exception as e:
        print(f"   ❌ Erro: {type(e).__name__}: {e}")
    
    print(f"{'='*50}")

# ==================== COMANDOS SIMPLES ====================

@bot.command(name="ping")
async def ping_cmd(ctx):
    """Verifica se o bot está online"""
    latency = round(bot.latency * 1000)
    
    embed = discord.Embed(
        title="🏓 Pong!",
        description=f"Latência: **{latency}ms**",
        color=discord.Color.green()
    )
    embed.add_field(name="Servidores", value=len(bot.guilds), inline=True)
    embed.add_field(name="Membros totais", value=sum(g.member_count for g in bot.guilds), inline=True)
    embed.set_footer(text="Bot de Cargo Automático • Online 24/7")
    
    await ctx.send(embed=embed)

@bot.command(name="status")
async def status_cmd(ctx):
    """Status do bot"""
    embed = discord.Embed(
        title="🤖 Status do Bot",
        description="Bot de Cargo Automático 24/7",
        color=discord.Color.blue()
    )
    
    embed.add_field(name="Nome", value=bot.user.name, inline=True)
    embed.add_field(name="ID", value=bot.user.id, inline=True)
    embed.add_field(name="Ping", value=f"{round(bot.latency * 1000)}ms", inline=True)
    embed.add_field(name="Servidores", value=len(bot.guilds), inline=True)
    embed.add_field(name="Online desde", value=bot.user.created_at.strftime('%d/%m/%Y'), inline=True)
    
    # Permissões
    perms = ctx.guild.me.guild_permissions
    perms_text = "✅ Gerenciar Cargos" if perms.manage_roles else "❌ Gerenciar Cargos"
    embed.add_field(name="Permissões", value=perms_text, inline=False)
    
    embed.set_footer(text="Hospedado no Render.com • Monitorado por UptimeRobot")
    
    await ctx.send(embed=embed)

@bot.command(name="help")
async def help_cmd(ctx):
    """Ajuda"""
    embed = discord.Embed(
        title="📚 Ajuda - Bot de Cargo Automático",
        description="Este bot atribui automaticamente o cargo **'𝗩𝗶𝘀𝗶𝘁𝗮𝗻𝘁𝗲'** a novos membros.",
        color=discord.Color.purple()
    )
    
    embed.add_field(name="🎯 Funcionalidade", 
                   value="• Atribui cargo automaticamente\n• Cria cargo se não existir\n• Envia mensagem de boas-vindas", 
                   inline=False)
    
    embed.add_field(name="📋 Comandos", 
                   value="• `!ping` - Verifica latência\n• `!status` - Status do bot\n• `!help` - Esta mensagem", 
                   inline=False)
    
    embed.add_field(name="⚙️ Configuração", 
                   value="1. Adicione o bot ao servidor\n2. Garanta que ele tenha permissão para 'Gerenciar Cargos'\n3. O cargo do bot deve estar acima do cargo '𝗩𝗶𝘀𝗶𝘁𝗮𝗻𝘁𝗲'", 
                   inline=False)
    
    embed.set_footer(text="Online 24/7 • Sistema automático")
    
    await ctx.send(embed=embed)

# ==================== INICIALIZAÇÃO ====================

if __name__ == '__main__':
    print("=" * 60)
    print("🚀 INICIANDO BOT DE CARGO AUTOMÁTICO")
    print("=" * 60)
    
    # Verificar token
    TOKEN = os.getenv('DISCORD_TOKEN')
    
    if not TOKEN:
        print("❌ DISCORD_TOKEN não encontrado nas variáveis de ambiente!")
        print("💡 Configure no Render:")
        print("   1. Vá em Environment")
        print("   2. Adicione: DISCORD_TOKEN=seu_token_aqui")
        print("   3. Clique em Save Changes")
        print("💡 Ou adicione ao .env localmente:")
        print("   DISCORD_TOKEN=seu_token_aqui")
        
        # Para desenvolvimento local
        try:
            from dotenv import load_dotenv
            load_dotenv()
            TOKEN = os.getenv('DISCORD_TOKEN')
            if TOKEN:
                print("✅ Token encontrado no arquivo .env")
        except:
            pass
    
    if not TOKEN:
        print("❌ ERRO: Token não encontrado!")
        sys.exit(1)
    
    print("✅ Token encontrado")
    print("🖥️ Iniciando servidor web...")
    
    # Iniciar servidor web
    start_keep_alive()
    
    # Iniciar bot
    try:
        print("🔗 Conectando ao Discord...")
        bot.run(TOKEN)
    except discord.LoginFailure:
        print("❌ Token inválido!")
        print("💡 Verifique se o token está correto")
    except Exception as e:
        print(f"❌ Erro: {type(e).__name__}: {e}")
