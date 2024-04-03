import pygame, sys
from pygame.locals import *
from random import randint, choice
from math import sin

# Basic setup
pygame.init()
clock = pygame.time.Clock()
FPS = 60

SCREEN_WIDTH = 400
SCREEN_HEIGHT = 600

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("少林功夫好嘢！")

# Upload images
bg_image = pygame.image.load("images/bg_img.png").convert_alpha()
bg_image = pygame.transform.scale(bg_image, (400, 600))

game_over_image = pygame.image.load("images/game_over_img.png").convert_alpha()
game_over_image = pygame.transform.scale(game_over_image, (400, 600))

soccer_field = pygame.image.load("images/soccer_field.png").convert_alpha()
soccer_field = pygame.transform.scale(soccer_field, (SCREEN_WIDTH, SCREEN_HEIGHT))

ball_img = pygame.image.load("images/ball.png").convert_alpha()
health_img = pygame.image.load("images/health.png").convert_alpha()
bottle_img = pygame.image.load("images/bottle.png").convert_alpha()

health_img_small = pygame.image.load("images/health.png").convert_alpha()
health_img_small = pygame.transform.scale(health_img_small, (20, 20))

# Buttons
start_btn_img = pygame.image.load("images/start_btn.png").convert_alpha()
restart_btn_img = pygame.image.load("images/restart_btn.png").convert_alpha()


# Music/ Sound
bg_music = pygame.mixer.Sound("sound/theme.mp3")
bg_music.play(-1)

ball_sound = pygame.mixer.Sound("sound/football.mp3")
ball_sound.set_volume(0.7)

button_sound = pygame.mixer.Sound("sound/button.mp3")
button_sound.set_volume(0.1)

health_sound = pygame.mixer.Sound("sound/health.wav")
health_sound.set_volume(0.6)

bottle_sound = pygame.mixer.Sound("sound/glass_broke.mp3")

# Variables
item_boxes = {
    'Ball'   : ball_img,
    'Health' : health_img,
    'Bottle' : bottle_img
}

# Stupid Monk
class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.alive = True
        self.image = pygame.image.load("images/monk.png").convert_alpha()
        self.image.set_colorkey((255, 255, 255))
        self.image = pygame.transform.scale(self.image, (85, 100))
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.score = 0
        self.health = 3
        self.hit = False
        self.lose = False
        self.hurt_duration = 1000
        self.hurt_time = 0

    def draw(self):
        screen.blit(self.image, self.rect)
        self.image.set_colorkey((255, 255, 255))

    def movement(self):
        dx = 0
        key = pygame.key.get_pressed()
        if self.alive:
            if key[pygame.K_LEFT]:
                dx -= 8
            if key[pygame.K_RIGHT]:
                dx += 8

        if self.rect.left + dx <= 0 or self.rect.right + dx >= SCREEN_WIDTH:
            dx = 0

        self.rect.x += dx

    def hurt(self):
        if not self.hit:
            self.hurt_time = pygame.time.get_ticks()
            self.image.set_alpha(255)
            
        elif self.hit:
            alpha = self.wave_value()
            self.image.set_alpha(alpha)
            current_time = pygame.time.get_ticks()
            if current_time - self.hurt_time >= self.hurt_duration:
                self.hit = False
                
    def wave_value(self):
        value = sin(pygame.time.get_ticks())
        if value >= 0: return 255
        else: return 0            
        
    def check_game_over(self):
        if self.health <= 0:
            self.lose = True            
                
    def update(self):
        self.movement()
        self.draw()
        self.check_game_over()
        self.hurt()
        self.wave_value()

class Item(pygame.sprite.Sprite):
    def __init__(self, item_type, speed):
        super().__init__()
        self.item_type = item_type
        self.image = item_boxes[self.item_type]
        if self.item_type == "Bottle":
            self.image = pygame.transform.scale(self.image, (40, 60))
        else:
            self.image = pygame.transform.scale(self.image, (40, 40))
            
        self.rect = self.image.get_rect()
        self.rect.center = (randint(20, 380), -20)
        self.speed = speed

    def movement(self):
        self.rect.y += self.speed
        if self.rect.y >= SCREEN_HEIGHT + 20:
            self.kill()

    def collision(self):
        if pygame.sprite.spritecollide(player, item_group, True):
            if self.item_type == "Ball":
                player.score += 100
                ball_sound.play()
            if self.item_type == "Health" and player.health < 5:
                player.health += 1
                health_sound.play()
                if player.health >= 5:
                    player.health = 5
            if self.item_type == "Bottle":
                player.health -= 1
                player.hit = True
                bottle_sound.play()
                    
    def update(self):
        self.movement()
        self.collision()
        
