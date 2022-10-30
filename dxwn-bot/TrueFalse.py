from discord.ui import View, Button
from discord import ButtonStyle

class TFView(View):

    q = None
    author = None

    def __init__(self, q, author):
        super().__init__()

        self.q = q
        self.author = author

        #create button objects
        self.add_item(TFButton(label='True', style=ButtonStyle.green))
        self.add_item(TFButton(label='False', style=ButtonStyle.red))

##############################################################################################
##############################################################################################

class TFButton(Button):

    async def callback(self, interaction):

        #only command invoker can interact with TF questions
        if interaction.user == self.view.author:

            if self.view.q['results'][0]['correct_answer'] == self.label:
                await interaction.response.edit_message(
                    content=f"{self.view.q['results'][0]['question']}\n\n**Correct!**", view=None)

            else:
                await interaction.response.edit_message(
                    content=f"{self.view.q['results'][0]['question']}\n\n**Incorrect...the correct answer is {self.view.q['results'][0]['correct_answer']}**", view=None)






