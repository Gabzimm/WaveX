"""
🤖 BOT DE CARGO AUTOMÁTICO 24/7
Funcionalidade: Atribui cargo "𝗩𝗶𝘀𝗶𝘁𝗮𝗻𝘁𝗲" automaticamente a novos membros
"""

import os
import sys
from threading import Thread
from datetime import datetime

# ========== CONFIGURAÇÃO DO BOT ==========
print("=" * 50)
print("🚀 INICIANDO BOT DE CARGO AUTOMÁTICO")
print("=" * 50)

# Tentar importar discord.py
try:
    import discord
    from discord.ext import commands
    print("✅ discord.py importado com sucesso")
except ImportError:
    print("❌ discord.py não encontrado!")
    print("💡 Instale com: pip install discord.py==2.3.2")
    sys.exit(1)

# Configurar intents (PERMISSÕES NECESSÁRIAS)
intents = discord.Intents.default()
intents.members = True  # IMPORTANTE: Para detectar quando membros entram
intents.guilds = True   # Para ver servidores

# Criar bot (SIMPLES)
bot = commands.Bot(
    command_prefix='!',
    intents=intents,
    help_command=None  # Remover ajuda padrão
)

# ========== SERVIDOR WEB PARA UPTIMEROBOT ==========
try:
    from flask import Flask
    
    # Criar aplicação Flask
    app = Flask(__name__)
    
    @app.route('/')
    def home():
        """Página inicial para verificar se está online"""
        status = "🟢 ONLINE" if bot.is_ready() else "🟡 CONECTANDO"
        servidores = len(bot.guilds) if hasattr(bot, 'guilds') else 0
        
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>🤖 Bot de Cargo Automático</title>
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    text-align: center;
                    padding: 20px;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    min-height: 100vh;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                }}
                .container {{
                    background: rgba(0, 0, 0, 0.8);
                    padding: 30px;
                    border-radius: 15px;
                    max-width: 600px;
                    width: 90%;
                }}
                .status {{
                    font-size: 24px;
                    font-weight: bold;
                    padding: 15px;
                    border-radius: 10px;
                    margin: 20px 0;
                    background: #28a745;
                }}
                .info {{
                    background: rgba(255, 255, 255, 0.1);
                    padding: 15px;
                    border-radius: 10px;
                    margin: 15px 0;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>🤖 Bot de Cargo Automático</h1>
                <div class="status">{status}</div>
                <div class="info">
                    <p><strong>Função:</strong> Atribuir cargo <strong>𝗩𝗶𝘀𝗶𝘁𝗮𝗻𝘁𝗲</strong> automaticamente</p>
                    <p><strong>Servidores:</strong> {servidores}</p>
                    <p><strong>Última atualização:</strong> {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}</p>
                </div>
                <p>Este bot está online 24/7 e monitorado por UptimeRobot</p>
            </div>
        </body>
        </html>
        """
    
    @app.route('/health')
    def health():
        """Endpoint para UptimeRobot verificar se está online"""
        return "OK", 200
    
    @app.route('/ping')
    def ping():
        """Endpoint simples de ping"""
        return "pong", 200
    
    def run_web_server():
        """Executar servidor web em uma thread separada"""
        print("🌐 Iniciando servidor web na porta 8080...")
        app.run(host='0.0.0.0', port=8080, debug=False, threaded=True)
    
    # Iniciar servidor web em background
    web_thread = Thread(target=run_web_server, daemon=True)
    web_thread.start()
    print("✅ Servidor web iniciado!")
    
except ImportError:
    print("⚠️ Flask não encontrado. Servidor web não será iniciado.")
    print("💡 Instale com: pip install flask==2.3.3")

# ========== EVENTOS DO BOT ==========

@bot.event
async def on_ready():
    """Quando o bot conecta ao Discord"""
    print("=" * 50)
    print(f"✅ BOT CONECTADO: {bot.user.name}")
    print(f"🆔 ID: {bot.user.id}")
    print(f"📡 Ping: {round(bot.latency * 1000)}ms")
    print(f"🏠 Servidores conectados: {len(bot.guilds)}")
    print("=" * 50)
    
    # Listar servidores
    if bot.guilds:
        print("📋 Lista de servidores:")
        for guild in bot.guilds:
            print(f"   • {guild.name} - {guild.member_count} membros")
    else:
        print("⚠️ O bot ainda não foi adicionado a nenhum servidor!")
        print("💡 Use o link de convite para adicioná-lo")
    
    # Status do bot
    await bot.change_presence(
        activity=discord.Activity(
            type=discord.ActivityType.watching,
            name=f"👥 {sum(g.member_count for g in bot.guilds)} membros"
        )
    )
    
    print("🎯 Pronto para atribuir cargos automaticamente!")

@bot.event
async def on_member_join(member):
    """
    ATRIBUI CARGO AUTOMATICAMENTE QUANDO ALGUÉM ENTRA
    Esta é a função principal do bot
    """
    print(f"\n{'='*50}")
    print(f"👤 NOVO MEMBRO DETECTADO!")
    print(f"   Nome: {member.name}")
    print(f"   ID: {member.id}")
    print(f"   Servidor: {member.guild.name}")
    print(f"   Horário: {datetime.now().strftime('%H:%M:%S')}")
    
    try:
        # 1. BUSCAR CARGO "𝗩𝗶𝘀𝗶𝘁𝗮𝗻𝘁𝗲"
        cargo_nome = "𝗩𝗶𝘀𝗶𝘁𝗮𝗻𝘁𝗲"
        cargo = discord.utils.get(member.guild.roles, name=cargo_nome)
        
        # 2. SE NÃO EXISTIR, CRIAR AUTOMATICAMENTE
        if not cargo:
            print(f"   ⚠️ Cargo '{cargo_nome}' não encontrado. Criando...")
            
            try:
                cargo = await member.guild.create_role(
                    name=cargo_nome,
                    color=discord.Color.light_grey(),  # Cor cinza clara
                    reason="Criado automaticamente pelo bot de cargo automático",
                    permissions=discord.Permissions.none()  # Sem permissões especiais
                )
                print(f"   ✅ Cargo '{cargo_nome}' criado com sucesso!")
                
                # Mover cargo para posição correta (acima do @everyone)
                everyone_role = member.guild.default_role
                await cargo.edit(position=everyone_role.position + 1)
                
            except discord.Forbidden:
                print("   ❌ ERRO: Bot não tem permissão para criar cargos!")
                print("   💡 Dê ao bot a permissão 'Gerenciar Cargos'")
                return
            except Exception as e:
                print(f"   ❌ ERRO ao criar cargo: {e}")
                return
        
        # 3. VERIFICAR SE BOT TEM PERMISSÃO
        bot_member = member.guild.me
        if not bot_member.guild_permissions.manage_roles:
            print("   ❌ ERRO: Bot não tem permissão para gerenciar cargos!")
            print("   💡 Configure a permissão 'Gerenciar Cargos' para o bot")
            return
        
        # 4. VERIFICAR SE CARGO DO BOT ESTÁ ACIMA DO CARGO VISITANTE
        if cargo.position >= bot_member.top_role.position:
            print(f"   ⚠️ AVISO: Cargo do bot está abaixo do cargo '{cargo_nome}'")
            print("   💡 Arraste o cargo do bot para CIMA na lista de cargos")
        
        # 5. ATRIBUIR CARGO AO MEMBRO
        await member.add_roles(cargo)
        print(f"   ✅ Cargo '{cargo_nome}' atribuído a {member.name}!")
        print(f"   📊 Total de membros no servidor: {member.guild.member_count}")
        
        # 6. TENTAR ENVIAR MENSAGEM DE BOAS-VINDAS (OPCIONAL)
        try:
            # Procurar canal de entrada
            canais_tentativa = ["🚪entrada", "entrada", "boas-vindas", "geral", "chat"]
            canal_encontrado = None
            
            for nome_canal in canais_tentativa:
                canal = discord.utils.get(member.guild.text_channels, name=nome_canal)
                if canal and canal.permissions_for(bot_member).send_messages:
                    canal_encontrado = canal
                    break
            
            if canal_encontrado:
                embed = discord.Embed(
                    title=f"👋 Bem-vindo(a), {member.name}!",
                    description=f"Seja bem-vindo(a) ao **{member.guild.name}**! 🎉",
                    color=discord.Color.green()
                )
                embed.add_field(name="Seu cargo", value=f"{cargo.mention}", inline=True)
                embed.add_field(name="Membros totais", value=f"{member.guild.member_count}", inline=True)
                embed.set_footer(text="Sistema automático de cargos")
                
                await canal_encontrado.send(embed=embed)
                print(f"   💬 Mensagem de boas-vindas enviada em #{canal_encontrado.name}")
                
        except Exception as e:
            print(f"   ⚠️ Não foi possível enviar mensagem de boas-vindas: {e}")
        
    except Exception as e:
        print(f"   ❌ ERRO INESPERADO: {type(e).__name__}: {e}")
    
    print(f"{'='*50}")

# ========== COMANDOS DO BOT ==========

@bot.command(name="ping")
async def comando_ping(ctx):
    """Verifica se o bot está online"""
    latency = round(bot.latency * 1000)
    
    embed = discord.Embed(
        title="🏓 Pong!",
        description=f"Estou online e funcionando! 🎯",
        color=discord.Color.green()
    )
    embed.add_field(name="Latência", value=f"{latency}ms", inline=True)
    embed.add_field(name="Servidores", value=f"{len(bot.guilds)}", inline=True)
    embed.set_footer(text="Bot de Cargo Automático • Online 24/7")
    
    await ctx.send(embed=embed)

@bot.command(name="status")
async def comando_status(ctx):
    """Mostra status completo do bot"""
    
    # Verificar permissões do bot neste servidor
    perms = ctx.guild.me.guild_permissions
    
    embed = discord.Embed(
        title="🤖 Status do Bot",
        description="Informações do sistema de cargo automático",
        color=discord.Color.blue()
    )
    
    # Informações básicas
    embed.add_field(name="Nome", value=bot.user.name, inline=True)
    embed.add_field(name="ID", value=bot.user.id, inline=True)
    embed.add_field(name="Ping", value=f"{round(bot.latency * 1000)}ms", inline=True)
    embed.add_field(name="Servidores", value=len(bot.guilds), inline=True)
    embed.add_field(name="Online desde", value=bot.user.created_at.strftime('%d/%m/%Y'), inline=True)
    
    # Permissões (VERIFICAR ISSO É IMPORTANTE!)
    tem_permissao = "✅ SIM" if perms.manage_roles else "❌ NÃO"
    embed.add_field(name="Pode gerenciar cargos?", value=tem_permissao, inline=True)
    
    # Cargo do bot
    cargo_bot = ctx.guild.me.top_role
    embed.add_field(
        name="Cargo do bot",
        value=f"{cargo_bot.name} (posição: {cargo_bot.position})",
        inline=False
    )
    
    # Cargo visitante
    cargo_visitante = discord.utils.get(ctx.guild.roles, name="𝗩𝗶𝘀𝗶𝘁𝗮𝗻𝘁𝗲")
    if cargo_visitante:
        embed.add_field(
            name="Cargo visitante",
            value=f"{cargo_visitante.mention} (posição: {cargo_visitante.position})",
            inline=False
        )
    else:
        embed.add_field(
            name="Cargo visitante",
            value="❌ Não encontrado (será criado automaticamente)",
            inline=False
        )
    
    embed.set_footer(text="Use !ping para testar • Hospedado 24/7")
    
    await ctx.send(embed=embed)

@bot.command(name="ajuda")
async def comando_ajuda(ctx):
    """Mostra ajuda sobre o bot"""
    
    embed = discord.Embed(
        title="📚 Ajuda - Bot de Cargo Automático",
        description="Este bot atribui **automaticamente** o cargo **'𝗩𝗶𝘀𝗶𝘁𝗮𝗻𝘁𝗲'** quando alguém entra no servidor.",
        color=discord.Color.purple()
    )
    
    embed.add_field(
        name="🎯 Funcionalidade principal",
        value="• Atribui cargo '𝗩𝗶𝘀𝗶𝘁𝗮𝗻𝘁𝗲' automaticamente\n• Cria o cargo se não existir\n• Funciona 24 horas por dia, 7 dias por semana",
        inline=False
    )
    
    embed.add_field(
        name="📋 Comandos disponíveis",
        value="• `!ping` - Testa se o bot está online\n• `!status` - Mostra status completo\n• `!ajuda` - Esta mensagem",
        inline=False
    )
    
    embed.add_field(
        name="⚙️ Configuração necessária",
        value="1. O bot precisa da permissão **'Gerenciar Cargos'**\n2. O cargo do bot deve estar **ACIMA** do cargo '𝗩𝗶𝘀𝗶𝘁𝗮𝗻𝘁𝗲'\n3. Ative a intent **'SERVER MEMBERS INTENT'** no Discord Dev Portal",
        inline=False
    )
    
    embed.add_field(
        name="🔧 Como testar",
        value="Saia e entre novamente no servidor, ou use outra conta para testar.",
        inline=False
    )
    
    embed.set_footer(text="Bot Online 24/7 • Monitorado por UptimeRobot")
    
    await ctx.send(embed=embed)

@bot.command(name="testar")
@commands.has_permissions(administrator=True)
async def comando_testar(ctx, usuario: discord.Member = None):
    """Testa o sistema de cargos (apenas administradores)"""
    
    if not usuario:
        usuario = ctx.author
    
    await ctx.send(f"🔧 Testando sistema para {usuario.mention}...")
    
    # Simular entrada do membro
    await on_member_join(usuario)
    
    await ctx.send(f"✅ Teste concluído para {usuario.mention}!")

# ========== INICIAR BOT ==========

if __name__ == "__main__":
    # OBTER TOKEN DO BOT
    TOKEN = os.getenv("DISCORD_TOKEN")
    
    # Se não encontrar nas variáveis de ambiente, tentar arquivo .env
    if not TOKEN:
        try:
            # Tentar carregar de um arquivo .env
            with open(".env", "r") as f:
                for line in f:
                    if line.startswith("DISCORD_TOKEN="):
                        TOKEN = line.split("=")[1].strip()
                        break
        except:
            pass
    
    # Se ainda não encontrou, pedir para configurar
    if not TOKEN:
        print("❌ ERRO: DISCORD_TOKEN não encontrado!")
        print("\n💡 COMO CONFIGURAR:")
        print("1. No Render/UptimeRobot, adicione a variável de ambiente:")
        print("   Nome: DISCORD_TOKEN")
        print("   Valor: seu_token_do_bot_aqui")
        print("\n2. Ou localmente, crie um arquivo .env com:")
        print("   DISCORD_TOKEN=seu_token_do_bot_aqui")
        print("\n🔗 Obtenha seu token em: https://discord.com/developers/applications")
        sys.exit(1)
    
    print("✅ Token encontrado")
    print("🔗 Conectando ao Discord...")
    print("=" * 50)
    
    try:
        # INICIAR BOT
        bot.run(TOKEN)
        
    except discord.LoginFailure:
        print("❌ ERRO: Token inválido ou expirado!")
        print("💡 Gere um novo token no Discord Developer Portal")
        
    except KeyboardInterrupt:
        print("\n👋 Bot encerrado manualmente")
        
    except Exception as e:
        print(f"❌ ERRO INESPERADO: {type(e).__name__}: {e}")
