import sqlite3
import numpy as np
import os

class DatabaseSQL:
    def __init__(self, num_players):
        self.num_players = num_players
        self.move_index = 0
        db_file = 'rummikub_game.db'
        if os.path.exists(db_file):
            os.remove(db_file)
        self.conn = sqlite3.connect(db_file)
        self.cursor = self.conn.cursor()
        self.init_db()

    def init_db(self):
        self.cursor.execute('CREATE TABLE board_tiles (move_index INTEGER, number INTEGER, color TEXT, row INTEGER, col INTEGER)')
        for i in range(self.num_players):
            self.cursor.execute(f'CREATE TABLE player{i+1}_tiles (move_index INTEGER, number INTEGER, color TEXT, player_id INTEGER)')
        self.cursor.execute('CREATE TABLE draw_tiles (move_index INTEGER, number INTEGER, color TEXT)')
        #self.save_to_db()
        self.conn.commit()


    def save_to_db(self, player_id, board, player_tiles, move):
        # self.cursor.execute('DELETE FROM board_tiles WHERE move_index = ?', (self.move_index,))
        # self.cursor.execute('DELETE FROM player_tiles WHERE move_index = ?', (self.move_index,))
        # self.cursor.execute('DELETE FROM draw_tiles WHERE move_index = ?', (self.move_index,))
        indices = np.where(board != None)

        for i in range(indices[0].size):
            tile = board[indices[0][i],indices[1][i]]
            #print(indices[0][i])
            row = int(indices[0][i])
            col = int(indices[1][i])
            self.cursor.execute('INSERT INTO board_tiles VALUES (?, ?, ?, ?, ?)',
                                (move, tile.numer, tile.colour, row, col))
        for tile in player_tiles:
            self.cursor.execute(f'INSERT INTO player{player_id+1}_tiles VALUES (?, ?, ?, ?)', (move, tile.numer, tile.colour, player_id))
        # for tile in self.draw_tiles:
        #     self.cursor.execute('INSERT INTO draw_tiles VALUES (?, ?, ?)', (self.move_index, tile.numer, tile.colour))
        self.conn.commit()
        # print wywalić potem
        self.cursor.execute('SELECT * FROM board_tiles')
        rows = self.cursor.fetchall()

        for row in rows:
            print(row)

    def move_tile_to_table(self, tile, row, col):
        self.board_tiles[row, col] = tile
        self.players_tiles[tile.player_id].remove(tile)
        self.move_index += 1
        self.save_to_db()

    def move_tile_to_player(self, tile, player_id):
        self.players_tiles[player_id].append(tile)
        row, col = np.where(self.board_tiles == tile)
        self.board_tiles[row, col] = None
        self.move_index += 1
        self.save_to_db()

    def draw_tile(self, player_id):
        tile = self.draw_tiles.pop()
        tile.player_id = player_id
        self.players_tiles[player_id].append(tile)
        self.move_index += 1
        self.save_to_db()

    def restart_game(self):
        self.board_tiles = np.zeros((4, 13), dtype=object)
        self.players_tiles = [[] for _ in range(self.num_players)]
        self.draw_tiles = []
        self.move_index = 0
        self.cursor.execute('DELETE FROM board_tiles')
        self.cursor.execute('DELETE FROM player_tiles')
        self.cursor.execute('DELETE FROM draw_tiles')
        self.conn.commit()


