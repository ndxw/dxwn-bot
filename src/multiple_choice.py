import random
from math import floor

import discord
from discord.ui import View, Button

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
        for answer in answers:                            
            self.add_item(MCButton(label=answer, style=discord.ButtonStyle.gray))  #buttons in two columns (2x2)

##############################################################################################
##############################################################################################

class MCButton(Button):

    async def callback(self, interaction):

        #only command invoker can interact with MC questions
        if interaction.user == self.view.author: 

            embed = discord.Embed(color=interaction.client.PINK, title='Trivia', description=f"{self.view.q['results'][0]['question']}")

            if self.view.q['results'][0]['correct_answer'] == self.label:
                self.style = discord.ButtonStyle.green
                embed.add_field(name='✅ Correct!', value='')
                await interaction.response.edit_message(embed=embed, view=self.view)
                self.view.stop()

            else:
                self.style = discord.ButtonStyle.red
                for item in self.view.children:
                    if item.label == self.view.q['results'][0]['correct_answer']:
                        item.style = discord.ButtonStyle.green

                embed.add_field(name='❌ Incorrect...', value='')
                await interaction.response.edit_message(embed=embed, view=self.view)
                self.view.stop()





