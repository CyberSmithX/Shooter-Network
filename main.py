import pygame
from os import listdir
import socket

# * INITIALIAZ PYGAME
pygame.init()

# * INITIALIAZ NETWORK
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
try:
    server.connect((socket.gethostname(), 55555))
except:
    pass

player_pos = [[400, 400], [500, 400]]

# * SCREEN SETUP
SCREEN_WIDTH = 600
SCREEN_HEIGHT = 500
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

# * BACKGROUND VARIBALES
BG = (65, 107, 65)

# * PLAYER VARIABLES
moving_left = False
moving_right = False
GRAVITY = 0.75

# * CLOCK VARS
clock = pygame.time.Clock()
FPS = 60

#* DRAW BG
RED = (255, 0, 0)

def draw_bg():
	screen.fill(BG)
	pygame.draw.line(screen, RED, (0, 400), (SCREEN_WIDTH, 400))


# *----------------------------------- CLASSES --------------------------------------------#
class Soldier(pygame.sprite.Sprite):
    def __init__(self, char_type, x, y, speed, scale):
        pygame.sprite.Sprite.__init__(self)
        self.speed = speed
        self.flip = False
        self.in_air = False
        self.jump = False
        self.vel_y = 0
        self.animation_list = []
        self.frame_index = 0
        self.action = 0
        self.update_time = pygame.time.get_ticks()

        animations = ["Idle", "Run", "Jump", "Death"]

        for animation in animations:

            num_of_frames = len(listdir(f"img/{char_type}/{animation}"))
            temp_list = []

            for i in range(num_of_frames):
                img = pygame.image.load(f"img/{char_type}/{animation}/{i}.png")
                img = pygame.transform.scale(
                    img, (img.get_width() * scale, img.get_height() * scale)
                )
                temp_list.append(img)
            
            self.animation_list.append(temp_list)

        self.image = self.animation_list[self.action][self.frame_index]
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)

    def move(self, moving_left, moving_right):
        global server
        dx = 0
        dy = 0
        
        if moving_right:
            dx += self.speed
            self.flip = False
            tup = [self.rect.x, self.rect.y]
            server.send(str(tup).encode())

        if moving_left:
            dx -= self.speed
            self.flip = True
            tup = [self.rect.x, self.rect.y]
            server.send(str(tup).encode())
        

        if self.jump == True and self.in_air == False:
            self.vel_y = -11
            self.jump = False
            self.in_air = True
            tup = (self.rect.x, self.rect.y)
            server.send(str(tup).encode())

        self.vel_y += GRAVITY
        if self.vel_y > 10:
            self.vel_y

        dy += self.vel_y

        if self.rect.bottom + dy > 400:
            dy = 400 - self.rect.bottom
            self.in_air = False

        self.rect.x += dx
        self.rect.y += dy


    def update_animation(self):
        
        ANIMATION_COOLDOWN = 100

        self.image = self.animation_list[self.action][self.frame_index]

        if pygame.time.get_ticks() - self.update_time > ANIMATION_COOLDOWN:
            self.update_time = pygame.time.get_ticks()
            self.frame_index += 1
        if self.frame_index >= len(self.animation_list[self.action]):
            self.frame_index = 0

    def update_action(self, new_action):
        if self.action != new_action:
            self.update_time = pygame.time.get_ticks()
            self.frame_index = 0
            self.action = new_action

    def draw(self):
        screen.blit(pygame.transform.flip(self.image, self.flip, False), self.rect)


# * DEFINE PLAYER
player = Soldier("player", player_pos[0][0], player_pos[0][1], 5, 3)
enemy = Soldier("enemy", player_pos[1][0], player_pos[1][1], 5, 3)

#! Do Not Edit !
run = True
while run:
    # * LOOP CONTROLS
    clock.tick(FPS)
    
    draw_bg()

    # * PLAYER CONTROLS
    player.draw()
    enemy.draw()
    player.move(moving_left, moving_right)
    if player.in_air == True:
        player.update_action(2) #: Run animation
    elif moving_left or moving_right:
        player.update_action(1) #: Jump animation
    else:
        player.update_action(0)#: Idle animation
    player.update_animation()
    enemy.update_animation()

    # * EVENT CONTROLS
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
            server.send("CLOSING APPLICATION...".encode())
            server.close()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                moving_left = True
            if event.key == pygame.K_RIGHT:
                moving_right = True
            if event.key == pygame.K_UP:
                player.jump = True

        if event.type == pygame.KEYUP:
            if event.key == pygame.K_LEFT:
                moving_left = False
            if event.key == pygame.K_RIGHT:
                moving_right = False

    pygame.display.update()

pygame.quit()
