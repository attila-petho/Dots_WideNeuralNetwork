import pygame
import random
import math
from decimal import *
import numpy as np

class Dotsgame_env:

    def __init__(self, max_steps=2000, FPS = 30, show_horizon=False):
        pygame.init()
        getcontext().prec = 1
        # Változók
        self.max_steps = max_steps           # max ennyi lépés lehet egy epizódban
        self.show_horizon = show_horizon     # látótér megjelenítése
        self.PLAYER_RADIUS = 10              # játékosok kezdő sugara
        self.START_VEL = 5                   # játékosok kezdő sebessége
        self.BALL_RADIUS = 5                 # pöttyök mérete
        self.N_BALLS = 100                   # pöttyök száma
        self.frame_reward = Decimal('0.001') # jutalom/lépés
        self.horizon_radius = 100            # játékosok látóterének mérete (kontúrtól számítva)

        # Képernyő inicializálása
        self.FPS = FPS
        self.W = 640
        self.H = 480
        self.WIN = pygame.display.set_mode((self.W, self.H))
        self.COLORS = [(255, 128, 0), (128, 255, 0), (0, 255, 0), (0, 255, 128), (0, 255, 255), (0, 128, 255),
                       (0, 255, 191), (0, 0, 255), (115, 0, 240), (255, 0, 255), (255, 0, 140), (128, 128, 128),
                       (0, 0, 0), (0, 181, 26)]
        self.SCORE_FONT = pygame.font.SysFont("comicsans", 25)
        pygame.display.set_caption("Dots AI")
        self.clock = pygame.time.Clock()

        # Játék inicializálása
        self.balls = []
        self.reset()

    def reset(self):
        # Alaphelyzetbe állítja a környezetet
        self.balls.clear()
        self.red_mass = 1
        self.yellow_mass = 1
        self.red_score = 0
        self.yellow_score = 0
        self.red_x = random.randrange(0, self.W)
        self.red_y = random.randrange(0, self.H)
        self.yellow_x, self.yellow_y = self.get_start_location()
        self.create_balls()
        self.step_iteration = 0

    def create_balls(self):
        # Létrehozza a pöttyöket
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

    def get_state(self):
        # Létrehozza a megfigyeléseket
        # Fokonként eltároljuk a pöttyök távolságát a játékosoktól, ha a látótéren belül vannak
        red_polar = np.zeros(360)
        yellow_polar = np.zeros(360)

        for ball in self.balls:
            bx = ball[0]
            by = ball[1]

            # Távolságok
            red_dis = math.sqrt((self.red_x - bx) ** 2 + (self.red_y - by) ** 2)
            yellow_dis = math.sqrt((self.yellow_x - bx) ** 2 + (self.yellow_y - by) ** 2)

            # Piros polárkoordinátás vektora
            if red_dis <= self.PLAYER_RADIUS+self.red_mass+self.horizon_radius:
                phi1 = round(180 + math.degrees(math.atan2((by - self.red_y), (bx - self.red_x))))
                red_polar[int(phi1)-1] = red_dis

            # Sárga polárkoordinátás vektora
            if yellow_dis <= self.PLAYER_RADIUS+self.yellow_mass+self.horizon_radius:
                phi2 = round(180 + math.degrees(math.atan2((by - self.yellow_y), (bx - self.yellow_x))))
                yellow_polar[int(phi2)-1] = yellow_dis

        # Ellenfél iránya és távolsága
        player_dis = math.sqrt((self.red_x - self.yellow_x) ** 2 + (self.red_y - self.yellow_y) ** 2)
        if player_dis <= (2*self.PLAYER_RADIUS + self.red_mass + self.yellow_mass + self.horizon_radius):
            phi1 = round(180 + math.degrees(math.atan2((self.yellow_y - self.red_y), (self.yellow_x - self.red_x))))  # PIROS
            phi2 = round(180 + math.degrees(math.atan2((self.red_y - self.yellow_y), (self.red_x - self.yellow_x))))  # SÁRGA
            red_polar[int(phi1)-1] = -player_dis + (self.PLAYER_RADIUS + self.yellow_mass)      # az ellenfél (kontúrjának) távolságát negatív előjellel vesszük
            yellow_polar[int(phi2)-1] = -player_dis + (self.PLAYER_RADIUS + self.red_mass)      # az ellenfél (kontúrjának) távolságát negatív előjellel vesszük

        # Játékosok távolsága a falaktól
        red_wall = np.zeros(4)
        if self.red_x <= self.PLAYER_RADIUS + self.red_mass + self.horizon_radius:                   # BAL
            red_wall[0] = self.red_x
        if  self.W <= self.red_x + self.PLAYER_RADIUS + self.red_mass + self.horizon_radius:         # JOBB
            red_wall[1] = self.W - self.red_x
        if self.red_y <= self.PLAYER_RADIUS + self.red_mass + self.horizon_radius:                   # FENT
            red_wall[2] = self.red_y
        if  self.H <= self.red_y + self.PLAYER_RADIUS + self.red_mass + self.horizon_radius:         # LENT
            red_wall[3] = self.H - self.red_y

        yellow_wall = np.zeros(4)
        if self.yellow_x <= self.PLAYER_RADIUS + self.yellow_mass + self.horizon_radius:             # BAL
            yellow_wall[0] = self.yellow_x
        if self.W <= self.yellow_x + self.PLAYER_RADIUS + self.yellow_mass + self.horizon_radius:    # JOBB
            yellow_wall[1] = self.W - self.yellow_x
        if self.yellow_y <= self.PLAYER_RADIUS + self.yellow_mass + self.horizon_radius:             # FENT
            yellow_wall[2] = self.yellow_y
        if self.H <= self.yellow_y + self.PLAYER_RADIUS + self.yellow_mass + self.horizon_radius:    # LENT
            yellow_wall[3] = self.H - self.yellow_y

        # Méretek
        size = np.array([self.PLAYER_RADIUS + self.red_mass, self.PLAYER_RADIUS + self.yellow_mass])

        # Megfigyelésvektorok létrehozása
        red_state = np.concatenate((red_polar, red_wall, size))
        yellow_state = np.concatenate((yellow_polar, yellow_wall, size))
        # Megfigyelésvektor normalizálása (a látótér mérete alapján)
        red_state = red_state / (self.PLAYER_RADIUS + self.red_mass + self.horizon_radius)
        yellow_state = yellow_state / (self.PLAYER_RADIUS + self.yellow_mass + self.horizon_radius)

        return [red_state, yellow_state]

    def step(self, red_action, yellow_action):
        self.step_iteration += 1
        self.red_reward = -self.frame_reward       # pirosnak minden lépés: - jutalom
        self.yellow_reward = self.frame_reward     # sárgának minden lépés: + jutalom

        # 1. Sebességek kezelése
        self.red_vel = self.START_VEL - round(self.red_mass / 14)
        if self.red_vel <= 1:
            self.red_vel = 1

        self.yellow_vel = self.START_VEL - round(self.yellow_mass / 14)
        if self.yellow_vel <= 1:
            self.yellow_vel = 1

        # 2. Játékosok mozgásának kezelése
        if np.array_equal(red_action, [1, 0, 0, 0]):        # BALRA
            if self.red_x - self.red_vel - self.PLAYER_RADIUS - self.red_mass >= 0:
                self.red_x = self.red_x - self.red_vel
        elif np.array_equal(red_action, [0, 1, 0, 0]):      # JOBBRA
            if self.red_x + self.red_vel + self.PLAYER_RADIUS + self.red_mass <= self.W:
                self.red_x = self.red_x + self.red_vel
        elif np.array_equal(red_action, [0, 0, 1, 0]):      # FEL
            if self.red_y - self.red_vel - self.PLAYER_RADIUS - self.red_mass >= 0:
                self.red_y = self.red_y - self.red_vel
        elif np.array_equal(red_action, [0, 0, 0, 1]):      # LE
            if self.red_y + self.red_vel + self.PLAYER_RADIUS + self.red_mass <= self.H:
                self.red_y = self.red_y + self.red_vel

        if np.array_equal(yellow_action, [1, 0, 0, 0]):     # BALRA
            if self.yellow_x - self.yellow_vel - self.PLAYER_RADIUS - self.yellow_mass >= 0:
                self.yellow_x = self.yellow_x - self.yellow_vel
        elif np.array_equal(yellow_action, [0, 1, 0, 0]):   # JOBBRA
            if self.yellow_x + self.yellow_vel + self.PLAYER_RADIUS + self.yellow_mass <= self.W:
                self.yellow_x = self.yellow_x + self.yellow_vel
        elif np.array_equal(yellow_action, [0, 0, 1, 0]):   # FEL
            if self.yellow_y - self.yellow_vel - self.PLAYER_RADIUS - self.yellow_mass >= 0:
                self.yellow_y = self.yellow_y - self.yellow_vel
        elif np.array_equal(yellow_action, [0, 0, 0, 1]):   # LE
            if self.yellow_y + self.yellow_vel + self.PLAYER_RADIUS + self.yellow_mass <= self.H:
                self.yellow_y = self.yellow_y + self.yellow_vel

        # 3. Eventek kezelése
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    quit()

        # 4. Méretcsökkenés kezelése
        if self.step_iteration % 60 == 0:
            if self.red_mass > 10:
                self.red_mass = math.floor(self.red_mass * 0.97)
            if self.yellow_mass > 10:
                self.yellow_mass = math.floor(self.yellow_mass * 0.97)

        # 5. Pöttyökkel és pontszámok ütközés kezelése
        self.ball_collision()

        # 6. Megfigyelések
        state = self.get_state()

        # 7. Epizód vége
        game_over = False
        reward = [self.red_reward, self.yellow_reward]
        score = [self.red_score, self.yellow_score]
        if self.player_collision() or self.step_iteration > self.max_steps-1:
            game_over = True
            reward = [self.red_reward, self.yellow_reward]
            score = [self.red_score, self.yellow_score]
            return state, reward, score, self.step_iteration, game_over

        # 8. Képernyő frissítése
        self.draw_window()
        self.clock.tick(self.FPS)

        return state, reward, score, self.step_iteration, game_over

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
                self.red_reward = 0.01
                self.red_score += 1


            elif yellow_dis <= self.PLAYER_RADIUS + self.yellow_mass + 2.5:
                self.yellow_mass = self.yellow_mass + 1
                self.balls.remove(ball)
                self.yellow_reward = 0.01
                self.yellow_score += 1

    def player_collision(self):
        # kezeli a játékosok ütközését
        dis = math.sqrt((self.yellow_x - self.red_x) ** 2 + (self.yellow_y - self.red_y) ** 2)
        if dis < (self.yellow_mass + self.red_mass + self.PLAYER_RADIUS * 2):
            if self.red_mass < self.yellow_mass:
                self.yellow_mass = math.sqrt(self.yellow_mass ** 2 + self.red_mass ** 2)
                self.red_mass = 0
                self.yellow_reward = 1
                self.red_reward = -1
                self.yellow_score += 100
                return True

            elif self.yellow_mass <= self.red_mass:
                self.red_mass = math.sqrt(self.red_mass ** 2 + self.yellow_mass ** 2)
                self.yellow_mass = 0
                self.red_reward = 1
                self.yellow_reward = -1
                self.red_score += 100
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
        pygame.draw.circle(self.WIN, (255, 0, 0), (self.red_x, self.red_y), self.PLAYER_RADIUS + self.red_mass)
        pygame.draw.circle(self.WIN, (245, 225, 0), (self.yellow_x, self.yellow_y), self.PLAYER_RADIUS + self.yellow_mass)
        if self.show_horizon:
            pygame.draw.circle(self.WIN, (255, 0, 0), (self.red_x, self.red_y), self.PLAYER_RADIUS + self.red_mass + self.horizon_radius, width=1)
            pygame.draw.circle(self.WIN, (245, 225, 10), (self.yellow_x, self.yellow_y), self.PLAYER_RADIUS + self.yellow_mass + self.horizon_radius, width=1)

        # kiírjuk a pontszámokat
        red_score_text = self.SCORE_FONT.render("Red score: " + str(self.red_score), True, (0, 0, 0))
        yellow_score_text = self.SCORE_FONT.render("Yellow score: " + str(self.yellow_score), True, (0, 0, 0))
        self.WIN.blit(red_score_text, (self.W - red_score_text.get_width() - 5, 5))
        self.WIN.blit(yellow_score_text, (5, 5))
        pygame.display.flip()