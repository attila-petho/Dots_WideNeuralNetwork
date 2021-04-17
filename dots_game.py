import pygame
import random
import math

pygame.init()

# KONSTANSOK
# Képernyő mérete, címe
W, H = 640, 480
WIN = pygame.display.set_mode((W, H))
pygame.display.set_caption("Agar-IO")
FPS = 30

# Színek
COLORS = [(255, 128, 0), (128,255,0),(0,255,0),(0,255,128),(0,255,255),(0, 128, 255), (0,0,255), (0,0,255), (128,0,255),(255,0,255), (255,0,128),(128,128,128), (0,0,0)]

# Betűtípusok
SCORE_FONT = pygame.font.SysFont("comicsans", 25)
ENDSCORE_FONT = pygame.font.SysFont("comicsans", 35)
WINNER_FONT = pygame.font.SysFont("comicsans", 40)

# Sebességek és méretek
PLAYER_RADIUS = 10      # játékosok kezdő sugara
START_VEL = 5           # játékosok kezdő sebessége
BALL_RADIUS = 5         # pöttyök mérete
MASS_LOSS_TIME = 1500	# méretcsökkenés gyorsasága ms-ban
N_BALLS = 100			# pöttyök száma

MASS_LOSS = pygame.USEREVENT + 1
pygame.time.set_timer(MASS_LOSS, MASS_LOSS_TIME)

# Dinamikus változók
balls = []

# FÜGGVÉNYEK
def draw_window(red, yellow, balls):
	WIN.fill((255,255,255))

	# kirajzoljuk a pöttyöket
	for ball in balls:
		pygame.draw.circle(WIN, ball[2], (ball[0], ball[1]), BALL_RADIUS)

	# kirajzoljuk a játékosokat
	pygame.draw.circle(WIN, (255,0,0), (red[0], red[1]), PLAYER_RADIUS + round(red[2]))
	pygame.draw.circle(WIN, (255,255,0), (yellow[0], yellow[1]), PLAYER_RADIUS + round(yellow[2]))

	# kiírjuk a pontszámokat
	red_score_text = SCORE_FONT.render("Red score: " + str(red[3]), True, (0,0,0))
	yellow_score_text = SCORE_FONT.render("Yellow score: " + str(yellow[3]), True, (0,0,0))
	WIN.blit(red_score_text, (W - red_score_text.get_width() - 5, 5))
	WIN.blit(yellow_score_text, (5, 5))

def create_balls(red, yellow, balls, n):
	# létrehozza a pöttyöket
	for i in range(n):
		while True:
			stop = True
			x = random.randrange(5, W-5)
			y = random.randrange(5, H-5)
			red_dis = math.sqrt((x - red[0]) ** 2 + (y - red[1]) ** 2)
			yellow_dis = math.sqrt((x - yellow[0]) ** 2 + (y - yellow[1]) ** 2)
			if red_dis <= PLAYER_RADIUS + red[2] or yellow_dis <= PLAYER_RADIUS + yellow[2]:
					stop = False
			if stop:
				break

		balls.append((x, y, random.choice(COLORS)))

def yellow_handle_movement(keys_pressed, yellow, yellow_vel):
	if keys_pressed[pygame.K_a]:  # LEFT
		if yellow[0] - yellow_vel - PLAYER_RADIUS - yellow[2] >= 0:
			yellow[0] = yellow[0] - yellow_vel
	if keys_pressed[pygame.K_d]:  # RIGHT
		if yellow[0] + yellow_vel + PLAYER_RADIUS + yellow[2] <= W:
			yellow[0] = yellow[0] + yellow_vel
	if keys_pressed[pygame.K_w]:  # UP
		if yellow[1] - yellow_vel - PLAYER_RADIUS - yellow[2] >= 0:
			yellow[1] = yellow[1] - yellow_vel
	if keys_pressed[pygame.K_s]:  # DOWN
		if yellow[1] + yellow_vel + PLAYER_RADIUS + yellow[2] <= H:
			yellow[1] = yellow[1] + yellow_vel

def red_handle_movement(keys_pressed, red, red_vel):
	if keys_pressed[pygame.K_LEFT]:	# LEFT
		if red[0] - red_vel - PLAYER_RADIUS - red[2] >= 0:
			red[0] = red[0] - red_vel
	if keys_pressed[pygame.K_RIGHT]:# RIGHT
		if red[0] + red_vel + PLAYER_RADIUS + red[2] <= W:
			red[0] = red[0] + red_vel
	if keys_pressed[pygame.K_UP]:	# UP
		if red[1] - red_vel - PLAYER_RADIUS - red[2] >= 0:
			red[1] = red[1] - red_vel
	if keys_pressed[pygame.K_DOWN]: # DOWN
		if red[1] + red_vel + PLAYER_RADIUS + red[2] <= H:
			red[1] = red[1] + red_vel

