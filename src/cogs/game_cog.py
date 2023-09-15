import re
import aiohttp
import html
import logging

import discord
from discord.ext import commands
from true_false import TFView
from multiple_choice import MCView

import sudoku


logfile = './log/dxwn.log'
fmt = '[%(levelname)s] %(asctime)s - %(message)s'

logging.basicConfig(filename = logfile, filemode = 'w', format = fmt, level = logging.DEBUG)

class game_cog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # contains ongoing sudoku games, each user can only have one ongoing game
        self.sudoku_games = {}

    def generate_board(self, board):

        if len(board) == len(board[0]):
            pass

        board_str = ''
        x_axis          = '    A   B   C   D   E   F   G   H   I  \n'
        border_top      = '  ┏━━━┯━━━┯━━━┳━━━┯━━━┯━━━┳━━━┯━━━┯━━━┓\n'
        border_thin     = '  ┠───┼───┼───╂───┼───┼───╂───┼───┼───┨\n'
        border_thick    = '  ┣━━━┿━━━┿━━━╋━━━┿━━━┿━━━╋━━━┿━━━┿━━━┫\n'
        border_bottom   = '  ┗━━━┷━━━┷━━━┻━━━┷━━━┷━━━┻━━━┷━━━┷━━━┛'

        for i, row in enumerate(board):
            if i == 0:
                board_str += x_axis + border_top
            elif i % 3 == 0:
                board_str += border_thick
            else:
                board_str += border_thin

            for j, column in enumerate(row):
                if column == None:
                    column = ' '
                if j == 0:
                    board_str += f'{i+1} ┃ {str(column)} '
                elif j % 3 == 0:
                    board_str += f'┃ {str(column)} '
                else:
                    board_str += f'│ {str(column)} '
            board_str += '┃\n'
        return board_str + border_bottom

    @commands.command()
    async def trivia(self, ctx, category=''):

        categories = {
            'general':'&category=9',
            'books':'&category=10',
            'film':'&category=11',
            'music':'&category=12',
            'theatre':'&category=13',
            'tv':'&category=14',
            'video_games':'&category=15',
            'board_games':'&category=16',
            'nature':'&category=17',
            'computers':'&category=18',
            'math':'&category=19',
            'myths':'&category=20',
            'sports':'&category=21',
            'geography':'&category=22',
            'history':'&category=23',
            'politics':'&category=24',
            'art':'&category=25',
            'celebrities':'&category=26',
            'animals':'&category=27',
            'vehicles':'&category=28',
            'comics':'&category=29',
            'tech':'&category=30',
            'anime':'&category=31',
            'cartoons':'&category=32',
            }
    
        if category != '':
            category = categories[category]

        async with aiohttp.ClientSession() as session:
            async with session.get(f"https://opentdb.com/api.php?amount=1{category}") as q:
        
                if q.status == 200:
                    q = await q.json()

                else:
                    q = None
                    #logging.warning(f'OpenTDB request status {q.status}')
                    del_msg = await ctx.send('mb bro no trivia this time :pensive:')
                    return await del_msg.delete(delay=5)
        
                if q['response_code'] != 0:
                    #logging.warning(f'OpenTDB bad result code {q["response_code"]}')
                    del_msg = await ctx.send('No results')
                    return await del_msg.delete(delay=5)

                q['results'][0]['question'] = html.unescape(q['results'][0]['question']) #fix bad decoding
                q['results'][0]['correct_answer'] = html.unescape(q['results'][0]['correct_answer'])
                for i, answer in enumerate(q['results'][0]['incorrect_answers']):
                    q['results'][0]['incorrect_answers'][i] = html.unescape(answer)

                if q['results'][0]['type'] == 'boolean': #True or False
                    view = TFView(q, ctx.author)
                elif q['results'][0]['type'] == 'multiple': #Multiple Choice
                    view = MCView(q, ctx.author)
                    
                embed = discord.Embed(color=self.bot.PINK, title='Trivia', description=f'{q["results"][0]["question"]}')
                await ctx.send(embed=embed, view=view)

    @commands.command(aliases=['sdk'])
    async def sudoku(self, ctx, difficulty='medium'):
        """ Gives a sudoku puzzle of one of four difficulties. """

        # Percentage of empty squares:
        difficulties = {'easy': 0.5, 'medium': 0.6, 'hard': 0.65, 'expert': 0.7}
        num_empty = {'easy': 40, 'medium': 48, 'hard': 52, 'expert': 56}

        embed = discord.Embed(color=self.bot.PINK, title='Sudoku', description=f'<@{ctx.author.id}>\'s game')

        if difficulty == 'ff':
            try:
                puzzle = self.sudoku_games[str(ctx.author.id)][0]
            except KeyError:
                return await ctx.send('You haven\'t started a game yet!')
            
            embed.add_field(name='<:pain:893590495773728818> Womp womp... <:pain:893590495773728818>', 
                            value=f'```{self.generate_board(board=puzzle.solve().board)}```')
            self.sudoku_games.pop(str(ctx.author.id))
            return await ctx.send(embed=embed)
        
        if difficulty == 'reset':
            try:
                self.sudoku_games[str(ctx.author.id)][0] = self.sudoku_games[str(ctx.author.id)][1]
                puzzle = self.sudoku_games[str(ctx.author.id)][0]
                status = 'Game reset!'
            except KeyError:
                return await ctx.send('You haven\'t started a game yet!')
            
        elif difficulty in difficulties:
            # only start a new game if user doesn't have an ongoing game
            if not str(ctx.author.id) in self.sudoku_games:
                puzzle = sudoku.Sudoku(3).difficulty(difficulties[difficulty])
                original_puzzle = sudoku.Sudoku(3, 3, board=puzzle.board)
                self.sudoku_games[str(ctx.author.id)] = [puzzle, original_puzzle, puzzle.solve(), num_empty[difficulty]]
                status = ''
            else:
                return await ctx.send('You already have an ongoing game!')
        else:
            return await ctx.send('Gimme a valid difficulty!')
        
        embed.add_field(name=status, value=f'```{self.generate_board(board=puzzle.board)}```')

        await ctx.send(embed=embed)
    
    @commands.command(aliases=['sdkp'])
    async def sudokuplay(self, ctx, square='z0', number:int=0):
        """ Make a move towards completing the sudoku. """
        if not str(ctx.author.id) in self.sudoku_games:
            return await ctx.send('You haven\'t started a game yet!')

        # ensures played square exists within the board
        try:
            column = square[0]
            row = square[1]
        except IndexError:
            return await ctx.send('Invalid move!')
        if not re.match('[A-Ia-i]', str(column)) or not re.match('[1-9]', str(row)) or not re.match('[1-9]', str(number)):
            return await ctx.send('Invalid move!')
        
        status = f'Set {column.upper()}{row} to {number}.'
        
        # convert to 0 indexed for lists later
        column = ord(column.upper()) - 65
        row = int(row) - 1
        number = int(number)

        # ensures played square was not part of original puzzle
        if self.sudoku_games[str(ctx.author.id)][1].board[row][column] == None:
            # don't decrement empty square counter if replacing incorrect square
            if self.sudoku_games[str(ctx.author.id)][0].board[row][column] == None:
                self.sudoku_games[str(ctx.author.id)][3] -= 1

            self.sudoku_games[str(ctx.author.id)][0].board[row][column] = number
        else:
            return await ctx.send('Invalid move!')

        # build embed
        embed = discord.Embed(color=self.bot.PINK, title='Sudoku', description=f'<@{ctx.author.id}>\'s game')
        embed.add_field(name='', value=f'```{self.generate_board(board=self.sudoku_games[str(ctx.author.id)][0].board)}```')
        
        # checks if correct
        if self.sudoku_games[str(ctx.author.id)][3] == 0:
            if self.sudoku_games[str(ctx.author.id)][0].board == self.sudoku_games[str(ctx.author.id)][2].board:
                self.sudoku_games.pop(str(ctx.author.id))
                status = '🎉 Victory! 🎉'
            else:
                status = '❌ Incorrect... ❌'

        embed.set_footer(text=status, 
                         icon_url=self.bot.user.display_avatar.url)

        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(game_cog(bot))


