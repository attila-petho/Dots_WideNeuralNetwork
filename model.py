import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F

class Q_Network(nn.Module):
    def __init__(self, input_size, hidden_size1, hidden_size2, output_size):
        super().__init__()
        self.linear1 = nn.Linear(input_size, hidden_size1)
        self.linear2 = nn.Linear(hidden_size1, hidden_size2)
        self.linear3 = nn.Linear(hidden_size2, output_size)

    def forward(self, x):
        x = F.relu(self.linear1(x))     # 1. réteg, aktiváció: ReLu
        x = F.relu(self.linear2(x))     # 2. réteg, aktiváció: ReLu
        x = self.linear3(x)             # 3. réteg, aktiváció nélkül
        return x

class Q_Trainer:
    def __init__(self, model, lr, gamma):
        self.model = model
        self.lr = lr
        self.gamma = gamma
        self.optimizer = optim.Adam(model.parameters(), lr=self.lr)
        self.criterion = nn.MSELoss()

    def train_step(self, state, action, reward, next_state, game_over):
        # lehet egy vagy több emlék
        state = torch.tensor(state, dtype=torch.float)
        next_state = torch.tensor(next_state, dtype=torch.float)
        action = torch.tensor(action, dtype=torch.long)
        reward = torch.tensor(reward, dtype=torch.float)
        # (n, x)

        if len(state.shape) == 1:
            # (1, x): 1db emlék esetén
            state = torch.unsqueeze(state, 0)
            next_state = torch.unsqueeze(next_state, 0)
            action = torch.unsqueeze(action, 0)
            reward = torch.unsqueeze(reward, 0)
            game_over = (game_over, )   # tuple 1 elemmel

        # 1: Becsült Q érték
        pred = self.model(state)
        target = pred.clone()
        # 2: Q_new = R + gamma * max(next_predicted Q value)  <- csak ha nincs vége az epizódnak
        for i in range(len(game_over)):
            Q_new = reward[i]
            if not game_over[i]:
                Q_new = reward[i] + self.gamma * torch.max(self.model(next_state[i]))

            target[i][torch.argmax(action).item()] = Q_new

        self.optimizer.zero_grad()  # gradiens nullázása
        self.loss = self.criterion(target, pred)
        self.loss.backward()
        self.optimizer.step()