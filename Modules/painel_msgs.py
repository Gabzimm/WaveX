import discord
from discord import ui
from discord.ext import commands

class PainelView(ui.View):
    def __init__(self, bot):
        super().__init__(timeout=None)
        self.bot = bot
    
    @ui.button(label="📋 Recarregar Painel", style=discord.ButtonStyle.primary, custom_id="recarregar_painel")
    async def recarregar_painel(self, interaction: discord.Interaction, button: ui.Button):
        # Deleta a mensagem do painel antigo
        await interaction.message.delete()
        
        # Cria um novo painel
        embed = await PainelManager.criar_painel_embed()
        await interaction.channel.send(embed=embed, view=PainelView(self.bot))
        
        # Confirma que foi recarregado (mensagem privada)
        await interaction.response.send_message("✅ Painel recarregado com sucesso!", ephemeral=True)

class AgendamentoView(ui.View):
    def __init__(self):
        super().__init__(timeout=None)
    
    @ui.button(label="📅 Novo Agendamento", style=discord.ButtonStyle.success, custom_id="novo_agendamento")
    async def novo_agendamento(self, interaction: discord.Interaction, button: ui.Button):
        modal = AgendamentoModal()
        await interaction.response.send_modal(modal)
    
    @ui.button(label="❌ Fechar", style=discord.ButtonStyle.danger, custom_id="fechar_agendamento")
    async def fechar_agendamento(self, interaction: discord.Interaction, button: ui.Button):
        # Deleta a mensagem do painel de agendamento
        await interaction.message.delete()
        await interaction.response.send_message("✅ Painel de agendamentos fechado!", ephemeral=True)

class AgendamentoModal(ui.Modal, title="📅 Novo Agendamento"):
    data = ui.TextInput(label="Data", placeholder="DD/MM/AAAA", required=True, max_length=10)
    horario = ui.TextInput(label="Horário", placeholder="HH:MM", required=True, max_length=5)
    descricao = ui.TextInput(label="Descrição", placeholder="Breve descrição do agendamento...", 
                             style=discord.TextStyle.paragraph, required=True, max_length=200)
    
    async def on_submit(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="✅ Agendamento Criado",
            color=discord.Color.green(),
            timestamp=interaction.created_at
        )
        embed.add_field(name="📅 Data", value=self.data.value, inline=True)
        embed.add_field(name="🕒 Horário", value=self.horario.value, inline=True)
        embed.add_field(name="📝 Descrição", value=self.descricao.value, inline=False)
        embed.set_footer(text=f"Agendado por: {interaction.user.display_name}")
        
        # Envia para o usuário que criou (privado)
        await interaction.response.send_message(embed=embed, ephemeral=True)
        
        # Também envia para um canal de logs (opcional)
        # await interaction.channel.send(f"📅 Novo agendamento criado por {interaction.user.mention}")

class PainelManager:
    @staticmethod
    async def criar_painel_embed():
        embed = discord.Embed(
            title="📊 PAINEL DE CONTROLE",
            description="Bem-vindo ao painel de controle do servidor!",
            color=discord.Color.blue()
        )
        
        embed.add_field(
            name="📋 Comandos Disponíveis",
            value="• `!painel` - Mostra este painel\n• `!agendamentos` - Abre painel de agendamentos\n• `!ping` - Testa a latência",
            inline=False
        )
        
        embed.add_field(
            name="⚙️ Estatísticas",
            value="• Use os botões abaixo para interagir\n• Clique em 'Recarregar' para atualizar",
            inline=False
        )
        
        embed.add_field(
            name="📅 Agendamentos",
            value="Para criar agendamentos, use `!agendamentos`",
            inline=False
        )
        
        embed.set_footer(text="Painel atualizado • Clique nos botões para interagir")
        
        return embed
    
    @staticmethod
    async def criar_agendamento_embed():
        embed = discord.Embed(
            title="📅 PAINEL DE AGENDAMENTOS",
            description="Gerencie seus agendamentos aqui.\n**Este painel é visível apenas para você.**",
            color=discord.Color.purple()
        )
        
        embed.add_field(
            name="📝 Como usar",
            value="• Clique em 'Novo Agendamento' para criar\n• Preencha o formulário que aparecerá\n• Seus agendamentos serão privados",
            inline=False
        )
        
        embed.add_field(
            name="🔧 Ações",
            value="Use os botões abaixo para interagir com o painel",
            inline=False
        )
        
        embed.set_footer(text="Painel privado • Seus dados são confidenciais")
        
        return embed
