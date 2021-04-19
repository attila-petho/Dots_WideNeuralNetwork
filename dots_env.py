import pygame
import random
import math
import numpy as np

class Dotsgame_env:

    def __init__(self, max_frames=2000):
        pygame.init()
        # Változók
        self.MAX_FRAMES = max_frames       # max ennyi lépés lehet egy epizódban
        self.PLAYER_RADIUS = 10     # játékosok kezdő sugara
        self.START_VEL = 5          # játékosok kezdő sebessége
        self.BALL_RADIUS = 5        # pöttyök mérete
        self.MASS_LOSS_TIME = 2000  # méretcsökkenés gyorsasága ms-ban
        self.N_BALLS = 100          # pöttyök száma
        self.MASS_LOSS = pygame.USEREVENT + 1
        pygame.time.set_timer(self.MASS_LOSS, self.MASS_LOSS_TIME)
        # Képernyő inicializálása
        self.FPS = 30
        self.W = 400
        self.H = 400
        self.WIN = pygame.display.set_mode((self.W, self.H))
        self.COLORS = [(255, 128, 0), (128, 255, 0), (0, 255, 0), (0, 255, 128), (0, 255, 255), (0, 128, 255),
                       (0, 0, 255),
                       (0, 0, 255), (128, 0, 255), (255, 0, 255), (255, 0, 128), (128, 128, 128), (0, 0, 0)]
        pygame.display.set_caption("Dots AI")
        self.clock = pygame.time.Clock()

        # Játék inicializálása
        self.balls = []
        self.state = None
        self.reset()

        # Sebességek
        self.red_vel = self.START_VEL - round(self.red_mass / 14)
        if self.red_vel <= 1:
            self.red_vel = 1

        self.yellow_vel = self.START_VEL - round(self.yellow_mass / 14)
        if self.yellow_vel <= 1:
            self.yellow_vel = 1

    def reset(self):
        self.balls.clear()
        self.red_mass = 0
        self.yellow_mass = 0
        self.red_x = random.randrange(0, self.W)
        self.red_y = random.randrange(0, self.H)
        self.yellow_x, self.yellow_y = self.get_start_location()
        self.create_balls()
        self.step_iteration = 0

    def create_balls(self):
        # létrehozza a pöttyöket
        for i in range(self.N_BALLS):
            while True:
                stop = True
                x = random.randrange(5, self.W - 5)
                y = random.randrange(5, self.H - 5)
                red_dis = math.sqrt((x - self.red_x) ** 2 + (y - self.red_y) ** 2)
                yellow_dis = math.sqrt((x - self.yellow_x) ** 2 + (y - self.yellow_y) ** 2)
                if red_dis <= self.PLAYER_RADIUS + self.red_mass or yellow_dis <= self.PLAYER_RADIUS + self.yellow_mass:
                    stop = False
                if stop:
                    break

            self.balls.append((x, y, random.choice(self.COLORS)))

    def step(self, red_action, yellow_action):
        self.step_iteration += 1
        self.red_reward = -0.1      # pirosnak minden lépés -0.1 jutalom
        self.yellow_reward = 0.1    # sárgának minden lépés +0.1 jutalom

        # 1. Inputok kezelése
        if np.array_equal(red_action, [1, 0, 0, 0]):  # LEFT
            if self.red_x - self.red_vel - self.PLAYER_RADIUS - self.red_mass >= 0:
                self.red_x = self.red_x - self.red_vel
        elif np.array_equal(red_action, [0, 1, 0, 0]):  # RIGHT
            if self.red_x + self.red_vel + self.PLAYER_RADIUS + self.red_mass <= self.W:
                self.red_x = self.red_x + self.red_vel
        elif np.array_equal(red_action, [0, 0, 1, 0]):  # UP
            if self.red_y - self.red_vel - self.PLAYER_RADIUS - self.red_mass >= 0:
                self.red_y = self.red_y - self.red_vel
        elif np.array_equal(red_action, [0, 0, 0, 1]):  # DOWN
            if self.red_y + self.red_vel + self.PLAYER_RADIUS + self.red_mass <= self.H:
                self.red_y = self.red_y + self.red_vel

        if np.array_equal(yellow_action, [1, 0, 0, 0]):  # LEFT
            if self.yellow_x - self.yellow_vel - self.PLAYER_RADIUS - self.yellow_mass >= 0:
                self.yellow_x = self.yellow_x - self.yellow_vel
        elif np.array_equal(yellow_action, [0, 1, 0, 0]):  # RIGHT
            if self.yellow_x + self.yellow_vel + self.PLAYER_RADIUS + self.yellow_mass <= self.W:
                self.yellow_x = self.yellow_x + self.yellow_vel
        elif np.array_equal(yellow_action, [0, 0, 1, 0]):  # UP
            if self.yellow_y - self.yellow_vel - self.PLAYER_RADIUS - self.yellow_mass >= 0:
                self.yellow_y = self.yellow_y - self.yellow_vel
        elif np.array_equal(yellow_action, [0, 0, 0, 1]):  # DOWN
            if self.yellow_y + self.yellow_vel + self.PLAYER_RADIUS + self.yellow_mass <= self.H:
                self.yellow_y = self.yellow_y + self.yellow_vel

        # 2. Eventek kezelése
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    quit()

            if event.type == self.MASS_LOSS:
                # Játékosok méretét csökkenti
                if self.red_mass > 8:
                    self.red_mass = math.floor(self.red_mass * 0.96)

                if self.yellow_mass > 8:
                    self.yellow_mass = math.floor(self.yellow_mass * 0.96)

        # 3. Pöttyökkel ütközés kezelése
        self.ball_collision()

        # 4. Epizód vége
        game_over = False
        if self.player_collision() or self.step_iteration > self.MAX_FRAMES-1:
            game_over = True
            return self.state, self.red_reward, self.yellow_reward, self.step_iteration, game_over

        # 5. Képernyő frissítése
        self.draw_window()
        self.state = pygame.surfarray.array3d(pygame.display.get_surface())
        self.clock.tick(self.FPS)

        return self.state, self.red_reward, self.yellow_reward, self.step_iteration, game_over

    def ball_collision(self):
        # kezeli ha egy játékos ütközik egy pöttyel
        for ball in self.balls:
            bx = ball[0]
            by = ball[1]

            red_dis = math.sqrt((self.red_x - bx) ** 2 + (self.red_y - by) ** 2)
            yellow_dis = math.sqrt((self.yellow_x - bx) ** 2 + (self.yellow_y - by) ** 2)

            if red_dis <= self.PLAYER_RADIUS + self.red_mass + 2.5:
                self.red_mass = self.red_mass + 1
                self.balls.remove(ball)
                self.red_reward = 1


            elif yellow_dis <= self.PLAYER_RADIUS + self.yellow_mass + 2.5:
                self.yellow_mass = self.yellow_mass + 1
                self.balls.remove(ball)
                self.yellow_reward = 1

    def player_collision(self):
        # kezeli a játékosok ütközését
        dis = math.sqrt((self.yellow_x - self.red_x) ** 2 + (self.yellow_y - self.red_y) ** 2)
        if self.red_mass < self.yellow_mass:
            if dis < (self.yellow_mass + self.red_mass + self.PLAYER_RADIUS) * 1.2:
                self.yellow_mass = math.sqrt(self.yellow_mass ** 2 + self.red_mass ** 2)  # a területtel arányosan nő
                self.red_mass = 0
                self.yellow_reward = 100
                self.red_reward = -100
                return True

        elif self.yellow_mass < self.red_mass:
            if dis < (self.red_mass + self.yellow_mass + self.PLAYER_RADIUS) * 1.2:
                self.red_mass = math.sqrt(self.red_mass ** 2 + self.yellow_mass ** 2)  # a területtel arányosan nő
                self.yellow_mass = 0
                self.red_reward = 100
                self.yellow_reward = -100
                return True

    def get_start_location(self):
        while True:
            stop = True
            x = random.randrange(0, self.W)
            y = random.randrange(0, self.H)
            dis = math.sqrt((x - self.red_x) ** 2 + (y - self.red_y) ** 2)
            if dis <= self.PLAYER_RADIUS + self.red_mass:
                stop = False
            if stop:
                break
        return (x, y)

    def draw_window(self):
        self.WIN.fill((255, 255, 255))

        # kirajzoljuk a pöttyöket
        for ball in self.balls:
            pygame.draw.circle(self.WIN, ball[2], (ball[0], ball[1]), self.BALL_RADIUS)

        # kirajzoljuk a játékosokat
        pygame.draw.circle(self.WIN, (255, 0, 0), (self.red_x, self.red_y), self.PLAYER_RADIUS + round(self.red_mass))
        pygame.draw.circle(self.WIN, (255, 255, 0), (self.yellow_x, self.yellow_y), self.PLAYER_RADIUS + round(self.yellow_mass))
        pygame.display.flip()


if __name__ == '__main__':
    game = Dotsgame_env()
    red_score = 0
    yellow_score = 0

    # Game loop
    while True:
        game_over, red_rew, yellow_rew, iteration= game.step()
        red_score += red_rew
        yellow_score += yellow_rew
        print("Red reward:" + str(red_rew) + "  Yellow reward:" + str(yellow_rew))

        if game_over == True:
            break

    print('Final Scores:')
    print('Red:', red_score)
    print('Yellow:', yellow_score)
    print('Iterations: ', iteration)

    pygame.quit()