import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
import asyncio
from aiohttp import web
import threading

# Importar módulos
from modules.painel_msgs import PainelManager, PainelView, AgendamentoView

# Carrega variáveis de ambiente
load_dotenv()

# Configurar intents
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

# Criar bot
bot = commands.Bot(command_prefix='!', intents=intents, help_command=None)

# ===== SERVIDOR WEB PARA KEEP-ALIVE =====
class KeepAliveServer:
    def __init__(self):
        self.app = web.Application()
        self.setup_routes()
        self.runner = None
        self.site = None
    
    def setup_routes(self):
        self.app.router.add_get('/', self.handle_root)
        self.app.router.add_get('/health', self.handle_health)
    
    async def handle_root(self, request):
        return web.Response(text="✅ Bot Discord está online!")
    
    async def handle_health(self, request):
        return web.json_response({
            "status": "online",
            "bot": str(bot.user) if bot.user else "starting",
            "latency": f"{round(bot.latency * 1000)}ms" if bot.is_ready() else "0ms"
        })
    
    async def start(self, port=8080):
        self.runner = web.AppRunner(self.app)
        await self.runner.setup()
        self.site = web.TCPSite(self.runner, '0.0.0.0', port)
        await self.site.start()
        print(f"🌐 Servidor keep-alive iniciado na porta {port}")
        print(f"📊 Health check: http://0.0.0.0:{port}/health")
    
    async def stop(self):
        if self.site:
            await self.site.stop()
        if self.runner:
            await self.runner.cleanup()

# Instância do servidor
keep_alive = KeepAliveServer()

# ===== EVENTOS =====
@bot.event
async def on_ready():
    print(f'✅ Bot conectado como: {bot.user}')
    print(f'📊 ID: {bot.user.id}')
    print('--- Bot está online! ---')
    
    # Definir status
    await bot.change_presence(
        activity=discord.Activity(
            type=discord.ActivityType.watching,
            name="painel com !painel"
        )
    )
    
    # Adicionar views persistentes
    bot.add_view(PainelView(bot))
    bot.add_view(AgendamentoView())
    
    # Iniciar tarefa de keep-alive
    bot.loop.create_task(keep_alive_task())

# Tarefa de keep-alive
async def keep_alive_task():
    while True:
        try:
            # Ping simples para manter ativo
            if bot.is_ready():
                # Você pode adicionar logs aqui se quiser
                pass
            await asyncio.sleep(60)  # Verifica a cada 60 segundos
        except Exception as e:
            print(f"Erro na tarefa keep-alive: {e}")

# ===== COMANDOS DE PAINEL =====
@bot.command(name='painel')
async def painel(ctx):
    """Envia o painel de controle e deleta o comando"""
    
    # Deleta a mensagem do comando
    await ctx.message.delete()
    
    # Cria e envia o painel
    embed = await PainelManager.criar_painel_embed()
    await ctx.send(embed=embed, view=PainelView(bot))

@bot.command(name='agendamentos')
async def agendamentos(ctx):
    """Envia o painel de agendamentos privado e deleta o comando"""
    
    # Deleta a mensagem do comando
    await ctx.message.delete()
    
    # Cria e envia o painel de agendamentos (privado)
    embed = await PainelManager.criar_agendamento_embed()
    try:
        await ctx.author.send(embed=embed, view=AgendamentoView())
        
        # Confirma no canal (mensagem que será deletada depois)
        confirm_msg = await ctx.send(f"{ctx.author.mention} 📬 Painel de agendamentos enviado para sua DM!")
        await confirm_msg.delete(delay=5)
    except discord.Forbidden:
        error_msg = await ctx.send(f"{ctx.author.mention} ❌ Não consigo enviar DM para você! Verifique suas configurações de privacidade.")
        await error_msg.delete(delay=10)

