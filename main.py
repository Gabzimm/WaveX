import os
import sys
import asyncio
from datetime import datetime
from threading import Thread

print("=" * 60)
print("🚀 INICIANDO BOT DE CARGO AUTOMÁTICO")
print(f"Python: {sys.version}")
print("=" * 60)

# ==================== CONFIGURAÇÃO DO BOT ====================

# IMPORTANTE: Importar discord.py de forma segura
try:
    # Tentar importar sem funcionalidades de voz
    import discord
    
    # Forçar desabilitar voz para evitar audioop
    discord.voice_client = None
    discord.VoiceClient = None
    
    from discord.ext import commands
    
    print("✅ discord.py importado com sucesso")
    
except ImportError as e:
    print(f"❌ Erro ao importar discord.py: {e}")
    print("💡 Instale com: pip install discord.py==2.2.3")
    sys.exit(1)

except Exception as e:
    print(f"⚠️ Aviso: {e}")
    # Continuar mesmo com avisos

# Configurar intents (sem voz)
intents = discord.Intents.default()
intents.members = True      # Para on_member_join
intents.guilds = True       # Para ver servidores

# Criar bot com funcionalidades limitadas
class SimpleBot(commands.Bot):
    async def setup_hook(self):
        # Desabilitar funcionalidades de voz
        self._connection._voice_clients = {}
        print("🔇 Funcionalidades de voz desabilitadas")

bot = SimpleBot(
    command_prefix='!',
    intents=intents,
    help_command=None
)

# ==================== SERVIDOR WEB ====================

try:
    from flask import Flask
    app = Flask(__name__)
    
    @app.route('/')
    def home():
        return f"""
        <!DOCTYPE html>
        <html>
        <head><title>🤖 Bot Online</title>
        <style>
            body {{font-family: Arial; text-align: center; padding: 50px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white;}}
            .container {{background: rgba(0,0,0,0.7); padding: 30px; border-radius: 15px;
            max-width: 600px; margin: 0 auto;}}
            .status {{background: #28a745; padding: 15px; border-radius: 10px; margin: 20px 0;}}
        </style>
        </head>
        <body>
            <div class="container">
                <h1>🤖 Bot de Cargo Automático</h1>
                <div class="status">🟢 ONLINE</div>
                <p>Atribui cargo <strong>𝗩𝗶𝘀𝗶𝘁𝗮𝗻𝘁𝗲</strong> automaticamente</p>
                <p><strong>Servidores:</strong> {len(bot.guilds) if hasattr(bot, 'guilds') else 0}</p>
                <p><strong>Última verificação:</strong> {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}</p>
            </div>
        </body>
        </html>
        """
    
    @app.route('/health')
    def health():
        return {"status": "online", "timestamp": datetime.now().isoformat()}, 200
    
    @app.route('/ping')
    def ping():
        return "pong", 200
    
    def run_flask():
        app.run(host='0.0.0.0', port=8080, debug=False, threaded=True)
    
    print("✅ Flask importado com sucesso")
    
except ImportError:
    print("⚠️ Flask não instalado, continuando sem servidor web...")
    
    # Criar um servidor web simples como fallback
    from http.server import HTTPServer, BaseHTTPRequestHandler
    
    class SimpleHandler(BaseHTTPRequestHandler):
        def do_GET(self):
            if self.path == '/health':
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(b'{"status":"online"}')
            else:
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                html = f"""
                <html><body>
                <h1>🤖 Bot Online</h1>
                <p>Status: Online</p>
                <p>Time: {datetime.now()}</p>
                </body></html>
                """
                self.wfile.write(html.encode())
    
    def run_simple_server():
        server = HTTPServer(('0.0.0.0', 8080), SimpleHandler)
        server.serve_forever()
    
    run_flask = run_simple_server

# Iniciar servidor web em thread separada
def start_web_server():
    print("🌐 Iniciando servidor web na porta 8080...")
    try:
        web_thread = Thread(target=run_flask, daemon=True)
        web_thread.start()
        print("✅ Servidor web iniciado!")
    except Exception as e:
        print(f"⚠️ Erro ao iniciar servidor web: {e}")

# ==================== EVENTOS DO BOT ====================

@bot.event
async def on_ready():
    print("=" * 60)
    print(f"✅ BOT CONECTADO: {bot.user}")
    print(f"🆔 ID: {bot.user.id}")
    print(f"📡 Ping: {round(bot.latency * 1000)}ms")
    print(f"🏠 Servidores: {len(bot.guilds)}")
    
    if bot.guilds:
        print("📋 Servidores conectados:")
        for guild in bot.guilds:
            print(f"   • {guild.name} ({guild.member_count} membros)")
    
    # Status simples
    await bot.change_presence(
        activity=discord.Activity(
            type=discord.ActivityType.watching,
            name=f"👥 {sum(g.member_count for g in bot.guilds)} membros"
        )
    )
    
    print("🎯 Bot pronto para atribuir cargos automaticamente!")
    print("=" * 60)

