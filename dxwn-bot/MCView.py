import random

from MCButton import MCButton
from discord.ui import View
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



