"""
🤖 BOT DE CARGO AUTOMÁTICO + PAINEL DE MENSAGENS AVANÇADO
Funcionalidades:
1. Atribui cargo "𝗩𝗶𝘀𝗶𝘁𝗮𝗻𝘁𝗲" automaticamente
2. Painel de envio de mensagens avançado
3. Templates, agendamento, multi-canal
"""

import os
import sys
import json
import asyncio
from threading import Thread
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import aiofiles

# ========== CONFIGURAÇÃO DO BOT ==========
print("=" * 60)
print("🚀 INICIANDO BOT AVANÇADO - CARGO + PAINEL DE MENSAGENS")
print("=" * 60)

# Tentar importar discord.py
try:
    import discord
    from discord.ext import commands, tasks
    print("✅ discord.py importado com sucesso")
except ImportError:
    print("❌ discord.py não encontrado!")
    print("💡 Instale com: pip install discord.py==2.3.2")
    sys.exit(1)

# Configurar intents
intents = discord.Intents.default()
intents.members = True
intents.guilds = True
intents.message_content = True

# Criar bot
bot = commands.Bot(
    command_prefix='!',
    intents=intents,
    help_command=None
)

# ========== SERVIDOR WEB PARA UPTIMEROBOT ==========
try:
    from flask import Flask
    app = Flask(__name__)
    
    @app.route('/')
    def home():
        status = "🟢 ONLINE" if bot.is_ready() else "🟡 CONECTANDO"
        return f"""
        <html>
        <head><title>🤖 Bot Avançado</title>
        <style>
            body {{font-family: Arial; text-align: center; padding: 20px; 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white;}}
            .container {{background: rgba(0,0,0,0.8); padding: 30px; border-radius: 15px; max-width: 600px; margin: auto;}}
            .status {{background: #28a745; padding: 15px; border-radius: 10px; margin: 20px 0;}}
        </style>
        </head>
        <body>
            <div class="container">
                <h1>🤖 Bot Avançado</h1>
                <div class="status">{status}</div>
                <p>Sistema de Cargo Automático + Painel de Mensagens</p>
                <p><small>{datetime.now().strftime('%d/%m/%Y %H:%M:%S')}</small></p>
            </div>
        </body>
        </html>
        """
    
    @app.route('/health')
    def health():
        return "OK", 200
    
    def run_web_server():
        app.run(host='0.0.0.0', port=8080, debug=False, threaded=True)
    
    web_thread = Thread(target=run_web_server, daemon=True)
    web_thread.start()
    print("✅ Servidor web iniciado!")
    
except ImportError:
    print("⚠️ Flask não encontrado. Servidor web não será iniciado.")

# ========== SISTEMA DE ARMAZENAMENTO ==========
DATA_FILE = "mensagens_data.json"

class SistemaMensagens:
    def __init__(self):
        self.templates = {}
        self.mensagens_agendadas = {}
        self.canais_favoritos = {}
        self.carregar_dados()
    
    def carregar_dados(self):
        """Carrega dados do arquivo JSON"""
        try:
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.templates = data.get('templates', {})
                self.mensagens_agendadas = data.get('mensagens_agendadas', {})
                self.canais_favoritos = data.get('canais_favoritos', {})
            print(f"✅ Dados carregados: {len(self.templates)} templates, {len(self.mensagens_agendadas)} agendamentos")
        except FileNotFoundError:
            self.criar_templates_padrao()
            self.salvar_dados()
    
    def salvar_dados(self):
        """Salva dados no arquivo JSON"""
        data = {
            'templates': self.templates,
            'mensagens_agendadas': self.mensagens_agendadas,
            'canais_favoritos': self.canais_favoritos
        }
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def criar_templates_padrao(self):
        """Cria templates padrão"""
        self.templates = {
            'anuncio_importante': {
                'nome': '📢 Anúncio Importante',
                'conteudo': '**{titulo}**\n\n{conteudo}\n\n📅 Data: {data}\n⏰ Horário: {hora}',
                'cor': '#FF0000',
                'variaveis': ['titulo', 'conteudo', 'data', 'hora']
            },
            'evento': {
                'nome': '🎉 Evento',
                'conteudo': '**🎮 EVENTO: {nome_evento}**\n\n{descricao}\n\n📅 **Data:** {data}\n⏰ **Horário:** {hora}\n📍 **Local:** {local}\n\n👉 **Como participar:** {participacao}',
                'cor': '#00FF00',
                'variaveis': ['nome_evento', 'descricao', 'data', 'hora', 'local', 'participacao']
            },
            'atualizacao': {
                'nome': '📅 Atualização',
                'conteudo': '**🔄 ATUALIZAÇÃO DO SISTEMA**\n\n{conteudo}\n\n🔧 **Novidades:**\n{novidades}\n\n🛠️ **Correções:**\n{correcoes}\n\n📋 **Próximas atualizações:**\n{proximas}',
                'cor': '#0000FF',
                'variaveis': ['conteudo', 'novidades', 'correcoes', 'proximas']
            },
            'aviso': {
                'nome': '⚠️ Aviso',
                'conteudo': '**⚠️ AVISO IMPORTANTE**\n\n{mensagem}\n\n🔒 **Medidas tomadas:**\n{medidas}\n\n📞 **Suporte:** {suporte}',
                'cor': '#FFA500',
                'variaveis': ['mensagem', 'medidas', 'suporte']
            }
        }
        print("✅ Templates padrão criados!")

sistema_mensagens = SistemaMensagens()

# ========== EVENTOS DO BOT ==========

@bot.event
async def on_ready():
    """Quando o bot conecta ao Discord"""
    print("=" * 60)
    print(f"✅ BOT CONECTADO: {bot.user.name}")
    print(f"🆔 ID: {bot.user.id}")
    print(f"📡 Ping: {round(bot.latency * 1000)}ms")
    print(f"🏠 Servidores: {len(bot.guilds)}")
    print("=" * 60)
    
    # Iniciar tarefa de verificar agendamentos
    verificar_agendamentos.start()
    print("✅ Tarefa de agendamentos iniciada")
    
    # Configurar painel em cada servidor
    for guild in bot.guilds:
        await configurar_painel(guild)
    
    await bot.change_presence(
        activity=discord.Activity(
            type=discord.ActivityType.watching,
            name=f"📢 Painel de Mensagens"
        )
    )
    
    print("🎯 Sistema de cargo + painel de mensagens pronto!")

@bot.event
async def on_member_join(member):
    """Atribui cargo automaticamente"""
    print(f"\n{'='*50}")
    print(f"👤 NOVO MEMBRO: {member.name}")
    
    try:
        cargo_nome = "𝗩𝗶𝘀𝗶𝘁𝗮𝗻𝘁𝗲"
        cargo = discord.utils.get(member.guild.roles, name=cargo_nome)
        
        if not cargo:
            print(f"⚠️ Criando cargo '{cargo_nome}'...")
            cargo = await member.guild.create_role(
                name=cargo_nome,
                color=discord.Color.light_grey(),
                reason="Criado automaticamente"
            )
            print(f"✅ Cargo criado!")
        
        await member.add_roles(cargo)
        print(f"✅ Cargo atribuído a {member.name}")
        
    except Exception as e:
        print(f"❌ Erro: {e}")
    
    print(f"{'='*50}")