@bot.event
async def on_member_join(member):
    """Atribui cargo automaticamente"""
    print(f"\n{'='*50}")
    print(f"👤 NOVO MEMBRO: {member.name}")
    print(f"🏠 Servidor: {member.guild.name}")
    
    try:
        # Buscar cargo
        cargo_nome = "𝗩𝗶𝘀𝗶𝘁𝗮𝗻𝘁𝗲"
        visitante = discord.utils.get(member.guild.roles, name=cargo_nome)
        
        # Criar cargo se não existir
        if not visitante:
            try:
                visitante = await member.guild.create_role(
                    name=cargo_nome,
                    color=discord.Color.light_grey(),
                    reason="Criado automaticamente"
                )
                print(f"✅ Cargo '{cargo_nome}' criado")
            except Exception as e:
                print(f"❌ Não foi possível criar cargo: {e}")
                return
        
        # Verificar permissões
        if not member.guild.me.guild_permissions.manage_roles:
            print("❌ Bot não tem permissão para gerenciar cargos")
            return
        
        # Atribuir cargo
        await member.add_roles(visitante)
        print(f"✅ Cargo atribuído a {member.name}")
        
        # Log
        print(f"📊 Total de membros: {member.guild.member_count}")
        
    except Exception as e:
        print(f"❌ Erro: {type(e).__name__}: {e}")
    
    print(f"{'='*50}")

# ==================== COMANDOS SIMPLES ====================

@bot.command()
async def ping(ctx):
    """Testa se o bot está online"""
    latency = round(bot.latency * 1000)
    await ctx.send(f"🏓 Pong! {latency}ms | Servidores: {len(bot.guilds)}")

@bot.command()
async def status(ctx):
    """Status do bot"""
    import platform
    
    embed = discord.Embed(
        title="🤖 Status do Bot",
        color=discord.Color.blue()
    )
    
    embed.add_field(name="Nome", value=bot.user.name, inline=True)
    embed.add_field(name="Ping", value=f"{round(bot.latency * 1000)}ms", inline=True)
    embed.add_field(name="Servidores", value=len(bot.guilds), inline=True)
    
    # Memória (aproximada)
    import psutil
    memory = psutil.virtual_memory()
    embed.add_field(name="Memória", value=f"{memory.percent}% usado", inline=True)
    
    # Sistema
    embed.add_field(name="Python", value=platform.python_version(), inline=True)
    embed.add_field(name="Sistema", value=platform.system(), inline=True)
    
    embed.set_footer(text="Bot de Cargo Automático • Online 24/7")
    
    await ctx.send(embed=embed)

@bot.command()
@commands.has_permissions(administrator=True)
async def test(ctx, user: discord.Member = None):
    """Testa o sistema de cargos (apenas ADM)"""
    if not user:
        user = ctx.author
    
    await ctx.send(f"🔧 Testando sistema para {user.mention}...")
    
    # Simular entrada
    await on_member_join(user)
    
    await ctx.send(f"✅ Teste concluído para {user.mention}!")

# ==================== INICIALIZAÇÃO ====================

if __name__ == '__main__':
    # Verificar token
    TOKEN = os.getenv('DISCORD_TOKEN')
    
    if not TOKEN:
        print("❌ DISCORD_TOKEN não encontrado!")
        print("💡 Configure no Render:")
        print("   Environment → Add Environment Variable")
        print("   Name: DISCORD_TOKEN")
        print("   Value: seu_token_aqui")
        
        # Tentar arquivo .env local
        try:
            from dotenv import load_dotenv
            load_dotenv()
            TOKEN = os.getenv('DISCORD_TOKEN')
            if TOKEN:
                print("✅ Token encontrado no .env")
        except:
            pass
    
    if not TOKEN:
        print("❌ ERRO: Token não configurado!")
        sys.exit(1)
    
    # Iniciar servidor web
    start_web_server()
    
    # Iniciar bot
    try:
        print("🔗 Conectando ao Discord...")
        bot.run(TOKEN)
    except discord.LoginFailure:
        print("❌ Token inválido!")
    except KeyboardInterrupt:
        print("\n👋 Bot encerrado")
    except Exception as e:
        print(f"❌ Erro: {type(e).__name__}: {e}")
