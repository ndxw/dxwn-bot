from discord.ui import Button
from discord import ButtonStyle

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



