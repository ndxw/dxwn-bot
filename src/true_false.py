import discord
from discord.ui import View, Button

class TFView(View):

    q = None
    author = None

    def __init__(self, q, author):
        super().__init__()

        self.q = q
        self.author = author

        #create button objects
        self.add_item(TFButton(label='True', style=discord.ButtonStyle.green))
        self.add_item(TFButton(label='False', style=discord.ButtonStyle.red))

##############################################################################################
##############################################################################################

class TFButton(Button):

    async def callback(self, interaction):

        #only command invoker can interact with TF questions
        if interaction.user == self.view.author:

            embed = discord.Embed(color=interaction.client.PINK, title='Trivia', description=f"{self.view.q['results'][0]['question']}")

            if self.view.q['results'][0]['correct_answer'] == self.label:
                embed.add_field(name='✅ Correct!', value='')
                await interaction.response.edit_message(embed=embed, view=None)

            else:
                embed.add_field(name='❌ Incorrect...',
                                value=f"The correct answer is {self.view.q['results'][0]['correct_answer']}")
                await interaction.response.edit_message(embed=embed, view=None)