@bot.event
async def on_guild_channel_create(channel):
    """Detecta quando um canal/categoria é criado"""
    print(f"\n📁 Canal criado: {channel.name} ({channel.type})")
    
    # Registrar no sistema para aparecer no painel
    guild_id = str(channel.guild.id)
    
    if guild_id not in sistema_mensagens.canais_favoritos:
        sistema_mensagens.canais_favoritos[guild_id] = []
    
    # Adicionar se não estiver na lista
    canal_info = {
        'id': channel.id,
        'name': channel.name,
        'type': str(channel.type)
    }
    
    if canal_info not in sistema_mensagens.canais_favoritos[guild_id]:
        sistema_mensagens.canais_favoritos[guild_id].append(canal_info)
        sistema_mensagens.salvar_dados()
        print(f"✅ Canal adicionado ao sistema: {channel.name}")

# ========== SISTEMA DE AGENDAMENTO ==========

@tasks.loop(seconds=30)
async def verificar_agendamentos():
    """Verifica e envia mensagens agendadas"""
    now = datetime.now()
    to_remove = []
    
    for msg_id, agendamento in sistema_mensagens.mensagens_agendadas.items():
        agendamento_time = datetime.fromisoformat(agendamento['hora_envio'])
        
        if now >= agendamento_time:
            try:
                guild = bot.get_guild(agendamento['guild_id'])
                if guild:
                    for channel_id in agendamento['canais']:
                        channel = guild.get_channel(channel_id)
                        if channel:
                            # Processar variáveis
                            conteudo = processar_template(
                                agendamento['conteudo'], 
                                agendamento.get('variaveis', {})
                            )
                            
                            embed = criar_embed_mensagem(
                                agendamento['titulo'],
                                conteudo,
                                agendamento.get('cor', '#3498db')
                            )
                            
                            await channel.send(embed=embed)
                            print(f"✅ Mensagem agendada enviada: {agendamento['titulo']} em #{channel.name}")
                
                to_remove.append(msg_id)
                
            except Exception as e:
                print(f"❌ Erro ao enviar mensagem agendada: {e}")
    
    # Remover mensagens já enviadas
    for msg_id in to_remove:
        sistema_mensagens.mensagens_agendadas.pop(msg_id, None)
    
    if to_remove:
        sistema_mensagens.salvar_dados()

# ========== FUNÇÕES AUXILIARES ==========

def processar_template(template: str, variaveis: dict) -> str:
    """Substitui variáveis no template"""
    resultado = template
    for key, value in variaveis.items():
        resultado = resultado.replace(f"{{{key}}}", str(value))
    return resultado

def criar_embed_mensagem(titulo: str, conteudo: str, cor: str) -> discord.Embed:
    """Cria embed para mensagem"""
    try:
        color = discord.Color.from_str(cor)
    except:
        color = discord.Color.blue()
    
    embed = discord.Embed(
        title=titulo,
        description=conteudo,
        color=color,
        timestamp=datetime.now()
    )
    embed.set_footer(text="📢 Sistema de Mensagens Automático")
    return embed

async def configurar_painel(guild: discord.Guild):
    """Configura o painel no canal especificado"""
    canal_painel = discord.utils.get(guild.text_channels, name="𝗪𝗮𝘃𝗲𝗫-𝗣𝗡𝗘𝗟_𝗠𝗦𝗚")
    
    if canal_painel:
        # Limpar mensagens antigas do bot
        try:
            async for message in canal_painel.history(limit=20):
                if message.author == bot.user:
                    await message.delete()
                    await asyncio.sleep(1)
        except:
            pass
        
        # Enviar novo painel
        await enviar_painel_principal(canal_painel)
        print(f"✅ Painel configurado em #{canal_painel.name}")
    else:
        print(f"⚠️ Canal '𝗪𝗮𝘃𝗲𝗫-𝗣𝗡𝗘𝗟_𝗠𝗦𝗚' não encontrado em {guild.name}")

async def enviar_painel_principal(canal: discord.TextChannel):
    """Envia o painel principal"""
    embed = discord.Embed(
        title="📢 **PAINEL DE MENSAGENS AVANÇADO**",
        description=(
            "**Sistema completo de gerenciamento de mensagens**\n\n"
            "🎯 **Funcionalidades disponíveis:**\n"
            "• 📋 **Templates** com variáveis\n"
            "• 👁️ **Pré-visualização** antes de enviar\n"
            "• ⏰ **Agendamento** automático\n"
            "• 📤 **Multi-canal** (envie para vários de uma vez)\n"
            "• ⭐ **Favoritos** (canais rapidamente acessíveis)\n\n"
            "**Clique nos botões abaixo para começar:**"
        ),
        color=discord.Color.purple()
    )
    
    embed.add_field(
        name="📊 **Status do Sistema**",
        value=(
            f"• Templates: {len(sistema_mensagens.templates)}\n"
            f"• Agendamentos: {len(sistema_mensagens.mensagens_agendadas)}\n"
            f"• Canais detectados: {len(sistema_mensagens.canais_favoritos.get(str(canal.guild.id), []))}"
        ),
        inline=True
    )
    
    embed.add_field(
        name="⚙️ **Comandos Úteis**",
        value=(
            "• `!painel` - Recarrega este painel\n"
            "• `!templates` - Lista todos templates\n"
            "• `!agendamentos` - Lista mensagens agendadas"
        ),
        inline=True
    )
    
    embed.set_footer(text="Sistema de Mensagens • Atualizado automaticamente")
    
    view = PainelPrincipalView()
    await canal.send(embed=embed, view=view)

# ========== CLASSES DO PAINEL ==========

