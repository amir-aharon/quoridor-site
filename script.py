from quoridor import *

b = Board()

tl = b.board[3][3]
br = b.board[4][4]

vert = WallOrientation.VERTICAL
hor = WallOrientation.HORIZONTAL

b.place_wall(tl, vert)
b.place_wall(tl, hor)

p1 = Player(name="1", position=(3, 3))
p2 = Player(name="2", position=(3, 2))

b.print_board([p1, p2])


b.set_occupation_state({p1, p2})
# b.get_valid_moves(p1)
b.get_valid_moves(p2)


from quoridor import *

g = GameManager()
g.play()
