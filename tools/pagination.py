import discord
from discord.ext import commands

class PaginationView(discord.ui.View):


    def __init__(self, data, sep : int = 5):
        """
        PaginationView constructor
        param - data: dictionary with ["title"]:["value"]
        param - sep: amount of data per page (Default = 5)
        """
        super().__init__()
        self.current_page = 1
        self.sep = sep
        self.data = data
        self.title = "List Page:"
        self.description = None
        self.color = discord.Color.default()

    async def send(self, ctx, title= "List Page:", description=None, color=discord.Color.default()):
        """
        Send the embed to the context
        param - ctx: context of the message (bot)
        param - title: title of the embed (Default = "List Page:")
        param - description: description of the embed (Default = None)
        param - color: color of the embed (Default = discord.Color.default() #gray)
        """
        self.title = title
        self.description = description
        self.color = color
        self.message = await ctx.send(view=self)
        await self.update_message(self.data[:self.sep])
    
    def create_embed(self, data):
        embed = discord.Embed(title=f"{self.title} {self.current_page} / {int(len(self.data) / self.sep) + 1}", description=self.description, color=self.color)
        for item in data:
            embed.add_field(name=item['title'], value=item['value'], inline=False)
        return embed

    async def update_message(self, data):
        self.update_buttons()
        await self.message.edit(embed=self.create_embed(data), view=self)

    def update_buttons(self):
        if self.current_page == 1:
            self.first_page_button.disabled = True
            self.prev_button.disabled = True
            self.first_page_button.style = discord.ButtonStyle.gray
            self.prev_button.style = discord.ButtonStyle.gray
        else:
            self.first_page_button.disabled = False
            self.prev_button.disabled = False
            self.first_page_button.style = discord.ButtonStyle.green
            self.prev_button.style = discord.ButtonStyle.primary

        if self.current_page == int(len(self.data) / self.sep) + 1:
            self.next_button.disabled = True
            self.last_page_button.disabled = True
            self.last_page_button.style = discord.ButtonStyle.gray
            self.next_button.style = discord.ButtonStyle.gray
        else:
            self.next_button.disabled = False
            self.last_page_button.disabled = False
            self.last_page_button.style = discord.ButtonStyle.green
            self.next_button.style = discord.ButtonStyle.primary

    def get_current_page_data(self):
        until_item = self.current_page * self.sep
        from_item = until_item - self.sep
        if not self.current_page == 1:
            from_item = 0
            until_item = self.sep
        if self.current_page == int(len(self.data) / self.sep) + 1:
            from_item = self.current_page * self.sep - self.sep
            until_item = len(self.data)
        return self.data[from_item:until_item]

    @discord.ui.button(label='Primeira página', style=discord.ButtonStyle.green)
    async def first_page_button(self, button: discord.ui.Button, interaction: discord.Interaction):
        self.current_page = 1
        await self.update_message(self.data[:self.sep])

    @discord.ui.button(label='Página anterior', style=discord.ButtonStyle.primary)
    async def prev_button(self, button: discord.ui.Button, interaction: discord.Interaction):
        self.current_page -= 1
        start = (self.current_page - 1) * self.sep
        end = start + self.sep
        await self.update_message(self.data[start:end])

    @discord.ui.button(label='Próxima página', style=discord.ButtonStyle.primary)
    async def next_button(self, button: discord.ui.Button, interaction: discord.Interaction):
        self.current_page += 1
        start = (self.current_page - 1) * self.sep
        end = start + self.sep
        await self.update_message(self.data[start:end])

    @discord.ui.button(label='Última página', style=discord.ButtonStyle.green)
    async def last_page_button(self, button: discord.ui.Button, interaction: discord.Interaction):
        self.current_page = int(len(self.data) / self.sep) + 1
        start = (self.current_page - 1) * self.sep
        await self.update_message(self.data[start:])


    