class PainelPrincipalView(discord.ui.View):
    """View principal do painel"""
    def __init__(self):
        super().__init__(timeout=None)
    
    @discord.ui.button(label="📝 Enviar Mensagem", style=discord.ButtonStyle.primary, emoji="📝", custom_id="enviar_mensagem")
    async def enviar_mensagem(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Abre modal para enviar mensagem"""
        modal = ModalEnviarMensagem()
        await interaction.response.send_modal(modal)
    
    @discord.ui.button(label="📋 Usar Template", style=discord.ButtonStyle.green, emoji="📋", custom_id="usar_template")
    async def usar_template(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Selecionar template"""
        view = TemplateSelectView()
        await interaction.response.send_message("📋 **Selecione um template:**", view=view, ephemeral=True)
    
    @discord.ui.button(label="⏰ Agendar Mensagem", style=discord.ButtonStyle.secondary, emoji="⏰", custom_id="agendar_mensagem")
    async def agendar_mensagem(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Agendar mensagem para envio futuro"""
        modal = ModalAgendarMensagem()
        await interaction.response.send_modal(modal)
    
    @discord.ui.button(label="⭐ Canais Favoritos", style=discord.ButtonStyle.success, emoji="⭐", custom_id="canais_favoritos")
    async def canais_favoritos(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Gerenciar canais favoritos"""
        view = CanaisFavoritosView(interaction.guild)
        await interaction.response.send_message("⭐ **Canais Favoritos:**", view=view, ephemeral=True)
    
    @discord.ui.button(label="🔄 Atualizar Painel", style=discord.ButtonStyle.gray, emoji="🔄", custom_id="atualizar_painel")
    async def atualizar_painel(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Recarrega o painel"""
        await interaction.response.defer()
        await enviar_painel_principal(interaction.channel)
        await interaction.followup.send("✅ Painel atualizado!", ephemeral=True)

class TemplateSelectView(discord.ui.View):
    """View para selecionar template"""
    def __init__(self):
        super().__init__()
        
        # Adicionar dropdown com templates
        select = discord.ui.Select(
            placeholder="📋 Selecione um template...",
            min_values=1,
            max_values=1,
            options=[
                discord.SelectOption(
                    label=template['nome'],
                    value=template_id,
                    description=f"Variáveis: {', '.join(template['variaveis'])}"
                )
                for template_id, template in sistema_mensagens.templates.items()
            ]
        )
        select.callback = self.template_selecionado
        self.add_item(select)
    
    async def template_selecionado(self, interaction: discord.Interaction):
        """Quando um template é selecionado"""
        template_id = interaction.data['values'][0]
        template = sistema_mensagens.templates[template_id]
        
        # Criar modal com campos para cada variável
        modal = ModalTemplateVariaveis(template_id, template)
        await interaction.response.send_modal(modal)

class ModalEnviarMensagem(discord.ui.Modal, title="📝 Enviar Mensagem"):
    """Modal para enviar mensagem personalizada"""
    
    titulo = discord.ui.TextInput(
        label="Título da mensagem:",
        placeholder="Ex: Anúncio Importante",
        required=True,
        max_length=100
    )
    
    conteudo = discord.ui.TextInput(
        label="Conteúdo da mensagem:",
        placeholder="Digite sua mensagem aqui...",
        style=discord.TextStyle.paragraph,
        required=True,
        max_length=2000
    )
    
    cor = discord.ui.TextInput(
        label="Cor (hexadecimal):",
        placeholder="Ex: #FF0000 para vermelho",
        default="#3498db",
        required=False,
        max_length=7
    )
    
    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        
        # Mostrar pré-visualização
        embed = criar_embed_mensagem(
            self.titulo.value,
            self.conteudo.value,
            self.cor.value
        )
        
        # Pedir seleção de canais
        view = SelecaoCanaisView(
            self.titulo.value,
            self.conteudo.value,
            self.cor.value,
            None,  # Sem variáveis
            False   # Não é agendamento
        )
        
        await interaction.followup.send(
            "👁️ **Pré-visualização da mensagem:**",
            embed=embed,
            view=view,
            ephemeral=True
        )

class ModalAgendarMensagem(discord.ui.Modal, title="⏰ Agendar Mensagem"):
    """Modal para agendar mensagem"""
    
    titulo = discord.ui.TextInput(
        label="Título da mensagem:",
        placeholder="Ex: Lembrete do Evento",
        required=True,
        max_length=100
    )
    
    conteudo = discord.ui.TextInput(
        label="Conteúdo da mensagem:",
        placeholder="Digite sua mensagem aqui...",
        style=discord.TextStyle.paragraph,
        required=True,
        max_length=2000
    )
    
    data_hora = discord.ui.TextInput(
        label="Data e hora (DD/MM/AAAA HH:MM):",
        placeholder="Ex: 25/01/2026 20:30",
        required=True
    )
    
    cor = discord.ui.TextInput(
        label="Cor (hexadecimal):",
        placeholder="Ex: #FF0000",
        default="#3498db",
        required=False,
        max_length=7
    )
    
    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        
        try:
            # Converter data/hora
            data_hora_obj = datetime.strptime(self.data_hora.value, "%d/%m/%Y %H:%M")
            
            if data_hora_obj <= datetime.now():
                await interaction.followup.send("❌ A data/hora deve ser no futuro!", ephemeral=True)
                return
            
            # Mostrar pré-visualização
            embed = criar_embed_mensagem(
                self.titulo.value,
                self.conteudo.value,
                self.cor.value
            )
            embed.add_field(name="⏰ Agendado para", value=data_hora_obj.strftime("%d/%m/%Y %H:%M"))
            
            # Pedir seleção de canais
            view = SelecaoCanaisView(
                self.titulo.value,
                self.conteudo.value,
                self.cor.value,
                None,
                True,  # É agendamento
                data_hora_obj
            )
            
            await interaction.followup.send(
                "👁️ **Pré-visualização da mensagem agendada:**",
                embed=embed,
                view=view,
                ephemeral=True
            )
            
        except ValueError:
            await interaction.followup.send("❌ Formato de data/hora inválido! Use DD/MM/AAAA HH:MM", ephemeral=True)

class ModalTemplateVariaveis(discord.ui.Modal):
    """Modal para preencher variáveis do template"""
    
    def __init__(self, template_id: str, template: dict):
        super().__init__(title=f"📋 {template['nome']}")
        self.template_id = template_id
        self.template = template
        
        # Criar campo para cada variável
        for var in template['variaveis']:
            field = discord.ui.TextInput(
                label=f"{var.replace('_', ' ').title()}:",
                placeholder=f"Digite o valor para {var}...",
                required=True,
                max_length=200
            )
            setattr(self, var, field)
            self.add_item(field)
    
    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        
        # Coletar valores das variáveis
        variaveis = {}
        for var in self.template['variaveis']:
            field = getattr(self, var)
            variaveis[var] = field.value
        
        # Processar template
        conteudo_processado = processar_template(self.template['conteudo'], variaveis)
        
        # Mostrar pré-visualização
        embed = criar_embed_mensagem(
            self.template['nome'],
            conteudo_processado,
            self.template['cor']
        )
        
        # Pedir seleção de canais
        view = SelecaoCanaisView(
            self.template['nome'],
            conteudo_processado,
            self.template['cor'],
            variaveis,
            False
        )
        
        await interaction.followup.send(
            "👁️ **Pré-visualização do template:**",
            embed=embed,
            view=view,
            ephemeral=True
        )

class SelecaoCanaisView(discord.ui.View):
    """View para selecionar canais de destino"""
    
    def __init__(self, titulo: str, conteudo: str, cor: str, variaveis: dict, 
                 is_agendamento: bool, data_hora: datetime = None):
        super().__init__()
        self.titulo = titulo
        self.conteudo = conteudo
        self.cor = cor
        self.variaveis = variaveis or {}
        self.is_agendamento = is_agendamento
        self.data_hora = data_hora
        self.canais_selecionados = []
    
    @discord.ui.button(label="📂 Selecionar Canais", style=discord.ButtonStyle.primary, emoji="📂")
    async def selecionar_canais(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Abre modal para selecionar canais"""
        
        # Obter categorias do servidor
        categorias = [c for c in interaction.guild.categories if c.channels]
        
        if not categorias:
            await interaction.response.send_message("❌ Não há categorias disponíveis!", ephemeral=True)
            return
        
        view = SelecaoCategoriaView(self, categorias)
        await interaction.response.send_message(
            "📂 **Selecione uma categoria:**",
            view=view,
            ephemeral=True
        )
    
    @discord.ui.button(label="⭐ Usar Favoritos", style=discord.ButtonStyle.success, emoji="⭐")
    async def usar_favoritos(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Usa canais favoritos"""
        guild_id = str(interaction.guild.id)
        favoritos = sistema_mensagens.canais_favoritos.get(guild_id, [])
        
        if not favoritos:
            await interaction.response.send_message("❌ Nenhum canal favorito configurado!", ephemeral=True)
            return
        
        self.canais_selecionados = [fav['id'] for fav in favoritos]
        await self.enviar_mensagem(interaction)
    
    @discord.ui.button(label="✅ Enviar Agora", style=discord.ButtonStyle.green, emoji="✅", row=1)
    async def enviar_agora(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Envia para os canais selecionados"""
        if not self.canais_selecionados:
            await interaction.response.send_message("❌ Selecione canais primeiro!", ephemeral=True)
            return
        
        await self.enviar_mensagem(interaction)
    
    async def enviar_mensagem(self, interaction: discord.Interaction):
        """Envia a mensagem para os canais selecionados"""
        await interaction.response.defer(ephemeral=True)
        
        if self.is_agendamento:
            # Salvar como agendamento
            msg_id = f"agendamento_{int(datetime.now().timestamp())}"
            sistema_mensagens.mensagens_agendadas[msg_id] = {
                'titulo': self.titulo,
                'conteudo': self.conteudo,
                'cor': self.cor,
                'variaveis': self.variaveis,
                'canais': self.canais_selecionados,
                'guild_id': interaction.guild.id,
                'hora_envio': self.data_hora.isoformat(),
                'criado_por': interaction.user.id
            }
            sistema_mensagens.salvar_dados()
            
            await interaction.followup.send(
                f"✅ Mensagem agendada para {self.data_hora.strftime('%d/%m/%Y %H:%M')} "
                f"em {len(self.canais_selecionados)} canal(is)!",
                ephemeral=True
            )
        else:
            # Enviar agora
            sucesso = 0
            falhas = 0
            
            for channel_id in self.canais_selecionados:
                try:
                    channel = interaction.guild.get_channel(channel_id)
                    if channel and isinstance(channel, discord.TextChannel):
                        embed = criar_embed_mensagem(self.titulo, self.conteudo, self.cor)
                        await channel.send(embed=embed)
                        sucesso += 1
                    else:
                        falhas += 1
                except:
                    falhas += 1
            
            await interaction.followup.send(
                f"✅ Mensagem enviada para {sucesso} canal(is)! "
                f"{f'({falhas} falhas)' if falhas > 0 else ''}",
                ephemeral=True
            )

class SelecaoCategoriaView(discord.ui.View):
    """View para selecionar categoria"""
    
    def __init__(self, parent_view: SelecaoCanaisView, categorias: list):
        super().__init__()
        self.parent_view = parent_view
        self.categorias = categorias
        
        # Adicionar botões para cada categoria
        for categoria in categorias[:5]:  # Limitar a 5 categorias
            button = discord.ui.Button(
                label=categoria.name[:20],
                style=discord.ButtonStyle.secondary,
                custom_id=f"categoria_{categoria.id}"
            )
            button.callback = self.categoria_selecionada
            self.add_item(button)
    
    async def categoria_selecionada(self, interaction: discord.Interaction):
        """Quando uma categoria é selecionada"""
        categoria_id = int(interaction.data['custom_id'].split('_')[1])
        categoria = discord.utils.get(self.categorias, id=categoria_id)
        
        if not categoria:
            await interaction.response.send_message("❌ Categoria não encontrada!", ephemeral=True)
            return
        
        # Obter canais da categoria
        canais = [c for c in categoria.channels if isinstance(c, discord.TextChannel)]
        
        if not canais:
            await interaction.response.send_message("❌ Nenhum canal de texto nesta categoria!", ephemeral=True)
            return
        
        # Mostrar seleção de canais
        view = SelecaoCanaisIndividualView(self.parent_view, canais)
        await interaction.response.edit_message(
            content=f"📝 **Selecione canais em {categoria.name}:**",
            view=view
        )

class SelecaoCanaisIndividualView(discord.ui.View):
    """View para selecionar canais individuais"""
    
    def __init__(self, parent_view: SelecaoCanaisView, canais: list):
        super().__init__()
        self.parent_view = parent_view
        self.canais = canais
        
        # Adicionar botões para cada canal
        for canal in canais[:10]:  # Limitar a 10 canais
            button = discord.ui.Button(
                label=f"#{canal.name[:15]}",
                style=discord.ButtonStyle.secondary,
                custom_id=f"canal_{canal.id}"
            )
            button.callback = self.canal_selecionado
            self.add_item(button)
        
        # Botão para selecionar todos
        select_all = discord.ui.Button(
            label="✅ Selecionar Todos",
            style=discord.ButtonStyle.success,
            row=1
        )
        select_all.callback = self.selecionar_todos
        self.add_item(select_all)
        
        # Botão para concluir
        concluir = discord.ui.Button(
            label="🏁 Concluir Seleção",
            style=discord.ButtonStyle.primary,
            row=1
        )
        concluir.callback = self.concluir_selecao
        self.add_item(concluir)
    
    async def canal_selecionado(self, interaction: discord.Interaction):
        """Quando um canal é selecionado"""
        canal_id = int(interaction.data['custom_id'].split('_')[1])
        
        if canal_id in self.parent_view.canais_selecionados:
            self.parent_view.canais_selecionados.remove(canal_id)
            await interaction.response.send_message(f"❌ Canal removido da seleção!", ephemeral=True)
        else:
            self.parent_view.canais_selecionados.append(canal_id)
            await interaction.response.send_message(f"✅ Canal adicionado à seleção!", ephemeral=True)
    
    async def selecionar_todos(self, interaction: discord.Interaction):
        """Seleciona todos os canais"""
        for canal in self.canais:
            if canal.id not in self.parent_view.canais_selecionados:
                self.parent_view.canais_selecionados.append(canal.id)
        
        await interaction.response.send_message(
            f"✅ Todos os {len(self.canais)} canais selecionados!",
            ephemeral=True
        )
    
    async def concluir_selecao(self, interaction: discord.Interaction):
        """Conclui a seleção"""
        if not self.parent_view.canais_selecionados:
            await interaction.response.send_message("❌ Nenhum canal selecionado!", ephemeral=True)
            return
        
        await interaction.response.edit_message(
            content=f"✅ {len(self.parent_view.canais_selecionados)} canal(is) selecionado(s)!",
            view=None
        )

class CanaisFavoritosView(discord.ui.View):
    """View para gerenciar canais favoritos"""
    
    def __init__(self, guild: discord.Guild):
        super().__init__()
        self.guild = guild
        self.guild_id = str(guild.id)
        
    @discord.ui.button(label="➕ Adicionar Favorito", style=discord.ButtonStyle.green, emoji="➕")
    async def adicionar_favorito(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Adiciona canal aos favoritos"""
        # Listar categorias para seleção
        categorias = [c for c in self.guild.categories if c.channels]
        
        if not categorias:
            await interaction.response.send_message("❌ Não há categorias disponíveis!", ephemeral=True)
            return
        
        view = SelecaoCategoriaFavoritos(self.guild_id)
        await interaction.response.send_message(
            "📂 **Selecione uma categoria para escolher canais:**",
            view=view,
            ephemeral=True
        )
    
    @discord.ui.button(label="🗑️ Remover Favoritos", style=discord.ButtonStyle.danger, emoji="🗑️")
    async def remover_favoritos(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Remove canais dos favoritos"""
        favoritos = sistema_mensagens.canais_favoritos.get(self.guild_id, [])
        
        if not favoritos:
            await interaction.response.send_message("❌ Nenhum canal favorito para remover!", ephemeral=True)
            return
        
        view = RemoverFavoritosView(self.guild_id, favoritos)
        await interaction.response.send_message(
            "🗑️ **Selecione canais para remover dos favoritos:**",
            view=view,
            ephemeral=True
        )
    
    @discord.ui.button(label="📋 Listar Favoritos", style=discord.ButtonStyle.primary, emoji="📋")
    async def listar_favoritos(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Lista todos os canais favoritos"""
        favoritos = sistema_mensagens.canais_favoritos.get(self.guild_id, [])
        
        if not favoritos:
            await interaction.response.send_message("❌ Nenhum canal favorito configurado!", ephemeral=True)
            return
        
        embed = discord.Embed(
            title="⭐ **Canais Favoritos**",
            description=f"Total: {len(favoritos)} canais",
            color=discord.Color.gold()
        )
        
        # Agrupar por tipo
        text_channels = [c for c in favoritos if c.get('type') == 'text']
        voice_channels = [c for c in favoritos if c.get('type') == 'voice']
        
        if text_channels:
            embed.add_field(
                name="📝 Canais de Texto",
                value="\n".join([f"• <#{c['id']}> - `{c['name']}`" for c in text_channels]),
                inline=False
            )
        
        if voice_channels:
            embed.add_field(
                name="🎤 Canais de Voz",
                value="\n".join([f"• 🔊 `{c['name']}`" for c in voice_channels]),
                inline=False
            )
        
        embed.set_footer(text="Use os botões acima para gerenciar")
        
        await interaction.response.send_message(embed=embed, ephemeral=True)

class SelecaoCategoriaFavoritos(discord.ui.View):
    """View para selecionar categoria ao adicionar favoritos"""
    
    def __init__(self, guild_id: str):
        super().__init__()
        self.guild_id = guild_id
        
    @discord.ui.select(
        placeholder="📂 Selecione uma categoria...",
        min_values=1,
        max_values=1,
        options=[]  # Será preenchido dinamicamente
    )
    async def select_categoria(self, interaction: discord.Interaction, select: discord.ui.Select):
        """Quando uma categoria é selecionada"""
        categoria_id = int(select.values[0])
        categoria = discord.utils.get(interaction.guild.categories, id=categoria_id)
        
        if not categoria:
            await interaction.response.send_message("❌ Categoria não encontrada!", ephemeral=True)
            return
        
        # Mostrar canais da categoria
        canais = [c for c in categoria.channels if isinstance(c, (discord.TextChannel, discord.VoiceChannel))]
        
        if not canais:
            await interaction.response.send_message("❌ Nenhum canal nesta categoria!", ephemeral=True)
            return
        
        view = AdicionarCanaisFavoritosView(self.guild_id, canais)
        await interaction.response.edit_message(
            content=f"📝 **Selecione canais em {categoria.name}:**",
            view=view
        )
    
    async def on_timeout(self):
        """Quando o view expira"""
        pass
    
    async def setup_options(self, guild: discord.Guild):
        """Configura as opções do select com as categorias do servidor"""
        categorias = [c for c in guild.categories if c.channels][:25]  # Limitar a 25
        
        options = []
        for categoria in categorias:
            option = discord.SelectOption(
                label=categoria.name[:100],
                value=str(categoria.id),
                description=f"{len(categoria.channels)} canais"[:100]
            )
            options.append(option)
        
        self.select_categoria.options = options

class AdicionarCanaisFavoritosView(discord.ui.View):
    """View para adicionar canais específicos aos favoritos"""
    
    def __init__(self, guild_id: str, canais: list):
        super().__init__()
        self.guild_id = guild_id
        self.canais = canais
        
        # Adicionar botões para cada canal
        for i, canal in enumerate(canais[:20]):  # Limitar a 20 canais
            emoji = "📝" if isinstance(canal, discord.TextChannel) else "🎤"
            button = discord.ui.Button(
                label=f"{emoji} {canal.name[:20]}",
                style=discord.ButtonStyle.secondary,
                row=i // 5  # Máximo 5 botões por linha
            )
            button.callback = self.create_callback(canal)
            self.add_item(button)
        
        # Botão para selecionar todos
        select_all = discord.ui.Button(
            label="✅ Selecionar Todos",
            style=discord.ButtonStyle.success,
            row=4
        )
        select_all.callback = self.selecionar_todos
        self.add_item(select_all)
    
    def create_callback(self, canal):
        """Cria uma callback específica para cada canal"""
        async def callback(interaction: discord.Interaction):
            await self.adicionar_canal(interaction, canal)
        return callback
    
    async def adicionar_canal(self, interaction: discord.Interaction, canal):
        """Adiciona um canal aos favoritos"""
        # Inicializar lista se não existir
        if self.guild_id not in sistema_mensagens.canais_favoritos:
            sistema_mensagens.canais_favoritos[self.guild_id] = []
        
        # Verificar se já está na lista
        canal_info = {
            'id': canal.id,
            'name': canal.name,
            'type': str(canal.type)
        }
        
        if canal_info in sistema_mensagens.canais_favoritos[self.guild_id]:
            await interaction.response.send_message(
                f"❌ {canal.mention if isinstance(canal, discord.TextChannel) else f'`{canal.name}`'} já está nos favoritos!",
                ephemeral=True
            )
            return
        
        # Adicionar à lista
        sistema_mensagens.canais_favoritos[self.guild_id].append(canal_info)
        sistema_mensagens.salvar_dados()
        
        tipo = "canal de texto" if isinstance(canal, discord.TextChannel) else "canal de voz"
        await interaction.response.send_message(
            f"✅ {canal.mention if isinstance(canal, discord.TextChannel) else f'`{canal.name}`'} adicionado aos favoritos!",
            ephemeral=True
        )
    
    async def selecionar_todos(self, interaction: discord.Interaction):
        """Seleciona todos os canais"""
        # Inicializar lista se não existir
        if self.guild_id not in sistema_mensagens.canais_favoritos:
            sistema_mensagens.canais_favoritos[self.guild_id] = []
        
        adicionados = 0
        for canal in self.canais:
            canal_info = {
                'id': canal.id,
                'name': canal.name,
                'type': str(canal.type)
            }
            
            if canal_info not in sistema_mensagens.canais_favoritos[self.guild_id]:
                sistema_mensagens.canais_favoritos[self.guild_id].append(canal_info)
                adicionados += 1
        
        if adicionados > 0:
            sistema_mensagens.salvar_dados()
        
        await interaction.response.send_message(
            f"✅ {adicionados} canal(is) adicionado(s) aos favoritos!",
            ephemeral=True
        )

class RemoverFavoritosView(discord.ui.View):
    """View para remover canais dos favoritos"""
    
    def __init__(self, guild_id: str, favoritos: list):
        super().__init__()
        self.guild_id = guild_id
        self.favoritos = favoritos
        
        # Adicionar botões para cada favorito
        for i, fav in enumerate(favoritos[:20]):  # Limitar a 20
            try:
                emoji = "📝" if fav.get('type') == 'text' else "🎤"
                label = f"{emoji} {fav['name'][:20]}"
                
                button = discord.ui.Button(
                    label=label,
                    style=discord.ButtonStyle.danger,
                    row=i // 5
                )
                button.callback = self.create_remove_callback(fav['id'])
                self.add_item(button)
            except:
                continue
        
        # Botão para remover todos
        remove_all = discord.ui.Button(
            label="🗑️ Remover Todos",
            style=discord.ButtonStyle.danger,
            row=4
        )
        remove_all.callback = self.remover_todos
        self.add_item(remove_all)
    
    def create_remove_callback(self, canal_id: int):
        """Cria uma callback para remover um canal específico"""
        async def callback(interaction: discord.Interaction):
            await self.remover_canal(interaction, canal_id)
        return callback
    
    async def remover_canal(self, interaction: discord.Interaction, canal_id: int):
        """Remove um canal dos favoritos"""
        if self.guild_id in sistema_mensagens.canais_favoritos:
            # Filtrar para remover o canal
            novos_favoritos = [f for f in sistema_mensagens.canais_favoritos[self.guild_id] if f['id'] != canal_id]
            sistema_mensagens.canais_favoritos[self.guild_id] = novos_favoritos
            sistema_mensagens.salvar_dados()
            
            await interaction.response.send_message(
                f"✅ Canal removido dos favoritos!",
                ephemeral=True
            )
        else:
            await interaction.response.send_message("❌ Erro: lista de favoritos não encontrada!", ephemeral=True)
    
    async def remover_todos(self, interaction: discord.Interaction):
        """Remove todos os favoritos"""
        if self.guild_id in sistema_mensagens.canais_favoritos:
            sistema_mensagens.canais_favoritos[self.guild_id] = []
            sistema_mensagens.salvar_dados()
            await interaction.response.send_message("✅ Todos os favoritos removidos!", ephemeral=True)
        else:
            await interaction.response.send_message("❌ Nenhum favorito para remover!", ephemeral=True)

# ========== COMANDOS DO BOT ==========

@bot.command(name="painel")
@commands.has_permissions(administrator=True)
async def comando_painel(ctx):
    """Recarrega o painel de mensagens"""
    await ctx.message.delete()
    await configurar_painel(ctx.guild)
    await ctx.send("✅ Painel recarregado!", delete_after=5)

@bot.command(name="templates")
@commands.has_permissions(manage_messages=True)
async def comando_templates(ctx):
    """Lista todos os templates disponíveis"""
    embed = discord.Embed(
        title="📋 **Templates Disponíveis**",
        description=f"Total: {len(sistema_mensagens.templates)} templates",
        color=discord.Color.blue()
    )
    
    for template_id, template in sistema_mensagens.templates.items():
        embed.add_field(
            name=template['nome'],
            value=f"**Variáveis:** {', '.join(template['variaveis'])}\n"
                  f"**ID:** `{template_id}`\n"
                  f"**Cor:** `{template['cor']}`",
            inline=False
        )
    
    embed.set_footer(text="Use o botão 'Usar Template' no painel para usar")
    await ctx.send(embed=embed)

@bot.command(name="agendamentos")
@commands.has_permissions(manage_messages=True)
async def comando_agendamentos(ctx):
    """Lista todas as mensagens agendadas"""
    if not sistema_mensagens.mensagens_agendadas:
        await ctx.send("📭 Nenhuma mensagem agendada no momento!")
        return
    
    embed = discord.Embed(
        title="⏰ **Mensagens Agendadas**",
        description=f"Total: {len(sistema_mensagens.mensagens_agendadas)} agendamento(s)",
        color=discord.Color.orange()
    )
    
    for msg_id, agendamento in sistema_mensagens.mensagens_agendadas.items():
        try:
            # Formatar informações
            hora_envio = datetime.fromisoformat(agendamento['hora_envio'])
            time_str = hora_envio.strftime("%d/%m/%Y %H:%M")
            time_left = hora_envio - datetime.now()
            
            if time_left.total_seconds() > 0:
                status = f"⏳ Envia em {time_left}"
            else:
                status = "🔄 Processando..."
            
            # Contar canais
            num_canais = len(agendamento.get('canais', []))
            
            embed.add_field(
                name=f"📅 {agendamento['titulo'][:50]}",
                value=f"**Quando:** {time_str}\n"
                      f"**Status:** {status}\n"
                      f"**Canais:** {num_canais} canal(is)\n"
                      f"**ID:** `{msg_id[:10]}...`",
                inline=False
            )
        except:
            continue
    
    embed.set_footer(text="As mensagens são enviadas automaticamente")
    await ctx.send(embed=embed)

@bot.command(name="cancelaragendamento")
@commands.has_permissions(manage_messages=True)
async def comando_cancelar_agendamento(ctx, msg_id: str = None):
    """Cancela uma mensagem agendada"""
    if not msg_id:
        # Mostrar lista de agendamentos
        if sistema_mensagens.mensagens_agendadas:
            embed = discord.Embed(
                title="🗑️ **Cancelar Agendamento**",
                description="Selecione o ID do agendamento para cancelar:",
                color=discord.Color.red()
            )
            
            for msg_id, agendamento in sistema_mensagens.mensagens_agendadas.items():
                hora_envio = datetime.fromisoformat(agendamento['hora_envio'])
                embed.add_field(
                    name=agendamento['titulo'][:50],
                    value=f"**ID:** `{msg_id}`\n"
                          f"**Data:** {hora_envio.strftime('%d/%m/%Y %H:%M')}",
                    inline=False
                )
            
            embed.set_footer(text="Use !cancelaragendamento <id> para cancelar")
            await ctx.send(embed=embed)
        else:
            await ctx.send("📭 Nenhuma mensagem agendada para cancelar!")
        return
    
    # Cancelar agendamento específico
    if msg_id in sistema_mensagens.mensagens_agendadas:
        titulo = sistema_mensagens.mensagens_agendadas[msg_id]['titulo']
        del sistema_mensagens.mensagens_agendadas[msg_id]
        sistema_mensagens.salvar_dados()
        
        await ctx.send(f"✅ Agendamento cancelado: **{titulo}**")
    else:
        await ctx.send(f"❌ Agendamento com ID `{msg_id}` não encontrado!")

@bot.command(name="canaisfavoritos")
@commands.has_permissions(manage_messages=True)
async def comando_canais_favoritos(ctx):
    """Mostra os canais favoritos"""
    guild_id = str(ctx.guild.id)
    favoritos = sistema_mensagens.canais_favoritos.get(guild_id, [])
    
    if not favoritos:
        await ctx.send("⭐ Nenhum canal favorito configurado!")
        return
    
    # Criar embed com categorias separadas
    embed = discord.Embed(
        title="⭐ **Canais Favoritos do Servidor**",
        color=discord.Color.gold()
    )
    
    # Separar por tipo
    canais_texto = []
    canais_voz = []
    
    for fav in favoritos:
        if fav.get('type') == 'text':
            canais_texto.append(f"• <#{fav['id']}> - `{fav['name']}`")
        elif fav.get('type') == 'voice':
            canais_voz.append(f"• 🔊 `{fav['name']}`")
    
    if canais_texto:
        embed.add_field(
            name="📝 Canais de Texto",
            value="\n".join(canais_texto[:20]),  # Limitar a 20
            inline=False
        )
    
    if canais_voz:
        embed.add_field(
            name="🎤 Canais de Voz",
            value="\n".join(canais_voz[:10]),  # Limitar a 10
            inline=False
        )
    
    embed.set_footer(text=f"Total: {len(favoritos)} canais")
    await ctx.send(embed=embed)

@bot.command(name="criartemplate")
@commands.has_permissions(administrator=True)
async def comando_criar_template(ctx):
    """Cria um novo template"""
    await ctx.send("🛠️ **Criação de Template**\n"
                   "Para criar um template, use o formato:\n"
                   "```\n"
                   "!novotemplate <id> <nome> <cor> <variáveis>\n"
                   "Exemplo:\n"
                   "!novotemplate promocao \"🎯 Promoção\" #FF5733 titulo,descricao,validade\n"
                   "```\n"
                   "Depois use `!edtemplate <id>` para configurar o conteúdo.")

@bot.command(name="novotemplate")
@commands.has_permissions(administrator=True)
async def comando_novo_template(ctx, template_id: str, nome: str, cor: str, variaveis: str):
    """Cria um novo template"""
    # Verificar se template já existe
    if template_id in sistema_mensagens.templates:
        await ctx.send(f"❌ Template com ID `{template_id}` já existe!")
        return
    
    # Processar variáveis
    variaveis_lista = [v.strip() for v in variaveis.split(',')]
    
    # Criar template
    sistema_mensagens.templates[template_id] = {
        'nome': nome,
        'conteudo': f"**{{{variaveis_lista[0] if variaveis_lista else 'titulo'}}}**\n\n" +
                   "\n".join([f"{{{{{v}}}}}" for v in variaveis_lista[1:]]),
        'cor': cor,
        'variaveis': variaveis_lista
    }
    
    sistema_mensagens.salvar_dados()
    
    embed = discord.Embed(
        title="✅ Template Criado!",
        description=f"**{nome}** foi criado com sucesso.",
        color=discord.Color.green()
    )
    embed.add_field(name="ID", value=f"`{template_id}`", inline=True)
    embed.add_field(name="Cor", value=f"`{cor}`", inline=True)
    embed.add_field(name="Variáveis", value=f"{len(variaveis_lista)} variáveis", inline=True)
    embed.set_footer(text="Use !edtemplate <id> para editar o conteúdo")
    
    await ctx.send(embed=embed)

@bot.command(name="edtemplate")
@commands.has_permissions(administrator=True)
async def comando_editar_template(ctx, template_id: str):
    """Edita o conteúdo de um template"""
    if template_id not in sistema_mensagens.templates:
        await ctx.send(f"❌ Template `{template_id}` não encontrado!")
        return
    
    template = sistema_mensagens.templates[template_id]
    
    # Enviar modal para edição
    class ModalEditarTemplate(discord.ui.Modal, title=f"✏️ Editando: {template['nome']}"):
        conteudo = discord.ui.TextInput(
            label="Novo conteúdo do template:",
            style=discord.TextStyle.paragraph,
            default=template['conteudo'],
            required=True,
            max_length=2000
        )
        
        async def on_submit(self, interaction: discord.Interaction):
            # Atualizar template
            sistema_mensagens.templates[template_id]['conteudo'] = self.conteudo.value
            sistema_mensagens.salvar_dados()
            
            await interaction.response.send_message(
                f"✅ Template **{template['nome']}** atualizado!",
                ephemeral=True
            )
    
    modal = ModalEditarTemplate()
    await ctx.send(f"📝 Editando template **{template['nome']}**...")
    await ctx.author.send("✏️ **Editar Template**", view=None)  # Abre modal via DM
    # Nota: Modals precisam ser usados em interações, então vamos usar um método alternativo
    await ctx.send("⚠️ Para editar o template, use o painel web ou edite manualmente o arquivo `mensagens_data.json`")

@bot.command(name="deletetemplate")
@commands.has_permissions(administrator=True)
async def comando_deletar_template(ctx, template_id: str):
    """Deleta um template"""
    if template_id not in sistema_mensagens.templates:
        await ctx.send(f"❌ Template `{template_id}` não encontrado!")
        return
    
    nome = sistema_mensagens.templates[template_id]['nome']
    del sistema_mensagens.templates[template_id]
    sistema_mensagens.salvar_dados()
    
    await ctx.send(f"🗑️ Template **{nome}** deletado com sucesso!")

@bot.command(name="ping")
async def comando_ping(ctx):
    """Verifica se o bot está online"""
    latency = round(bot.latency * 1000)
    
    embed = discord.Embed(
        title="🤖 Bot Avançado - Online!",
        description="Sistema de Cargo Automático + Painel de Mensagens",
        color=discord.Color.green()
    )
    embed.add_field(name="📡 Ping", value=f"{latency}ms", inline=True)
    embed.add_field(name="🏠 Servidores", value=f"{len(bot.guilds)}", inline=True)
    embed.add_field(name="📊 Templates", value=f"{len(sistema_mensagens.templates)}", inline=True)
    embed.add_field(name="⏰ Agendamentos", value=f"{len(sistema_mensagens.mensagens_agendadas)}", inline=True)
    embed.set_footer(text="Funcionando 24/7 com UptimeRobot")
    
    await ctx.send(embed=embed)

@bot.command(name="ajuda")
async def comando_ajuda(ctx):
    """Mostra ajuda completa do bot"""
    embed = discord.Embed(
        title="📚 **Ajuda - Bot Avançado**",
        description="Sistema completo de gerenciamento de servidor",
        color=discord.Color.purple()
    )
    
    embed.add_field(
        name="🎯 **Funcionalidades Principais**",
        value=(
            "1. **Cargo Automático** - Atribui '𝗩𝗶𝘀𝗶𝘁𝗮𝗻𝘁𝗲' a novos membros\n"
            "2. **Painel de Mensagens** - Interface completa no canal `𝗪𝗮𝘃𝗲𝗫-𝗣𝗡𝗘𝗟_𝗠𝗦𝗚`\n"
            "3. **Templates** - Modelos com variáveis para mensagens\n"
            "4. **Agendamento** - Envie mensagens automaticamente\n"
            "5. **Multi-canal** - Envie para vários canais de uma vez\n"
            "6. **Pré-visualização** - Veja como ficará antes de enviar"
        ),
        inline=False
    )
    
    embed.add_field(
        name="📋 **Comandos do Bot**",
        value=(
            "• `!ping` - Status do bot\n"
            "• `!painel` - Recarrega o painel (admin)\n"
            "• `!templates` - Lista todos templates\n"
            "• `!agendamentos` - Lista mensagens agendadas\n"
            "• `!canaisfavoritos` - Mostra canais favoritos\n"
            "• `!cancelaragendamento` - Cancela um agendamento\n"
            "• `!criartemplate` - Ajuda para criar templates\n"
            "• `!novotemplate` - Cria novo template (admin)\n"
            "• `!ajuda` - Esta mensagem"
        ),
        inline=False
    )
    
    embed.add_field(
        name="⚙️ **Configuração**",
        value=(
            "1. Crie o canal `𝗪𝗮𝘃𝗲𝗫-𝗣𝗡𝗘𝗟_𝗠𝗦𝗚`\n"
            "2. Use `!painel` para configurar\n"
            "3. Dê permissões de administrador ou:\n"
            "   • Gerenciar Mensagens\n"
            "   • Gerenciar Canais\n"
            "   • Gerenciar Cargos"
        ),
        inline=False
    )
    
    embed.set_footer(text="Bot Online 24/7 • Hospedado no Render")
    await ctx.send(embed=embed)

# ========== FUNÇÕES AUXILIARES ADICIONAIS ==========

async def atualizar_select_categorias(interaction: discord.Interaction):
    """Atualiza dinamicamente as opções do select de categorias"""
    # Esta função será usada para views que precisam de selects dinâmicos
    pass

# ========== INICIAR BOT ==========

@bot.event
async def on_guild_join(guild):
    """Quando o bot é adicionado a um novo servidor"""
    print(f"\n{'='*50}")
    print(f"🏠 BOT ADICIONADO AO SERVIDOR:")
    print(f"   Nome: {guild.name}")
    print(f"   ID: {guild.id}")
    print(f"   Membros: {guild.member_count}")
    print(f"{'='*50}")
    
    # Configurar painel automaticamente
    await configurar_painel(guild)
    
    # Enviar mensagem de boas-vindas no canal geral
    try:
        # Procurar canal adequado
        canais_tentativa = ["geral", "chat", "bem-vindo", "welcome", "lounge"]
        canal_encontrado = None
        
        for nome_canal in canais_tentativa:
            canal = discord.utils.get(guild.text_channels, name=nome_canal)
            if canal and canal.permissions_for(guild.me).send_messages:
                canal_encontrado = canal
                break
        
        if not canal_encontrado:
            # Usar primeiro canal com permissão
            for canal in guild.text_channels:
                if canal.permissions_for(guild.me).send_messages:
                    canal_encontrado = canal
                    break
        
        if canal_encontrado:
            embed = discord.Embed(
                title="🤖 Bot Avançado - Configurado!",
                description=(
                    "Olá! Sou um bot com **duas funcionalidades principais:**\n\n"
                    "🎯 **1. Sistema de Cargo Automático**\n"
                    "• Atribui cargo `𝗩𝗶𝘀𝗶𝘁𝗮𝗻𝘁𝗲` automaticamente a novos membros\n"
                    "• Cria o cargo se não existir\n\n"
                    "📢 **2. Painel de Mensagens Avançado**\n"
                    "• Sistema completo no canal `𝗪𝗮𝘃𝗲𝗫-𝗣𝗡𝗘𝗟_𝗠𝗦𝗚`\n"
                    "• Templates, agendamento, multi-canal\n"
                    "• Pré-visualização antes de enviar\n\n"
                    "🔧 **Configuração automática:**\n"
                    "• Painel configurado automaticamente\n"
                    "• Canais novos são detectados automaticamente"
                ),
                color=discord.Color.blue()
            )
            
            embed.add_field(
                name="⚡ Comandos Rápidos",
                value="• `!painel` - Configura/recarrega o painel\n• `!ajuda` - Ajuda completa\n• `!ping` - Verifica status",
                inline=False
            )
            
            embed.set_footer(text="Bot Online 24/7 • Desenvolvido para a WaveX")
            await canal_encontrado.send(embed=embed)
            
    except Exception as e:
        print(f"⚠️ Erro ao enviar mensagem de boas-vindas: {e}")

if __name__ == "__main__":
    # OBTER TOKEN DO BOT
    TOKEN = os.getenv("DISCORD_TOKEN")
    
    if not TOKEN:
        try:
            with open(".env", "r") as f:
                for line in f:
                    if line.startswith("DISCORD_TOKEN="):
                        TOKEN = line.split("=")[1].strip()
                        break
        except:
            pass
    
    if not TOKEN:
        print("❌ ERRO: DISCORD_TOKEN não encontrado!")
        print("\n💡 COMO CONFIGURAR:")
        print("1. No Render, adicione a variável de ambiente:")
        print("   DISCORD_TOKEN=seu_token_do_bot_aqui")
        print("\n2. Configure as intents no Discord Dev Portal:")
        print("   - SERVER MEMBERS INTENT (OBRIGATÓRIO)")
        print("   - MESSAGE CONTENT INTENT (para comandos)")
        print("\n🔗 https://discord.com/developers/applications")
        sys.exit(1)
    
    print("✅ Token encontrado")
    print("🔗 Conectando ao Discord...")
    print("=" * 60)
    
    try:
        bot.run(TOKEN)
    except discord.LoginFailure:
        print("❌ ERRO: Token inválido!")
    except KeyboardInterrupt:
        print("\n👋 Bot encerrado manualmente")
    except Exception as e:
        print(f"❌ ERRO: {type(e).__name__}: {e}")
