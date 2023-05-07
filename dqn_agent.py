import random
import numpy as np
from collections import deque
from keras.layers import Dense
from keras.models import Sequential
from keras.optimizers import Adam



class DQNAgent:
    def __init__(self, state_size, action_size):
        self.state_size = state_size
        self.action_size = action_size
        self.memory = deque(maxlen=2000)
        self.gamma = 0.95
        self.epsilon = 1.0
        self.epsilon_min = 0.01
        self.epsilon_decay = 0.995
        self.learning_rate = 0.001
        self.model = self._build_model()

    def _build_model(self):
        model = Sequential()
        model.add(Dense(64, input_dim=self.state_size, activation='relu'))
        model.add(Dense(32, activation='relu'))
        model.add(Dense(self.action_size, activation='linear'))
        model.compile(loss='mse', optimizer=Adam(lr=self.learning_rate))
        return model

    def remember(self, state, action, reward, next_state, done):
        self.memory.append((state, action, reward, next_state, done))

    def act(self, state, tile_list):
        if np.random.rand() <= self.epsilon:
            indices = np.where(state != None)
            num_tiles = len(tile_list)
            empty_indices = np.where(state == None)
            if len(empty_indices) > 0 and len(indices) > 0 and len(empty_indices[0]) > 0 and len(indices[0]) > 0 and len(empty_indices[1]) > 0 and len(indices[1]) > 0:
              empty_rows = empty_indices[0]
              empty_cols = empty_indices[1]
              if len(empty_rows) > 0 and len(empty_cols) > 0:
                empty_index = empty_indices[0][np.random.randint(len(empty_indices))], empty_indices[1][
                    np.random.randint(len(empty_indices))]
                #print(len(indices))
                tile_index = indices[0][np.random.randint(len(indices))], indices[1][
                    np.random.randint(len(indices))]
                return tile_index, empty_index

        q_values = self.model.predict(state)
        return np.unravel_index(np.argmax(q_values), q_values.shape)

    def replay(self, batch_size, tiles_list, board):
        minibatch = np.array(random.sample(self.memory, batch_size))
        for state, action, reward, next_state, done in minibatch:
            target = reward
            if not done:
                target = reward + self.gamma * np.amax(self.model.predict(next_state)[0])
            target_f = self.model.predict(state)
            indices = np.unravel_index(action, self.state_size)
            empty_indices = np.where(state == None)
            empty_index = empty_indices[0][0], empty_indices[1][0]
            self.move_tile(indices, empty_index)
            new_state = self.board_to_input(self.board, tiles_list)
            new_q_value = target_f[0][action] = target
            self.model.fit(state, target_f, epochs=1, verbose=0)
            self.memory.append((new_state, action, new_q_value, next_state, done))

    def board_to_input(self, board, tile_list):
        input_arr = np.zeros((board.shape[0], board.shape[1], len(tile_list)))
        for i, tile in enumerate(tile_list):
            tile_indices = np.where(board == tile)
            input_arr[tile_indices[0], tile_indices[1], i] = 1
        return input_arr.flatten()


