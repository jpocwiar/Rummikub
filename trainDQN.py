import random
import numpy as np
from itertools import combinations
import threading

class DQNTrainer:
    def __init__(self, players, agent):
        super().__init__()
        self.tiles = []
        self.move_number = 0
        # self.user_tiles = []
        self.selected_tiles = []
        self.board = np.full((15, 40), None, dtype=object)
        self.board_prev = self.board.copy()
        self.groups = []
        # self.colours = [Qt.red, Qt.blue, Qt.darkYellow, Qt.black]
        self.colours = ["red", "blue", "yellow", "black"]
        self.players = players
        self.current_player_index = 0
        self.is_game_over = False
        self.agent = agent
        self.total_reward = 0
        self.generate_tiles()

    def move_tile(self, index_a, index_b):
        non_none_indices = np.where(self.board != None)
        tile = self.board[index_a]
        self.board[index_a] = None
        self.board[index_b] = tile
        #tile.setPosFromIndices(index_b)

    def make_move(self):
        if self.players[self.current_player_index].first_move:

            own_board = np.where(self.board == self.board_prev, None, self.board)
            mask = np.where(own_board != None)
            own_tiles = own_board[mask]
            sum_of_tiles = 0
            if len(own_tiles) >= 3:
                for i, tile in enumerate(own_tiles):
                    sum_of_tiles += tile.numer
                    if tile.is_joker:
                        if i > 0 and i < len(own_tiles) - 1 and mask[1][i] == mask[1][i - 1] + 1 and mask[1][i] == \
                                mask[1][i + 1] - 1:  # czy joker jest pomiędzy dwoma innymi elementami
                            if own_tiles[i - 1].is_joker:
                                sum_of_tiles += own_tiles[i + 1].numer
                            elif own_tiles[i + 1].is_joker:
                                sum_of_tiles += own_tiles[i - 1].numer
                            else:
                                sum_of_tiles += int((own_tiles[i - 1].numer + own_tiles[i + 1].numer) / 2)
                        elif i == 0 or mask[1][i] != mask[1][i - 1] + 1:  # gdy joker jest na lewym skraju
                            try:
                                if own_tiles[i + 1].is_joker:
                                    sum_of_tiles += own_tiles[i + 2].numer
                                elif own_tiles[i + 2].is_joker:
                                    sum_of_tiles += own_tiles[i + 1].numer
                                else:
                                    sum_of_tiles += own_tiles[i + 1].numer - (
                                                own_tiles[i + 2].numer - own_tiles[i + 1].numer)
                            except:
                                pass
                        elif i == len(own_tiles) - 1 or mask[1][i] != mask[1][i + 1] - 1:  # jeśli joker na końcu serii
                            try:
                                if own_tiles[i - 1].is_joker:
                                    sum_of_tiles += own_tiles[i - 2].numer
                                elif own_tiles[i - 2].is_joker:
                                    sum_of_tiles += own_tiles[i - 1].numer
                                else:
                                    sum_of_tiles += own_tiles[i - 1].numer - (
                                                own_tiles[i - 2].numer - own_tiles[i - 1].numer)
                            except:
                                pass

            if len(self.players[self.current_player_index].tiles) == len(
                    self.players[self.current_player_index].tiles_prev) and not self.timed_out:
                # print("Musisz wykonać ruch!")
                self.logger.error(str(self.players[self.current_player_index].name) + " nie wykonał pierwszego ruchu!")
            elif self.check_move(own_board) and not len(self.players[self.current_player_index].tiles) == len(
                    self.players[self.current_player_index].tiles_prev) and sum_of_tiles >= 30:
                # print("ruch prawidłowy")
                self.logger.log(
                    str(self.players[self.current_player_index].name) + " położył kombinację o wartości " + str(
                        sum_of_tiles))
                self.board_prev = self.board.copy()
                self.players[self.current_player_index].tiles_prev = self.players[
                    self.current_player_index].tiles.copy()

                self.players[self.current_player_index].first_move = False  # już nie pierwszy ruch
                self.switch_player()
            elif self.check_move(own_board) and not len(self.players[self.current_player_index].tiles) == len(
                    self.players[self.current_player_index].tiles_prev) and sum_of_tiles < 30 and not self.timed_out:
                self.logger.error(
                    self.players[self.current_player_index].name + " położył pierwszą kombinację o wartości " + str(
                        sum_of_tiles) + ". Przy pierwszym ruchu konieczne jest wyłożenie klocków o łącznej wartości >=30!")
            elif self.timed_out and (not self.check_move(own_board) or (
                    len(self.players[self.current_player_index].tiles) == len(
                self.players[self.current_player_index].tiles_prev)) or sum_of_tiles < 30):
                self.logger.error(
                    self.players[
                        self.current_player_index].name + " nie wykonał poprawnego pierwszego ruchu i czas się skończył!")

                self.draw_tile()
            elif not self.check_move(own_board) and not self.timed_out:
                self.logger.error(
                    self.players[self.current_player_index].name + " nie wykonał poprawnego pierwszego ruchu!")
        else:
            if len(self.players[self.current_player_index].tiles) == len(
                    self.players[self.current_player_index].tiles_prev) and not self.timed_out:
                # print("Musisz wykonać ruch!")
                self.logger.error(str(self.players[self.current_player_index].name) + " nie wykonał ruchu!")
            elif self.check_move(self.board) and not len(self.players[self.current_player_index].tiles) == len(
                    self.players[self.current_player_index].tiles_prev):
                # print("ruch prawidłowy")
                self.logger.log(
                    str(self.players[self.current_player_index].name) + " wykonał prawidłowy ruch i zostało mu " + str(
                        len(self.players[self.current_player_index].tiles)) + " klocków")
                if len(self.players[self.current_player_index].tiles) == 0:
                    self.logger.log("Wygrywa " + str(self.players[self.current_player_index].name) + "!")
                    self.is_game_over = True
                self.board_prev = self.board.copy()
                self.players[self.current_player_index].tiles_prev = self.players[
                    self.current_player_index].tiles.copy()
                self.switch_player()
            # elif (not self.check_move() and self.timed_out) or (sorted(self.players[self.current_player_index].tiles, key=lambda tile: (tile.numer, self.colours.index(tile.colour)) == sorted(self.players[self.current_player_index].tiles_prev, key=lambda tile: (tile.numer, self.colours.index(tile.colour)))) and self.timed_out): #przy pierwszym ruchu może robić jakby osobny board? Zęby to 30 sprawdzać
            elif (not self.check_move(self.board) and self.timed_out) or (
                    len(self.players[self.current_player_index].tiles) == len(
                    self.players[self.current_player_index].tiles_prev) and self.timed_out):
                # przywróć stan poprzedni i przejdź do następnego gracza
                # print("ruch nieprawidłowy i czas minął!")
                self.logger.error(
                    self.players[self.current_player_index].name + " nie wykonał poprawnego ruchu i czas się skończył!")
                self.draw_tile()
            elif not self.check_move(self.board) and not self.timed_out:
                self.logger.error(str(self.players[self.current_player_index].name) + " - ruch nieprawidłowy!")

    def check_move(self, board):
        if self.is_every_element_grouped(board):
            # print("youp")
            for group in self.groups:
                non_joker = np.sum([not til.is_joker for til in group])
                # print(non_joker)
                if (non_joker <= 1):
                    # self.logger.log(str(self.players[self.current_player_index].name) + "- kombinacja z dominacją jokerów")
                    pass
                else:
                    colors = set(str(til.colour) for til in group if not til.is_joker)
                    color_count = len(colors)
                    # print("kolory: " + str(color_count))
                    if color_count == 1:
                        unique_values = set(til.numer - idx for idx, til in enumerate(group) if not til.is_joker)
                        if len(unique_values) == 1 and not unique_values == {0} and not next(iter(unique_values)) + len(
                                group) - 1 >= 14:
                            # print(unique_values)
                            # print("po kolei")
                            # self.logger.log(
                            #     str(self.players[self.current_player_index].name) + "- kombinacja jeden kolor, po kolei")
                            pass
                        else:
                            # print("nie po kolei")
                            # self.logger.error(
                            #     str(self.players[
                            #             self.current_player_index].name) + "- kombinacja nie po kolei")
                            return False
                    elif color_count == non_joker and len(group) <= 4:
                        values = set(til.numer for til in group if not til.is_joker)
                        if len(values) == 1:
                            pass
                            # print("te same cyfr")
                            # self.logger.log(
                            #     str(self.players[
                            #             self.current_player_index].name) + " - kombinacja tych samych cyfr")
                        else:
                            return False
                    else:
                        # print("źle")
                        return False
            return True
        else:
            return False

    def is_every_element_grouped(self, board):
        # board = self.board
        non_none_indices = np.where(board != None)
        counter = 0
        self.groups = []
        if non_none_indices[0].size < 3:
            return False
        for i in range(non_none_indices[0].size):

            if counter == 0:
                counter += 1
                group = [board[non_none_indices[0][i], non_none_indices[1][i]]]
            elif non_none_indices[0][i] == y and non_none_indices[1][i] == x + 1:  # sprawdzanie czy obok siebie
                counter += 1
                group.append(board[non_none_indices[0][i], non_none_indices[1][i]])
                if i == non_none_indices[0].size - 1 and counter >= 3:
                    self.groups.append(group)

            elif (not (non_none_indices[0][i] == y and non_none_indices[1][i] == x + 1) or i == non_none_indices[
                0].size) and counter < 3:
                return False
            elif not (non_none_indices[0][i] == y and non_none_indices[1][i] == x + 1) and counter >= 3:
                counter = 1
                self.groups.append(group)
                group = [board[non_none_indices[0][i], non_none_indices[1][i]]]
                # print("bbbb")

            y = non_none_indices[0][i]
            x = non_none_indices[1][i]
        if counter < 3:
            return False
        # print(len(self.groups))
        return True

    def switch_player(self):

        self.current_player_index = (self.current_player_index + 1) % len(self.players)

        # if self.players[self.current_player_index].is_ai:
        #     self.make_ai_move()

    def generate_tiles(self):
        # Generowanie klocków
        self.tiles = [Tile(colour, numer)
                      for colour in self.colours
                      for numer in range(1, 14)
                      for i in range(2)]

        self.tiles += [Tile("black", 0, is_joker=True),
                       Tile("red", 0, is_joker=True)]
        random.shuffle(self.tiles)
        for player in self.players:
            player.tiles = self.tiles[:14]
            player.tiles_prev = player.tiles.copy()
            self.tiles = self.tiles[14:]
        self.current_player_index = 0

    def valid_groups(self, group):
        non_joker = np.sum([not til.is_joker for til in group])
        if (non_joker <= 1):
            # self.logger.log(str(self.players[self.current_player_index].name) + "- kombinacja z dominacją jokerów")
            pass
        else:
            colors = set(str(til.colour) for til in group if not til.is_joker)
            color_count = len(colors)
            # print("kolory: " + str(color_count))
            if color_count == 1:
                unique_values = set(til.numer - idx for idx, til in enumerate(group) if not til.is_joker)
                if len(unique_values) == 1 and not unique_values == {0} and not next(iter(unique_values)) + len(
                        group) - 1 >= 14:
                    pass
                else:
                    return False
            elif color_count == non_joker and len(group) <= 4:
                values = set(til.numer for til in group if not til.is_joker)
                if len(values) == 1:
                    pass
                else:
                    return False
            else:
                return False
        return True

    def get_random_indices(self, board, len):
        for i in range(100):
            row, col = np.random.randint(0, 10), np.random.randint(0, 27)
            # print(row)
            # print(col)
            for i in range(-1, len + 1):
                if col + len + 1 < 27 and board[row, col + i] is None:
                    return row, col
        else:
            return False

    def make_ai_move(self):
        placements = self.possible_placements()
        moved = False
        while len(placements) > 0:
            indexx, indexy = self.get_random_indices(self.board,len(placements[0]))
            for i, tile in enumerate(placements[0]):
                self.players[self.current_player_index].tiles.remove(tile)
                self.board[indexx, indexy + i] = tile
                moved = True
            #row+=1
            placements = self.possible_placements()

        state = self.agent.board_to_input(self.board, self.players[self.current_player_index].tiles)



        for step in range(max_steps_per_episode):
          if len(np.where(self.board != None)) >0:
            action = self.agent.act(self.board, self.players[self.current_player_index].tiles)

            indices = action[0]
            empty_index = action[1]
            self.move_tile(indices, empty_index)
            new_board = self.board.copy()

            next_state = self.agent.board_to_input(new_board)

            num_tiles_before = len(np.where(board == self.agent.player_tile)[0])
            num_tiles_after = len(np.where(new_board == self.agent.player_tile)[0])
            reward = num_tiles_before - num_tiles_after

            self.agent.remember(state, action, reward, next_state, False)

            self.total_reward += reward

            # Update the state
            state = next_state

            # Check if the episode is over
            done = self.agent.is_done(board)
            if done:
                break

        # Decay the epsilon value
        if self.agent.epsilon > self.agent.epsilon_min:
            self.agent.epsilon *= self.agent.epsilon_decay

        # Train the self.agent
        if len(self.agent.memory) > batch_size:
            self.agent.replay(batch_size, self.players[self.current_player_index].tiles, self)


        for tile in self.players[self.current_player_index].tiles:
            moves = self.possible_movements(tile)
            if len(moves) >0:
                move = moves[np.random.randint(0, len(moves))]
                # print(move[1])
                # print(move[0])
                self.players[self.current_player_index].tiles.remove(tile)
                self.board[move[0],move[1]] = tile

                moved = True
        if moved:
            prev_ind = self.current_player_index
            self.make_move()
            ind = self.current_player_index
            if prev_ind == ind:
                moved = False
        if not moved:
            self.draw_tile()

    def move_tile(self, index_a, index_b):
        non_none_indices = np.where(self.board != None)
        tile = self.board[index_a]
        self.board[index_a] = None
        self.board[index_b] = tile



    def possible_placements_thread(self):
        thread = threading.Thread(target=self.possible_placements)
        thread.start()


    def possible_placements(self):
        # self.sort_tiles_by_number()
        # self.sort_tiles_by_color()
        #self.check_move(board)
        tiles = self.players[self.current_player_index].tiles
        results = []
        for i in range(3, 5):
            for combination in combinations(tiles, i):
                if self.valid_groups(list(combination)):
                    results.append(list(combination))
        #return results
        #results.sort(key=lambda x: (-len(x), -max([tile.numer for tile in x if not tile.is_joker])))
        if self.players[self.current_player_index].first_move:
            results.sort(key=lambda x: (-len(x) * max([tile.numer for tile in x])))
        else:
            results.sort(key=lambda x: (-len(x), -max([tile.numer for tile in x if not tile.is_joker])))
        # for combination in results:
        #     for tile in combination:
        #         print(tile.numer)
        #     print("===================")
        return results

    def possible_movements(self, tile):
        possible_moves = []
        if self.players[self.current_player_index].first_move:
            board = np.where(self.board == self.board_prev, None, self.board)
        else:
            board = self.board
        # if not self.players[self.current_player_index].first_move:
        mask = (board[:, :-1] != None) & (board[:, 1:] == None)
        left_indices = np.column_stack(np.where(mask))
        left_indices[:, 1] += 1

        mask = (board[:, 1:] != None) & (board[:, :-1] == None)
        right_indices = np.column_stack(np.where(mask))
        if tile.is_joker:
            # possible_moves = np.concatenate((left_indices, right_indices))
            left_mask = np.zeros(len(left_indices), dtype=bool)
            for i, idx in enumerate(left_indices):
                left_tile = board[idx[0], idx[1] - 1]
                left_left_tile = board[idx[0], idx[1] - 2]
                if left_tile is not None and left_tile.numer < 13 and left_left_tile is not None and (left_left_tile.numer == left_tile.numer - 1 or left_left_tile.is_joker):
                    left_mask[i] = True
                elif left_tile is not None and left_left_tile is not None and (left_left_tile.numer == left_tile.numer or left_left_tile.is_joker) and board[idx[0], idx[1] - 4] is None:
                    left_mask[i] = True
            possible_left_indices = left_indices[left_mask]

            right_mask = np.zeros(len(right_indices), dtype=bool)
            for i, idx in enumerate(right_indices):
                right_tile = board[idx[0], idx[1] + 1]
                right_right_tile = board[idx[0], idx[1] + 2]
                if right_tile is not None and right_tile.numer >= 2 and right_right_tile is not None and (right_right_tile.numer == right_tile.numer + 1 or right_right_tile.is_joker):
                    right_mask[i] = True
                elif right_tile is not None and right_right_tile is not None and (right_right_tile.numer == right_tile.numer or right_right_tile.is_joker) and board[idx[0], idx[1] + 4] is None:
                    right_mask[i] = True
            possible_right_indices = right_indices[right_mask]

            possible_moves = np.concatenate((possible_left_indices, possible_right_indices))
        else:
            for i in range(len(right_indices)):
                if board[right_indices[:, 0][i], right_indices[:, 1][i] + 1] != None and board[
                    right_indices[:, 0][i], right_indices[:, 1][i] + 2] != None:

                    if (board[right_indices[:, 0][i], right_indices[:, 1][i] + 1].is_joker or (
                            board[right_indices[:, 0][i], right_indices[:, 1][i] + 1].numer == tile.numer + 1 and
                            board[right_indices[:, 0][i], right_indices[:, 1][i] + 1].colour == tile.colour)) and (
                            board[right_indices[:, 0][i], right_indices[:, 1][i] + 2].is_joker or (
                            board[right_indices[:, 0][i], right_indices[:, 1][i] + 2].numer == tile.numer + 2 and
                            board[right_indices[:, 0][i], right_indices[:, 1][i] + 2].colour == tile.colour)) and (
                            board[
                                right_indices[:, 0][i], right_indices[:, 1][i] + 3] == None or
                            board[right_indices[:, 0][i], right_indices[:, 1][i] + 3].is_joker or  (board[
                                                                                            right_indices[:, 0][i],
                                                                                            right_indices[:, 1][
                                                                                                i] + 3].numer == tile.numer + 3 and
                                                                                        board[
                                                                                            right_indices[:, 0][i],
                                                                                            right_indices[:, 1][
                                                                                                i] + 3].colour == tile.colour)):
                        possible_moves.append((right_indices[i]))
                    elif (board[right_indices[:, 0][i], right_indices[:, 1][i] + 1].is_joker or (
                            board[right_indices[:, 0][i], right_indices[:, 1][i] + 1].numer == tile.numer and board[
                        right_indices[:, 0][i], right_indices[:, 1][i] + 1].colour != tile.colour)) and (
                            board[right_indices[:, 0][i], right_indices[:, 1][i] + 2].is_joker or (
                            board[right_indices[:, 0][i], right_indices[:, 1][i] + 2].numer == tile.numer and board[
                        right_indices[:, 0][i], right_indices[:, 1][i] + 2].colour != tile.colour)) and (
                            board[right_indices[:, 0][i], right_indices[:, 1][i] + 3] == None or board[
                        right_indices[:, 0][i], right_indices[:, 1][i] + 3].is_joker or (board[
                                                                                             right_indices[:, 0][i],
                                                                                             right_indices[:, 1][
                                                                                                 i] + 3].numer == tile.numer and
                                                                                         board[
                                                                                             right_indices[:, 0][i],
                                                                                             right_indices[:, 1][
                                                                                                 i] + 3].colour != tile.colour)) and (
                            board[right_indices[:, 0][i], right_indices[:, 1][i] + 4] == None):
                        possible_moves.append((right_indices[i]))
            for i in range(len(left_indices)):
                if board[left_indices[:, 0][i], left_indices[:, 1][i] - 1] != None and board[
                    left_indices[:, 0][i], left_indices[:, 1][i] - 2] != None:
                    if (board[left_indices[:, 0][i], left_indices[:, 1][i] - 1].is_joker or (
                            board[left_indices[:, 0][i], left_indices[:, 1][i] - 1].numer == tile.numer - 1 and
                            board[
                                left_indices[:, 0][i], left_indices[:, 1][i] - 1].colour == tile.colour)) and (
                            board[left_indices[:, 0][i], left_indices[:, 1][i] - 2].is_joker or (
                            board[left_indices[:, 0][i], left_indices[:, 1][i] - 2].numer == tile.numer - 2 and
                            board[
                                left_indices[:, 0][i], left_indices[:, 1][i] - 2].colour == tile.colour)) and (
                            board[left_indices[:, 0][i], left_indices[:, 1][i] - 3] == None or board[
                        left_indices[:, 0][i], left_indices[:, 1][i] - 3].is_joker or (
                                    board[left_indices[:, 0][i], left_indices[:, 1][
                                                                     i] - 3].numer == tile.numer - 3 and
                                    board[
                                        left_indices[:, 0][i], left_indices[:, 1][i] - 3].colour == tile.colour)):
                        possible_moves.append((left_indices[i]))
                    elif (board[left_indices[:, 0][i], left_indices[:, 1][i] - 1].is_joker or (
                            board[left_indices[:, 0][i], left_indices[:, 1][i] - 1].numer == tile.numer and
                            board[
                                left_indices[:, 0][i], left_indices[:, 1][i] - 1].colour != tile.colour)) and (
                            board[left_indices[:, 0][i], left_indices[:, 1][i] - 2].is_joker or (
                            board[left_indices[:, 0][i], left_indices[:, 1][i] - 2].numer == tile.numer and
                            board[
                                left_indices[:, 0][i], left_indices[:, 1][i] - 2].colour != tile.colour)) and (
                            board[left_indices[:, 0][i], left_indices[:, 1][i] - 3] == None or board[
                        left_indices[:, 0][i], left_indices[:, 1][i] - 3].is_joker or (
                                    board[left_indices[:, 0][i], left_indices[:, 1][i] - 3].numer == tile.numer and
                                    board[
                                        left_indices[:, 0][i], left_indices[:, 1][
                                                                   i] - 3].colour != tile.colour)) and (
                            board[left_indices[:, 0][i], left_indices[:, 1][i] - 4] == None):
                        possible_moves.append((left_indices[i]))

            # indices = np.concatenate((left_indices, right_indices))
        return possible_moves

    def draw_tile(self):
        if len(self.tiles) > 0:
            self.board = self.board_prev.copy()
            self.players[self.current_player_index].tiles = self.players[
                self.current_player_index].tiles_prev.copy()
            tile = self.tiles.pop()
            #self.user_tiles.append(tile)
            self.players[self.current_player_index].add_tile(tile)
            self.board_prev = self.board.copy()
            self.players[self.current_player_index].tiles_prev = self.players[
                self.current_player_index].tiles.copy()
            #self.addItem(tile)
            self.logger.log(str(self.players[self.current_player_index].name) + " dobrał klocek")
            self.switch_player()
        else:
            # to na wypadek rzadkiej sytuacji kiedy zabraknie klocków do dobrania
            self.is_game_over = True
            pass


batch_size = 32
num_episodes = 1000
max_steps_per_episode = 100
board = np.full((15, 40), None, dtype=object)
state_size = board.size
action_size = board.size

agent = DQNAgent(state_size, action_size)

for episode in range(num_episodes):
    #board = np.full((15, 40), None, dtype=object)
    players = [Player("AI0", True), Player("AI1", True), Player("AI2", True),
               Player("AI3", True)]
    board = DQNTrainer(players, agent)
    while not board.is_game_over:
        board.make_ai_move()

    print("Episode:", episode + 1, "Total Reward:", board.total_reward, "Epsilon:", agent.epsilon)

agent.save_model()