# ===== COMANDOS DE STATUS =====
@bot.command(name='status')
async def status(ctx):
    """Mostra status do bot e informações do servidor"""
    
    embed = discord.Embed(
        title="📊 STATUS DO BOT",
        color=discord.Color.blue()
    )
    
    # Informações do bot
    embed.add_field(
        name="🤖 Bot",
        value=f"Nome: {bot.user.name}\nID: {bot.user.id}\nPing: {round(bot.latency * 1000)}ms",
        inline=True
    )
    
    # Informações do servidor
    if ctx.guild:
        embed.add_field(
            name="🏠 Servidor",
            value=f"Nome: {ctx.guild.name}\nMembros: {ctx.guild.member_count}\nCanais: {len(ctx.guild.channels)}",
            inline=True
        )
    
    # Status do keep-alive
    embed.add_field(
        name="🌐 Keep-Alive",
        value="✅ Ativo\nPorta: 8080\nHealth check: /health",
        inline=False
    )
    
    # Uptime (simplificado)
    embed.add_field(
        name="⏱️ Uptime",
        value="Use UptimeRobot para monitoramento externo",
        inline=False
    )
    
    embed.set_footer(text="Monitorado por UptimeRobot")
    
    await ctx.send(embed=embed)

@bot.command(name='ping')
async def ping(ctx):
    """Testa a latência do bot"""
    latency = round(bot.latency * 1000)
    
    embed = discord.Embed(
        title="🏓 Pong!",
        description=f"**Latência:** `{latency}ms`",
        color=discord.Color.green() if latency < 100 else discord.Color.orange() if latency < 200 else discord.Color.red()
    )
    
    # Adiciona status baseado na latência
    if latency < 100:
        status = "✅ Excelente"
    elif latency < 200:
        status = "⚠️ Moderada"
    else:
        status = "❌ Alta"
    
    embed.add_field(name="Status", value=status, inline=True)
    embed.add_field(name="Keep-Alive", value="✅ Ativo", inline=True)
    
    await ctx.send(embed=embed)

@bot.command(name='ajuda')
async def ajuda(ctx):
    """Mostra ajuda dos comandos"""
    embed = discord.Embed(
        title="🤖 COMANDOS DISPONÍVEIS",
        color=discord.Color.blue()
    )
    
    embed.add_field(
        name="📊 **PAINEL**",
        value="`!painel` - Mostra o painel de controle do servidor\n`!agendamentos` - Abre painel de agendamentos (privado)",
        inline=False
    )
    
    embed.add_field(
        name="🔧 **UTILITÁRIOS**",
        value="`!ping` - Testa a latência do bot\n`!status` - Mostra status completo\n`!ajuda` - Mostra esta mensagem",
        inline=False
    )
    
    embed.add_field(
        name="📝 **NOTAS**",
        value="• Comandos `!painel` e `!agendamentos` são auto-deletados\n• Agendamentos são visíveis apenas para você\n• Bot com keep-alive ativo na porta 8080",
        inline=False
    )
    
    embed.set_footer(text="Monitorado por UptimeRobot • Health check: /health")
    
    await ctx.send(embed=embed)

# ===== TRATAMENTO DE ERROS =====
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        embed = discord.Embed(
            title="❌ Comando não encontrado",
            description="Use `!ajuda` para ver os comandos disponíveis.",
            color=discord.Color.red()
        )
        msg = await ctx.send(embed=embed)
        await msg.delete(delay=10)
    elif isinstance(error, commands.MissingPermissions):
        await ctx.send("❌ Você não tem permissão para usar este comando!", delete_after=10)
    else:
        print(f"Erro: {error}")

# ===== INICIAR BOT COM KEEP-ALIVE =====
async def main():
    """Função principal para iniciar bot e servidor web"""
    
    # Iniciar servidor web em segundo plano
    port = int(os.getenv('PORT', 8080))
    await keep_alive.start(port)
    
    # Iniciar bot Discord
    TOKEN = os.getenv('DISCORD_TOKEN')
    if not TOKEN:
        print("❌ ERRO: DISCORD_TOKEN não encontrado!")
        print("Configure no Render: Environment → DISCORD_TOKEN")
        print("Ou crie um arquivo .env com: DISCORD_TOKEN=seu_token_aqui")
        return
    
    print("🚀 Iniciando bot com keep-alive...")
    await bot.start(TOKEN)

# Handler para desligamento
async def shutdown():
    """Desliga o bot e servidor web"""
    print("🛑 Desligando bot...")
    await keep_alive.stop()
    await bot.close()

if __name__ == "__main__":
    try:
        # Inicia o bot com keep-alive
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Bot interrompido pelo usuário")
    except Exception as e:
        print(f"❌ Erro fatal: {e}")
        asyncio.run(shutdown())
