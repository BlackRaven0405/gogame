# Manual play can be used to illustrate go strategies, to show moves of a past game, or to explore possibilities
# This program display the 30 firsts moves of the first game between AlphaGo and Fan Hui

from gopy import Board, Color

b = Board(show=True)
b.play(15, 3, color=Color.Black)
b.play(15, 15, color=Color.White)
b.play(3, 3, color=Color.Black)
b.play(2, 15, color=Color.White)
b.play(4, 16, color=Color.Black)
b.play(7, 15, color=Color.White)
b.play(5, 15, color=Color.Black)
b.play(3, 13, color=Color.White)
b.play(2, 17, color=Color.Black)
b.play(2, 9, color=Color.White)

b.play(13, 16, color=Color.Black)
b.play(11, 16, color=Color.White)
b.play(15, 13, color=Color.Black)
b.play(13, 15, color=Color.White)
b.play(12, 15, color=Color.Black)
b.play(12, 16, color=Color.White)
b.play(16, 15, color=Color.Black)
b.play(14, 16, color=Color.White)
b.play(16, 16, color=Color.Black)
b.play(16, 11, color=Color.White)

b.play(17, 13, color=Color.Black)
b.play(16, 5, color=Color.White)
b.play(13, 2, color=Color.Black)
b.play(17, 3, color=Color.White)
b.play(13, 17, color=Color.Black)
b.play(14, 17, color=Color.White)
b.play(13, 14, color=Color.Black)
b.play(14, 15, color=Color.White)
b.play(16, 2, color=Color.Black)
b.play(16, 8, color=Color.White)
