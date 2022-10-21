from TFButton import TFButton
from discord.ui import View
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