#button class
class Button():
	def __init__(self,x, y, image, scale):
		width = image.get_width()
		height = image.get_height()
		self.image = pygame.transform.scale(image, (int(width * scale), int(height * scale)))
		self.rect = self.image.get_rect()
		self.rect.topleft = (x, y)
		self.clicked = False

	def draw(self, surface):
		action = False

		#get mouse position
		pos = pygame.mouse.get_pos()

		#check mouseover and clicked conditions
		if self.rect.collidepoint(pos):
			if pygame.mouse.get_pressed()[0] == 1 and self.clicked == False:
				action = True
				self.clicked = True

		if pygame.mouse.get_pressed()[0] == 0:
			self.clicked = False

		#draw button
		surface.blit(self.image, (self.rect.x, self.rect.y))

		return action

# Draw text
font = pygame.font.SysFont('Futura', 30)
score_font = pygame.font.SysFont('Futura', 50)
def draw_text(text, font, color, x, y):
    img = font.render(text, True, color)
    screen.blit(img, (x, y))
    
# Instances
player = Player(SCREEN_WIDTH // 2, 550)
item_group = pygame.sprite.Group()
start_button = Button(SCREEN_WIDTH // 2 - 60, SCREEN_HEIGHT // 2 - 30, start_btn_img, 0.5)
restart_button = Button(SCREEN_WIDTH // 2 - 60, SCREEN_HEIGHT // 2 + 120, restart_btn_img, 1)

# Timer for item to spawn
item_timer = pygame.USEREVENT + 1
pygame.time.set_timer(item_timer, 750)

# Timer for countdown
countdown = 60
last_count = pygame.time.get_ticks()

# Screen Transition
game_start = False
game_over = False

# Main Game Loop
run = True
while run:
    clock.tick(FPS)
    if not game_start:
        screen.blit(bg_image, (0, 0))
        if start_button.draw(screen):
            button_sound.play()
            game_start = True

    else:
        if not game_over:
            screen.blit(soccer_field, (0, 0))
            draw_text('Health: ', font, (240, 255, 240), 10, 20)
            draw_text('Score:   ' + str(player.score), font, (240, 255, 240), 10, 45)
            draw_text('Timer:   ' + str(countdown), font, (240, 255, 240), 10, 70)
            for i in range(player.health):
                screen.blit(health_img_small, (85 + (i * 20), 20))
                
            # Game over condition
            if countdown <= 0 or player.health <= 0:
                player.alive = False            
                game_over = True

            if countdown > 0:
                count_timer = pygame.time.get_ticks()
                if count_timer - last_count >= 1000:
                    countdown -= 1
                    last_count = count_timer
            
            for event in pygame.event.get():       
                if event.type == item_timer:
                    if 45 <= countdown <= 60:
                        item_group.add(Item(choice(['Ball', 'Ball', 'Ball', 'Ball', 'Ball', 'Ball', 'Ball', 'Ball', 'Bottle', 
                                                    'Bottle', 'Bottle', 'Bottle', 'Bottle', 'Health']), 10))
                    elif 30 <= countdown <= 45:
                        item_group.add(Item(choice(['Ball', 'Ball', 'Ball', 'Ball', 'Ball', 'Ball', 'Ball', 
                                                    'Bottle', 'Bottle', 'Bottle', 'Bottle', 'Bottle', 'Bottle', 'Health']), 13.5))
                    elif 15 <= countdown <= 30:
                        item_group.add(Item(choice(['Ball', 'Ball', 'Ball', 'Ball', 'Ball', 'Ball', 
                                                    'Bottle', 'Bottle', 'Bottle', 'Bottle', 'Bottle', 'Bottle', 'Bottle', 'Health']), 17.5))
                    else:
                        item_group.add(Item(choice(['Bottle', 'Bottle', 'Ball']), 20))
                        
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                    
            player.update()
            item_group.draw(screen)
            item_group.update()
            
        else:
            screen.blit(game_over_image, (0, 0))
            item_group.empty()
            draw_text("GAME OVER", score_font, (0, 0, 0), SCREEN_WIDTH // 2 - 100, 30)
            draw_text("Score: " + str(player.score), score_font, (0, 0, 0), 10, 500)
            if restart_button.draw(screen):
                button_sound.play()
                game_over = False
                countdown = 60
                player.alive = True
                player.health = 3
                player.score = 0
                player.update()
                item_group.draw(screen)
                item_group.update()
                        
    for event in pygame.event.get():        
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    pygame.display.flip()
