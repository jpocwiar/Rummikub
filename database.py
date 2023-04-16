import sqlite3
import numpy as np
import os
import xml.etree.ElementTree as ET

class DatabaseSQL:
    def __init__(self, num_players):
        self.num_players = num_players
        self.move_index = 0
        db_file = 'history.db'
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
        # self.cursor.execute('SELECT * FROM board_tiles')
        # rows = self.cursor.fetchall()
        #
        # for row in rows:
        #     print(row)




class DatabaseXML:
    def __init__(self, num_players):
        self.num_players = num_players
        self.move_index = 0
        xml_file = 'history.xml'
        if os.path.exists(xml_file):
            os.remove(xml_file)
        self.tree = ET.ElementTree(ET.Element('root'))
        self.root = self.tree.getroot()
        self.init_db()

    def init_db(self):
        ET.SubElement(self.root, 'board_tiles')
        for i in range(self.num_players):
            ET.SubElement(self.root, f'player{i+1}_tiles')
        ET.SubElement(self.root, 'draw_tiles')
        #self.save_to_db(0, np.zeros((14, 14), dtype=object), [], 0)

    def save_to_db(self, player_id, board, player_tiles, move):
        board_elem = ET.SubElement(self.root.find('board_tiles'), 'move', {'index': str(move)})
        indices = np.where(board != None)
        for i in range(indices[0].size):
            tile = board[indices[0][i],indices[1][i]]
            tile_elem = ET.SubElement(board_elem, 'tile', {'number': str(tile.numer), 'color': tile.colour, 'row': str(indices[0][i]), 'col': str(indices[1][i])})
        player_elem = ET.SubElement(self.root.find(f'player{player_id + 1}_tiles'), 'move', {'index': str(move)})
        for i, tile in enumerate(player_tiles):

            tile_elem = ET.SubElement(player_elem, 'tile', {'number': str(tile.numer), 'color': tile.colour, 'player_id': str(player_id)})
        self.tree.write('history.xml', encoding='utf-8')