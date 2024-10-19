from quoridor import *

b = Board()

tl = b.board[3][3]
br = b.board[4][4]

vert = WallOrientation.VERTICAL
hor = WallOrientation.HORIZONTAL

b.place_wall(tl, vert)
b.place_wall(tl, hor)

b.print_board()

p1 = Player(name="a", position=(3, 3))
p2 = Player(name="b", position=(3, 2))


b.set_occupation_state({p1, p2})
b.get_valid_moves(p1)
b.get_valid_moves(p2)
