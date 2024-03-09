
class Player:
    def __init__(self, name="player", is_ai = False):
        self.tiles = []
        self.tiles_prev = []
        self.name = name
        self.first_move = True
        self.is_ai = is_ai

    def add_tile(self, tile):
        self.tiles.append(tile)