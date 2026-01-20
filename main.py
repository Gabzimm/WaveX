import discord
from discord.ext import commands
import os
from datetime import datetime
import asyncio
import sys
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('discord')

# Configuração do bot
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.guilds = True

class WaveXBot(commands.Bot):
    def __init__(self):
        super().__init__(
            command_prefix='!',
            intents=intents,
            help_command=None,
            case_insensitive=True
        )
        self.start_time = datetime.now()
        self.modules_loaded = []
    
    async def setup_hook(self):
        """Carrega os módulos/cogs automaticamente"""
        print("⚙️ Iniciando carregamento de módulos...")
        
        # Carregar módulos da pasta modules/
        for filename in os.listdir('./modules'):
            if filename.endswith('.py'):
                module_name = f'modules.{filename[:-3]}'
                try:
                    await self.load_extension(module_name)
                    self.modules_loaded.append(filename[:-3])
                    print(f"✅ Módulo carregado: {filename[:-3]}")
                except Exception as e:
                    print(f"❌ Erro ao carregar {filename}: {e}")
        
        print(f"✅ Total de módulos carregados: {len(self.modules_loaded)}")
    
    async def on_ready(self):
        """Evento quando o bot está pronto"""
        print(f"\n{'='*50}")
        print(f"🤖 Bot conectado como: {self.user}")
        print(f"🆔 ID: {self.user.id}")
        print(f"⏰ Hora: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
        print(f"📊 Servidores: {len(self.guilds)}")
        print(f"📦 Módulos: {', '.join(self.modules_loaded)}")
        print(f"{'='*50}\n")
        
        # Mudar status
        await self.change_presence(
            activity=discord.Activity(
                type=discord.ActivityType.watching,
                name=f"{len(self.guilds)} servidores | !ajuda"
            ),
            status=discord.Status.online
        )
    
    async def on_guild_join(self, guild):
        """Quando o bot entra em um novo servidor"""
        print(f"🎉 Entrei no servidor: {guild.name} (ID: {guild.id})")
        
        # Encontrar canal geral para enviar mensagem
        try:
            # Tenta encontrar um canal chamado 'geral' ou primeiro canal de texto
            channel = discord.utils.get(guild.text_channels, name='geral')
            if not channel:
                channel = guild.text_channels[0]
            
            if channel.permissions_for(guild.me).send_messages:
                embed = discord.Embed(
                    title="🤖 WaveX Bot - Conectado!",
                    description=(
                        "Olá! Eu sou o **WaveX**, seu assistente de servidor Discord.\n"
                        "Estou aqui para ajudar com administração, tickets, sets e muito mais!\n\n"
                        "**📋 Comandos principais:**\n"
                        "• `!setup_tickets` - Configura sistema de tickets\n"
                        "• `!setup_sets` - Configura sistema de sets\n"
                        "• `!setup_cargos` - Configura sistema de cargos\n"
                        "• `!ajuda` - Mostra todos os comandos\n\n"
                        "**🔧 Precisa de ajuda?**\n"
                        "Use `!suporte` para falar com nossa equipe!"
                    ),
                    color=discord.Color.purple()
                )
                embed.set_footer(text="WaveX Bot • Sistema profissional")
                await channel.send(embed=embed)
        except Exception as e:
            print(f"⚠️ Não pude enviar mensagem em {guild.name}: {e}")
    
    async def on_command_error(self, ctx, error):
        """Tratamento de erros de comandos"""
        if isinstance(error, commands.CommandNotFound):
            embed = discord.Embed(
                title="❌ Comando não encontrado",
                description=f"Use `!ajuda` para ver todos os comandos disponíveis.",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed, delete_after=10)
        elif isinstance(error, commands.MissingPermissions):
            embed = discord.Embed(
                title="🚫 Permissão negada",
                description="Você não tem permissão para usar este comando.",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed, delete_after=10)
        else:
            print(f"⚠️ Erro no comando: {error}")
            
            embed = discord.Embed(
                title="⚠️ Erro interno",
                description="Ocorreu um erro ao executar o comando.",
                color=discord.Color.orange()
            )
            await ctx.send(embed=embed, delete_after=10)

# Criar instância do bot
bot = WaveXBot()

# Comandos principais (podem ficar aqui ou em módulos separados)
@bot.command(name="ping")
async def ping(ctx):
    """Mostra a latência do bot"""
    latency = round(bot.latency * 1000)
    
    embed = discord.Embed(
        title="🏓 Pong!",
        description=f"Latência: **{latency}ms**",
        color=discord.Color.green()
    )
    embed.set_footer(text=f"Solicitado por {ctx.author.name}")
    
    await ctx.send(embed=embed)

@bot.command(name="ajuda")
async def ajuda(ctx):
    """Mostra todos os comandos disponíveis"""
    embed = discord.Embed(
        title="📚 Central de Ajuda - WaveX Bot",
        description=(
            "Aqui estão todos os comandos disponíveis:\n\n"
            "**🎫 SISTEMA DE TICKETS**\n"
            "• `!setup_tickets` - Configura painel de tickets\n"
            "• `!ticket_info` - Informações do ticket atual\n"
            "• `!fechar_ticket` - Fecha o ticket atual\n\n"
            "**👤 SISTEMA DE SETS**\n"
            "• `!setup_sets` - Configura painel de sets\n"
            "• `!check_id [id]` - Verifica ID Fivem\n"
            "• `!sets_pendentes` - Lista sets pendentes\n\n"
            "**👑 SISTEMA DE CARGOS**\n"
            "• `!setup_cargos` - Configura sistema de cargos\n"
            "• `!cargo_add @user @cargo` - Adiciona cargo\n"
            "• `!cargo_remove @user @cargo` - Remove cargo\n\n"
            "**🔧 UTILIDADES**\n"
            "• `!ping` - Mostra latência do bot\n"
            "• `!status` - Status do bot\n"
            "• `!limpar [quantidade]` - Limpa mensagens\n\n"
            "**👑 ADMINISTRAÇÃO**\n"
            "• `!ban @user` - Bane um usuário\n"
            "• `!kick @user` - Expulsa um usuário\n"
            "• `!mute @user` - Silencia um usuário"
        ),
        color=discord.Color.purple()
    )
    embed.set_footer(text="Use !comando para executar • WaveX Bot")
    
    await ctx.send(embed=embed)

@bot.command(name="status")
@commands.has_permissions(administrator=True)
async def status(ctx):
    """Mostra status detalhado do bot"""
    uptime = datetime.now() - bot.start_time
    hours, remainder = divmod(int(uptime.total_seconds()), 3600)
    minutes, seconds = divmod(remainder, 60)
    
    embed = discord.Embed(
        title="📊 Status do WaveX Bot",
        color=discord.Color.blue()
    )
    
    embed.add_field(name="🤖 Nome", value=bot.user.name, inline=True)
    embed.add_field(name="🆔 ID", value=bot.user.id, inline=True)
    embed.add_field(name="📅 Criado em", value=bot.user.created_at.strftime("%d/%m/%Y"), inline=True)
    
    embed.add_field(name="🏠 Servidores", value=len(bot.guilds), inline=True)
    embed.add_field(name="👥 Usuários", value=sum(g.member_count for g in bot.guilds), inline=True)
    embed.add_field(name="📦 Módulos", value=len(bot.modules_loaded), inline=True)
    
    embed.add_field(name="⚡ Latência", value=f"{round(bot.latency * 1000)}ms", inline=True)
    embed.add_field(name="⏰ Uptime", value=f"{hours}h {minutes}m {seconds}s", inline=True)
    embed.add_field(name="💾 Versão Python", value=sys.version.split()[0], inline=True)
    
    if bot.modules_loaded:
        embed.add_field(
            name="✅ Módulos ativos", 
            value=", ".join(bot.modules_loaded), 
            inline=False
        )
    
    embed.set_footer(text=f"Solicitado por {ctx.author.name}")
    
    await ctx.send(embed=embed)

@bot.command(name="limpar")
@commands.has_permissions(manage_messages=True)
async def limpar(ctx, quantidade: int = 10):
    """Limpa mensagens do canal"""
    if quantidade > 100:
        quantidade = 100
    
    deleted = await ctx.channel.purge(limit=quantidade + 1)  # +1 para incluir o comando
    
    embed = discord.Embed(
        title="🧹 Mensagens limpas",
        description=f"**{len(deleted)-1}** mensagens foram removidas.",
        color=discord.Color.green()
    )
    msg = await ctx.send(embed=embed, delete_after=5)

@bot.command(name="suporte")
async def suporte(ctx):
    """Informações de suporte"""
    embed = discord.Embed(
        title="🔧 Suporte WaveX",
        description=(
            "**Precisa de ajuda?** Aqui estão nossos contatos:\n\n"
            "**🎮 Discord:** [wavex.support](https://discord.gg/seu-link)\n"
            "**📧 Email:** contato@wavex.com\n"
            "**🌐 Site:** https://wavex.onrender.com\n\n"
            "**📞 Atendimento:**\n"
            "• Suporte via tickets: 24/7\n"
            "• Tempo médio de resposta: 15min\n"
            "• Equipe especializada sempre disponível"
        ),
        color=discord.Color.blue()
    )
    embed.set_footer(text="WaveX Bot • Suporte profissional")
    
    await ctx.send(embed=embed)

@bot.command(name="reload")
@commands.has_permissions(administrator=True)
async def reload_module(ctx, module_name: str = None):
    """Recarrega um módulo específico"""
    if module_name:
        try:
            await bot.reload_extension(f"modules.{module_name}")
            embed = discord.Embed(
                title="🔄 Módulo recarregado",
                description=f"O módulo **{module_name}** foi recarregado com sucesso!",
                color=discord.Color.green()
            )
            await ctx.send(embed=embed)
            print(f"✅ Módulo recarregado: {module_name}")
        except Exception as e:
            embed = discord.Embed(
                title="❌ Erro ao recarregar",
                description=f"Erro: {e}",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
    else:
        embed = discord.Embed(
            title="❌ Especifique um módulo",
            description="Uso: `!reload [nome_do_modulo]`\nExemplo: `!reload tickets`",
            color=discord.Color.orange()
        )
        await ctx.send(embed=embed)

# Comando de teste rápido
@bot.command(name="teste")
async def teste(ctx):
    """Comando de teste rápido"""
    embed = discord.Embed(
        title="🧪 Teste do WaveX Bot",
        description="✅ Bot funcionando perfeitamente!\n\n"
                   "**Módulos carregados:**\n" + 
                   "\n".join([f"• {mod}" for mod in bot.modules_loaded]),
        color=discord.Color.purple()
    )
    embed.set_footer(text=f"Testado por {ctx.author.name}")
    
    await ctx.send(embed=embed)

# Inicialização do bot
async def main():
    """Função principal de inicialização"""
    try:
        # Verificar se o token está definido
        token = os.getenv('DISCORD_TOKEN')
        if not token:
            print("❌ ERRO: Token do Discord não encontrado!")
            print("Defina a variável de ambiente DISCORD_TOKEN")
            sys.exit(1)
        
        print("🚀 Iniciando WaveX Bot...")
        print(f"📦 Python: {sys.version}")
        print(f"🤖 Discord.py: {discord.__version__}")
        
        # Iniciar bot
        async with bot:
            await bot.start(token)
            
    except KeyboardInterrupt:
        print("\n👋 Bot encerrado pelo usuário")
    except Exception as e:
        print(f"❌ ERRO CRÍTICO: {e}")
        import traceback
        traceback.print_exc()
    finally:
        print("🔴 Bot desconectado")

# Ponto de entrada
if __name__ == "__main__":
    # Configuração para produção
    import sys
    import warnings
    
    # Ignorar avisos específicos
    warnings.filterwarnings("ignore", category=DeprecationWarning)
    
    # Executar bot
    asyncio.run(main())
