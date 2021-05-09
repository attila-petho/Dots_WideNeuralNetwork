import os
import torch
import random
import numpy as np
from collections import deque
from model import Q_Network, Q_Trainer

MAX_MEMORY = 100_000    # Memória maximális mérete
BATCH_SIZE = 500        # Batch mérete
LR = 0.001              # Learning rate

class Agent:

    def __init__(self, max_epsilon=1):
        self.n_episodes = 1                         # Epizódok száma
        self.max_epsilon = max_epsilon              # Exploration kezdeti valószínűsége
        self.min_epsilon = 0.0001                   # Min. exploration valószínűség
        self.decay_rate = 0.01                      # Exploration exponenciális csökkenésének mértéke
        self.gamma = 0.9                            # Diszkont ráta
        self.memory = deque(maxlen=MAX_MEMORY)      # Memória
        self.model = Q_Network(366, 1024, 1024, 4)  # Rétegek méretei
        self.trainer = Q_Trainer(self.model, lr=LR, gamma=self.gamma)

    def remember(self, state, action, reward, next_state, game_over):
        self.memory.append((state, action, reward, next_state, game_over))    # a legrégebbi elem kiesik, ha a memória megtelt

    def train_long_memory(self):
        # Egy Batch adat tanítása
        if len(self.memory) > BATCH_SIZE:
            mini_sample = random.sample(self.memory, BATCH_SIZE)
        else:
            mini_sample = self.memory

        states, actions, rewards, next_states, game_overs = zip(*mini_sample)
        self.trainer.train_step(states, actions, rewards, next_states, game_overs)  # nem egy-egy darab változót adunk neki, hanem egy BATCH-nyit

    def train_short_memory(self, state, action, reward, next_state, game_over):
        # Egy db adat tanítása
        self.trainer.train_step(state, action, reward, next_state, game_over)

    def get_action(self, state):
        # Exploration vs. Exploitation
        final_move = [0,0,0,0]
        epsilon = self.min_epsilon + (self.max_epsilon - self.min_epsilon) * np.exp(-self.decay_rate * self.n_episodes)
        # Létrehozunk egy random számot
        rand_n = random.uniform(0, 1)
        # Ha ez a szám nagyobb mint epsilon -> exploitation
        # Ha kisebb -> exploration
        if rand_n < epsilon:
            move = random.randint(0,3)
            final_move[move] = 1
        else:
            state0 = torch.tensor(state, dtype=torch.float)
            prediction = self.model(state0)
            move = torch.argmax(prediction).item()
            final_move[move] = 1

        return final_move

    def save(self, epoch, file_name='model.pth'):
        # Model mentése
        model_folder_path = './models'
        if not os.path.exists(model_folder_path):
            os.makedirs(model_folder_path)
        file_name = os.path.join(model_folder_path, file_name)
        torch.save({
            'epoch': epoch,
            'model_state_dict': self.model.state_dict(),
            'optimizer_state_dict': self.trainer.optimizer.state_dict(),
            'loss': self.trainer.loss,
        }, file_name)

    def load(self, path='.models/model.pth'):
        # Model betöltése
        checkpoint = torch.load(path)
        self.model.load_state_dict(checkpoint['model_state_dict'])
        self.trainer.optimizer.load_state_dict(checkpoint['optimizer_state_dict'])
        epoch = checkpoint['epoch']
        self.model.loss = checkpoint['loss']
        return epoch