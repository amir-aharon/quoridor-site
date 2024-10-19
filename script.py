from quoridor import *

b = Board()

tl = b.board[3][3]
br = b.board[4][4]

vert = WallOrientation.VERTICAL
hor = WallOrientation.HORIZONTAL

b.place_wall(tl, vert)
b.place_wall(tl, hor)

b.print_board()
