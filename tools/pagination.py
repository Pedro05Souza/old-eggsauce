import discord

class PaginationView(discord.ui.View):


    def __init__(self, data, sep : int = 5, thumbnail = None):
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
        self.total_pages= len(self.data) // self.sep + (len(self.data) % self.sep > 0)
        self.thumbnail = thumbnail

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
        """Creates the embed with the data provided."""
        embed = discord.Embed(title=f"{self.title} {self.current_page} / {self.total_pages}", description=self.description, color=self.color)
        for item in data:
            embed.add_field(name=item['title'], value=item['value'], inline=False)
        if self.thumbnail:
            embed.set_thumbnail(url=self.thumbnail)
        return embed

    async def update_message(self, data):
        """Update the message with the new data."""
        self.update_buttons()
        await self.message.edit(embed=self.create_embed(data), view=self)

    def update_buttons(self):
        """Update the buttons according to the"""
        is_first_page = self.current_page == 1
        is_last_page = self.current_page == self.total_pages

        self.first_page_button.disabled = is_first_page
        self.prev_button.disabled = is_first_page
        self.next_button.disabled = is_last_page
        self.last_page_button.disabled = is_last_page 

    def get_current_page_data(self):
        """Get the data of the current page."""
        start = (self.current_page - 1) * self.sep
        end = start + self.sep if self.current_page != self.total_pages else None
        return self.data[start:end]

    @discord.ui.button(label='First page', style=discord.ButtonStyle.green)
    async def first_page_button(self, button: discord.ui.Button, interaction: discord.Interaction):
        """Go to the first page."""
        self.current_page = 1
        await self.update_message(self.get_current_page_data())

    @discord.ui.button(label='Previous page', style=discord.ButtonStyle.primary)
    async def prev_button(self, button: discord.ui.Button, interaction: discord.Interaction):
        """Go to the previous page."""
        self.current_page -= 1
        await self.update_message(self.get_current_page_data())

    @discord.ui.button(label='Next page', style=discord.ButtonStyle.primary)
    async def next_button(self, button: discord.ui.Button, interaction: discord.Interaction):
        """Go to the next page."""
        self.current_page += 1
        await self.update_message(self.get_current_page_data())

    @discord.ui.button(label='Last page', style=discord.ButtonStyle.green)
    async def last_page_button(self, button: discord.ui.Button, interaction: discord.Interaction):
        """Go to the last page."""
        self.current_page = self.total_pages
        await self.update_message(self.get_current_page_data())