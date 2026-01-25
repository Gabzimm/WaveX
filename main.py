import discord
from discord.ext import commands
from flask import Flask
from threading import Thread
import os
import sys
import asyncio
from datetime import datetime

# ==================== CONFIGURAÇÃO ====================

# Configurar intents para eventos de membros
intents = discord.Intents.default()
intents.members = True  # CRÍTICO para on_member_join
intents.message_content = True
intents.guilds = True

# Criar bot
bot = commands.Bot(
    command_prefix='!',
    intents=intents,
    help_command=None  # Remover comando de ajuda padrão
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
        <style>
            body {
                font-family: Arial, sans-serif;
                text-align: center;
                padding: 50px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
            }
            .container {
                background: rgba(0,0,0,0.7);
                padding: 30px;
                border-radius: 15px;
                max-width: 600px;
                margin: 0 auto;
            }
            .status {
                font-size: 24px;
                margin: 20px 0;
                padding: 10px;
                border-radius: 10px;
                background: #28a745;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🤖 Bot de Cargo Automático</h1>
            <div class="status">🟢 ONLINE 24/7</div>
            <p>Sistema automático para atribuir cargo <strong>𝗩𝗶𝘀𝗶𝘁𝗮𝗻𝘁𝗲</strong> aos novos membros</p>
            <p><strong>Servidores:</strong> {}</p>
            <p><strong>Último check:</strong> {}</p>
        </div>
    </body>
    </html>
    """.format(len(bot.guilds), datetime.now().strftime('%d/%m/%Y %H:%M:%S'))

@app.route('/health')
def health():
    return {"status": "online", "timestamp": datetime.now().isoformat()}, 200

@app.route('/status')
def status():
    return {
        "status": "online",
        "servers": len(bot.guilds),
        "bot_name": bot.user.name if bot.user else "Carregando...",
        "uptime": datetime.now().isoformat()
    }

def run_web_server():
    app.run(host='0.0.0.0', port=8080)

def start_keep_alive():
    """Inicia servidor web para keep-alive"""
    print("🌐 Iniciando servidor web na porta 8080...")
    t = Thread(target=run_web_server, daemon=True)
    t.start()
    print("✅ Servidor web iniciado!")
    print("📡 Acesse: http://localhost:8080")
    print("🔧 Health check: http://localhost:8080/health")

# ==================== EVENTOS DO BOT ====================

@bot.event
async def on_ready():
    """Quando o bot está pronto"""
    print("=" * 50)
    print(f"🤖 Bot conectado como: {bot.user}")
    print(f"🆔 ID: {bot.user.id}")
    print(f"📡 Ping: {round(bot.latency * 1000)}ms")
    print(f"🏠 Servidores conectados: {len(bot.guilds)}")
    print("=" * 50)
    
    # Definir status do bot
    await bot.change_presence(
        activity=discord.Activity(
            type=discord.ActivityType.watching,
            name=f"{len(bot.guilds)} servidor(es) | Cargo automático"
        )
    )
    
    # Listar servidores
    for guild in bot.guilds:
        print(f"• {guild.name} (ID: {guild.id}) - Membros: {guild.member_count}")

@bot.event
async def on_member_join(member: discord.Member):
    """Atribui cargo automático quando alguém entra"""
    print(f"\n{'='*40}")
    print(f"👤 NOVO MEMBRO: {member.name} entrou em {member.guild.name}")
    print(f"🆔 ID do usuário: {member.id}")
    print(f"📅 Data: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    
    try:
        # 1. Buscar cargo "𝗩𝗶𝘀𝗶𝘁𝗮𝗻𝘁𝗲" (COM FONTE ESPECIAL)
        visitante_role = discord.utils.get(member.guild.roles, name="𝗩𝗶𝘀𝗶𝘁𝗮𝗻𝘁𝗲")
        
        if not visitante_role:
            print("⚠️ Cargo '𝗩𝗶𝘀𝗶𝘁𝗮𝗻𝘁𝗲' não encontrado! Tentando criar...")
            
            try:
                # Tentar criar o cargo automaticamente
                visitante_role = await member.guild.create_role(
                    name="𝗩𝗶𝘀𝗶𝘁𝗮𝗻𝘁𝗲",
                    color=discord.Color.light_grey(),
                    reason="Criado automaticamente pelo bot de cargo automático",
                    permissions=discord.Permissions.none()
                )
                
                # Mover cargo para baixo (acima do @everyone)
                everyone_role = member.guild.default_role
                await visitante_role.edit(position=everyone_role.position + 1)
                
                print(f"✅ Cargo '𝗩𝗶𝘀𝗶𝘁𝗮𝗻𝘁𝗲' criado automaticamente!")
                
            except discord.Forbidden:
                print("❌ ERRO: Sem permissão para criar cargo!")
                print("💡 Dê ao bot permissão de 'Gerenciar Cargos'")
                return
            except Exception as e:
                print(f"❌ ERRO ao criar cargo: {type(e).__name__}: {e}")
                return
                
        # 2. Verificar se o cargo do bot está acima do cargo visitante
        bot_member = member.guild.me
        if visitante_role.position >= bot_member.top_role.position:
            print(f"⚠️ AVISO: Cargo do bot ({bot_member.top_role.name}) está abaixo do cargo '𝗩𝗶𝘀𝗶𝘁𝗮𝗻𝘁𝗲'")
            print("💡 Arraste o cargo do bot para cima na lista de cargos")
        
        # 3. Dar o cargo ao membro
        await member.add_roles(visitante_role)
        print(f"✅ Cargo '𝗩𝗶𝘀𝗶𝘁𝗮𝗻𝘁𝗲' atribuído a {member.name}")
        
        # 4. Log detalhado
        print(f"📊 Detalhes:")
        print(f"   • Usuário: {member.name} (ID: {member.id})")
        print(f"   • Servidor: {member.guild.name} (ID: {member.guild.id})")
        print(f"   • Cargo atribuído: {visitante_role.name} (ID: {visitante_role.id})")
        print(f"   • Total de membros agora: {member.guild.member_count}")
        
        # 5. Enviar mensagem de boas-vindas (opcional)
        try:
            # Tentar encontrar canal de boas-vindas
            welcome_channels = ["🚪entrada", "entrada", "bem-vindo", "geral", "chat"]
            
            for channel_name in welcome_channels:
                channel = discord.utils.get(member.guild.text_channels, name=channel_name)
                if channel and channel.permissions_for(bot_member).send_messages:
                    embed = discord.Embed(
                        title=f"👋 Bem-vindo(a), {member.name}!",
                        description=(
                            f"Seja muito bem-vindo(a) ao **{member.guild.name}**!\n\n"
                            f"📋 **Seu cargo:** {visitante_role.mention}\n"
                            f"👤 **Membros totais:** {member.guild.member_count}\n\n"
                            f"💡 **Próximo passo:**\n"
                            f"Peça seu set personalizado para a staff!"
                        ),
                        color=discord.Color.green()
                    )
                    embed.set_thumbnail(url=member.avatar.url if member.avatar else member.default_avatar.url)
                    embed.set_footer(text=f"ID: {member.id} • {datetime.now().strftime('%d/%m/%Y %H:%M')}")
                    
                    await channel.send(embed=embed)
                    print(f"✅ Mensagem de boas-vindas enviada em #{channel.name}")
                    break
                    
        except Exception as e:
            print(f"⚠️ Não foi possível enviar mensagem de boas-vindas: {e}")
        
        print(f"{'='*40}")
        
    except discord.Forbidden as e:
        print(f"❌ ERRO DE PERMISSÃO: {e}")
        print("💡 Verifique se o bot tem permissão para:")
        print("   • Gerenciar Cargos")
        print("   • O cargo do bot está acima do cargo '𝗩𝗶𝘀𝗶𝘁𝗮𝗻𝘁𝗲'")
        
    except Exception as e:
        print(f"❌ ERRO INESPERADO: {type(e).__name__}: {e}")

# ==================== COMANDOS SIMPLES ====================

@bot.command(name="ping")
async def ping(ctx):
    """Verifica se o bot está online"""
    latency = round(bot.latency * 1000)
    
    embed = discord.Embed(
        title="🏓 Pong!",
        description=f"**Latência:** {latency}ms\n**Servidores:** {len(bot.guilds)}",
        color=discord.Color.green()
    )
    embed.add_field(name="👤 Usuário", value=ctx.author.mention, inline=True)
    embed.add_field(name="🏠 Servidor", value=ctx.guild.name, inline=True)
    embed.set_footer(text=f"Bot de Cargo Automático • Online 24/7")
    
    await ctx.send(embed=embed)

@bot.command(name="status")
async def status_cmd(ctx):
    """Mostra status completo do bot"""
    
    # Verificar permissões do bot no servidor
    perms = ctx.guild.me.guild_permissions
    
    embed = discord.Embed(
        title="🤖 Status do Bot",
        description=f"Bot de Cargo Automático - Online 24/7",
        color=discord.Color.blue()
    )
    
    embed.add_field(name="🏷️ Nome", value=bot.user.name, inline=True)
    embed.add_field(name="🆔 ID", value=bot.user.id, inline=True)
    embed.add_field(name="📡 Ping", value=f"{round(bot.latency * 1000)}ms", inline=True)
    embed.add_field(name="🏠 Servidores", value=len(bot.guilds), inline=True)
    embed.add_field(name="📅 Online desde", value=bot.user.created_at.strftime('%d/%m/%Y'), inline=True)
    
    # Permissões
    perms_status = []
    perms_status.append(f"✅ Gerenciar Cargos" if perms.manage_roles else "❌ Gerenciar Cargos")
    perms_status.append(f"✅ Enviar Mensagens" if perms.send_messages else "❌ Enviar Mensagens")
    perms_status.append(f"✅ Ver Canais" if perms.view_channel else "❌ Ver Canais")
    
    embed.add_field(name="🔐 Permissões", value="\n".join(perms_status), inline=False)
    
    # Cargo do bot
    bot_role = ctx.guild.me.top_role
    embed.add_field(
        name="📊 Cargo do Bot",
        value=f"**Nome:** {bot_role.name}\n**Posição:** {bot_role.position}/{len(ctx.guild.roles)}",
        inline=False
    )
    
    embed.set_footer(text="Sistema automático de cargos • Hospedado 24/7")
    
    await ctx.send(embed=embed)

@bot.command(name="check_cargo")
@commands.has_permissions(administrator=True)
async def check_cargo(ctx):
    """Verifica configuração do sistema de cargos (apenas ADM)"""
    
    # Buscar cargo
    visitante_role = discord.utils.get(ctx.guild.roles, name="𝗩𝗶𝘀𝗶𝘁𝗮𝗻𝘁𝗲")
    bot_member = ctx.guild.me
    
    embed = discord.Embed(
        title="🔍 Verificação do Sistema de Cargos",
        description="Status do sistema automático de cargos",
        color=discord.Color.blue()
    )
    
    # Status do cargo
    if visitante_role:
        embed.add_field(
            name="✅ Cargo '𝗩𝗶𝘀𝗶𝘁𝗮𝗻𝘁𝗲'",
            value=f"**Encontrado!**\nID: `{visitante_role.id}`\nPosição: {visitante_role.position}",
            inline=True
        )
    else:
        embed.add_field(
            name="❌ Cargo '𝗩𝗶𝘀𝗶𝘁𝗮𝗻𝘁𝗲'",
            value="**Não encontrado!**\nSerá criado automaticamente quando necessário.",
            inline=True
        )
    
    # Permissões do bot
    has_manage_roles = bot_member.guild_permissions.manage_roles
    embed.add_field(
        name="🔐 Permissões",
        value=f"Gerenciar Cargos: {'✅' if has_manage_roles else '❌'}",
        inline=True
    )
    
    # Posição do cargo
    if visitante_role:
        position_status = "✅" if bot_member.top_role.position > visitante_role.position else "❌"
        embed.add_field(
            name="📊 Posição do Cargo",
            value=f"Bot acima do cargo: {position_status}",
            inline=True
        )
    
    # Testar com usuário atual
    if visitante_role and visitante_role in ctx.author.roles:
        embed.add_field(
            name="🧪 Teste com você",
            value=f"✅ Você TEM o cargo {visitante_role.mention}",
            inline=False
        )
    elif visitante_role:
        embed.add_field(
            name="🧪 Teste com você",
            value=f"❌ Você NÃO TEM o cargo {visitante_role.mention}",
            inline=False
        )
    
    embed.set_footer(text="Use !status para mais informações")
    
    await ctx.send(embed=embed)

@bot.command(name="simular_entrada")
@commands.has_permissions(administrator=True)
async def simular_entrada(ctx, membro: discord.Member = None):
    """Simula a entrada de um membro (apenas ADM)"""
    if not membro:
        membro = ctx.author
    
    await ctx.send(f"🔧 Simulando entrada de {membro.mention}...")
    
    # Chamar manualmente o evento
    await on_member_join(membro)
    
    await ctx.send(f"✅ Simulação concluída para {membro.mention}!")

@bot.command(name="help")
async def help_cmd(ctx):
    """Mostra ajuda dos comandos"""
    
    embed = discord.Embed(
        title="🤖 Ajuda - Bot de Cargo Automático",
        description="Comandos disponíveis:",
        color=discord.Color.purple()
    )
    
    embed.add_field(
        name="!ping",
        value="Verifica se o bot está online",
        inline=False
    )
    
    embed.add_field(
        name="!status",
        value="Mostra status completo do bot",
        inline=False
    )
    
    embed.add_field(
        name="!check_cargo",
        value="Verifica configuração do sistema (apenas ADM)",
        inline=False
    )
    
    embed.add_field(
        name="!simular_entrada [@usuário]",
        value="Simula entrada de um membro (apenas ADM)",
        inline=False
    )
    
    embed.add_field(
        name="ℹ️ Funcionalidade Automática",
        value="O bot atribui automaticamente o cargo **'𝗩𝗶𝘀𝗶𝘁𝗮𝗻𝘁𝗲'** a novos membros",
        inline=False
    )
    
    embed.set_footer(text="Bot Online 24/7 • Sistema automático de cargos")
    
    await ctx.send(embed=embed)

# ==================== INICIALIZAÇÃO ====================

if __name__ == '__main__':
    print("=" * 50)
    print("🚀 INICIANDO BOT DE CARGO AUTOMÁTICO")
    print("=" * 50)
    
    # Verificar token
    TOKEN = os.getenv('DISCORD_TOKEN')
    
    # Se não encontrar na variável de ambiente, tentar arquivo .env
    if not TOKEN:
        try:
            from dotenv import load_dotenv
            load_dotenv()
            TOKEN = os.getenv('DISCORD_TOKEN')
        except:
            pass
    
    if not TOKEN:
        print("❌ ERRO: DISCORD_TOKEN não encontrado!")
        print("\n💡 SOLUÇÕES:")
        print("1. Configure a variável de ambiente:")
        print("   Render/UptimeRobot: Adicione 'DISCORD_TOKEN' nas Environment Variables")
        print("2. Crie um arquivo .env com:")
        print("   DISCORD_TOKEN=seu_token_aqui")
        print("\n🔗 Obtenha seu token em: https://discord.com/developers/applications")
        sys.exit(1)
    
    print("✅ Token encontrado")
    print("🤖 Iniciando servidor web para keep-alive...")
    
    # Iniciar servidor web para keep-alive
    start_keep_alive()
    
    # Iniciar bot
    try:
        print("🔗 Conectando ao Discord...")
        bot.run(TOKEN)
        
    except discord.LoginFailure:
        print("❌ ERRO: Token inválido ou expirado!")
        print("💡 Gere um novo token em: https://discord.com/developers/applications")
        
    except KeyboardInterrupt:
        print("\n👋 Bot encerrado pelo usuário")
        
    except Exception as e:
        print(f"❌ Erro inesperado: {type(e).__name__}: {e}")
