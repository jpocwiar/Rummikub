
class Player:
    def __init__(self, name="player"):
        self.tiles = []
        self.tiles_prev = []
        self.name = name
        self.first_move = True

    def add_tile(self, tile):
        self.tiles.append(tile)