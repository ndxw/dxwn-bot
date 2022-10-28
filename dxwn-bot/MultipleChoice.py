import random

from discord.ui import View, Button
from discord import ButtonStyle
from math import floor

class MCView(View):

    q = None
    author = None

    def __init__(self, q, author):
        super().__init__()

        self.q = q
        self.author = author

        #randomize answers
        answers = q['results'][0]['incorrect_answers']
        answers.append(q['results'][0]['correct_answer'])
        random.shuffle(answers)

        #create button objects
        for i, answer in enumerate(answers):                            
            self.add_item(MCButton(label=answer, style=ButtonStyle.gray, row=floor(i/2)))  #buttons in two columns (2x2)

##############################################################################################
##############################################################################################

class MCButton(Button):

    async def callback(self, interaction):

        #only command invoker can interact with MC questions
        if interaction.user == self.view.author: 

            if self.view.q['results'][0]['correct_answer'] == self.label:
                self.style = ButtonStyle.green
                await interaction.response.edit_message(content=f"{self.view.q['results'][0]['question']}\n\n**Correct!**", view=self.view)
                self.view.stop()

            else:
                self.style = ButtonStyle.red
                for item in self.view.children:
                    if item.label == self.view.q['results'][0]['correct_answer']:
                        item.style = ButtonStyle.green

                await interaction.response.edit_message(content=f"{self.view.q['results'][0]['question']}\n\n**Incorrect...**", view=self.view)
                self.view.stop()