def ball_collision(yellow, red, balls):
	# kezeli ha egy játékos ütközik egy pöttyel
	for ball in balls:
		bx = ball[0]
		by = ball[1]

		red_dis = math.sqrt((red[0] - bx) ** 2 + (red[1] - by) ** 2)
		yellow_dis = math.sqrt((yellow[0] - bx) ** 2 + (yellow[1] - by) ** 2)

		if red_dis <= PLAYER_RADIUS + red[2] + 2.5:
			red[2] = red[2] + 0.5
			balls.remove(ball)
			red[3] += 1
			return red

		elif yellow_dis <= PLAYER_RADIUS + yellow[2] + 2.5:
			yellow[2] = yellow[2] + 0.5
			balls.remove(ball)
			yellow[3] += 1
			return yellow

def player_collision(yellow, red, balls):
	# kezeli a játékosok ütközését
	dis = math.sqrt((yellow[0] - red[0]) ** 2 + (yellow[1] - red[1]) ** 2)
	if red[2] < yellow[2]:
		if dis < (yellow[2] + red[2] + PLAYER_RADIUS)*1.2:
			yellow[2] = math.sqrt(yellow[2] ** 2 + red[2] ** 2)  # a területtel arányosan nő
			red[2] = 0
			yellow[3] += 100
			winner_text = "Yellow wins!"
			draw_winner(red, yellow, winner_text)
			reset_environment(red, yellow, balls)

	elif yellow[2] < red[2]:
		if dis < (red[2] + yellow[2] + PLAYER_RADIUS)*1.2:
			red[2] = math.sqrt(red[2] ** 2 + yellow[2] ** 2)  # a területtel arányosan nő
			yellow[2] = 0
			red[3] += 100
			winner_text = "Red wins!"
			draw_winner(red, yellow, winner_text)
			reset_environment(red, yellow, balls)

def draw_winner(red, yellow, text):
	go_text = WINNER_FONT.render("GAME OVER", True, (0,0,0))
	winner_text = WINNER_FONT.render(text, True, (0,0,0))
	scores_text = ENDSCORE_FONT.render("Red score: " + str(red[3]) + "  Yellow score: " + str(yellow[3]), True, (0, 0, 0))
	WIN.blit(go_text, (W / 2 - go_text.get_width() / 2, H / 2 - go_text.get_height()*2))
	WIN.blit(winner_text, (W/2 - winner_text.get_width() /2, H/2 - winner_text.get_height()/2))
	WIN.blit(scores_text, (W / 2 - scores_text.get_width() / 2, H / 2 + scores_text.get_height()))
	pygame.display.update()
	pygame.time.delay(3000)

def get_start_location(red):
	while True:
		stop = True
		x = random.randrange(0, W)
		y = random.randrange(0, H)
		dis = math.sqrt((x - red[0]) ** 2 + (y - red[1]) ** 2)
		if dis <= PLAYER_RADIUS + red[2]:
			stop = False
		if stop:
			break
	return (x, y)

def reset_environment(red, yellow, balls):
	balls.clear()
	red[2] = 0
	red[3] = 0
	yellow[2] = 0
	yellow[3] = 0
	red[0] = random.randrange(0, W)
	red[1] = random.randrange(0, H)
	yellow[0], yellow[1] = get_start_location(red)
	create_balls(red, yellow, balls, N_BALLS)

def main():
	red_x = random.randrange(0,W)
	red_y = random.randrange(0,H)
	red_mass = 0
	red_score = 0
	red = [red_x, red_y, red_mass, red_score]

	yellow_x, yellow_y = get_start_location(red)
	yellow_mass = 0
	yellow_score = 0
	yellow = [yellow_x, yellow_y, yellow_mass, yellow_score]

	clock = pygame.time.Clock()
	run = True
	create_balls(red, yellow, balls, N_BALLS)

	while run:
		clock.tick(FPS)

		for event in pygame.event.get():
			# X-re kattintáskor bezár
			if event.type == pygame.QUIT:
				run = False
				pygame.quit()

			if event.type == pygame.KEYDOWN:
				# Esc lenyomásakor bezár
				if event.key == pygame.K_ESCAPE:
					run = False
					pygame.quit()

			if event.type == MASS_LOSS:
				# játékosok méretét csökkenti
				if red[2] > 8:
					red[2] = math.floor(red[2] * 0.95)

				if yellow[2] > 8:
					yellow[2] = math.floor(yellow[2] * 0.95)

		# Sebességek
		red_vel = START_VEL - round(red[2] / 14)
		if red_vel <= 1:
			red_vel = 1

		yellow_vel = START_VEL - round(yellow[2] / 14)
		if yellow_vel <= 1:
			yellow_vel = 1

		# Függvényhívások
		keys_pressed = pygame.key.get_pressed()
		yellow_handle_movement(keys_pressed, yellow, yellow_vel)
		red_handle_movement(keys_pressed, red, red_vel)

		ball_collision(yellow, red, balls)
		player_collision(yellow, red, balls)

		draw_window(red, yellow, balls)
		pygame.display.update()

main()