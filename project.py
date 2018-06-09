import pygame
import sys
import random
import time
import cv2
import numpy as np
from threading import Thread
import newWebcam
import os

my_path = os.path.abspath(os.path.dirname(__file__))


#
WIDTH = 500
HEIGHT = 750
FPS = 30
shootdelay = 0.08
bulletspeed = -10

# define colors
WHITE = (255,255,255)
BLACK = (0,0,0)
RED = (200,0,0)
GREEN = (0,200,0)
bright_red = (255,0,0)
bright_green = (0,255,0)
YELLOW = (153,153,0)
bright_yellow = (204,204,0)
bright_black = (128,128,128)
BLUE = (30,144,255)
bright_blue = (135,206,250)

# initialize pygame and create window
pygame.init()
pygame.mixer.init()
screen = pygame.display.set_mode((WIDTH,HEIGHT))
pygame.display.set_caption("Space shooting")
clock = pygame.time.Clock()

class Player(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.transform.scale(ship_img,(30,40))
        self.image.set_colorkey(WHITE)
        self.rect = self.image.get_rect()
        self.radius = 16
        # pygame.draw.circle(self.image,RED,self.rect.center,self.radius)
        self.rect.center = (WIDTH/2,HEIGHT -20)
        self.speed = 50
        self.lastshot = 0
        self.shield = 200
        self.lives = 3
        self.hidden = False
        self.hide_timer = pygame.time.get_ticks()
    def update(self):
        if self.hidden and pygame.time.get_ticks() - self.hide_timer > 1000:
            self.hidden = False
            self.rect.center = (WIDTH / 2, HEIGHT - 20)
        if self.rect.x <0:
            self.rect.x = 0
        elif self.rect.right > WIDTH:
            self.rect.right = WIDTH
        if self.rect.bottom > HEIGHT:
            self.rect.bottom = HEIGHT
        elif self.rect.top < HEIGHT -150:
            self.rect.top = HEIGHT -150



    def shoot(self):
        self.bullet = Bullet(self.rect.centerx, self.rect.top)
        if time.time()-self.lastshot > shootdelay:
            self.lastshot = time.time()
            all_sprites.add(self.bullet)
            bullets.add(self.bullet)

    def hide(self):
        self.hidden = True
        self.hide_timer = pygame.time.get_ticks()
        self.rect.center = (WIDTH/2, HEIGHT + 200)


class Enemy(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = random.choice(enemy_img)
        self.image.set_colorkey(BLACK)
        self.image = pygame.transform.scale(self.image, random.choice(size_list))
        self.rect = self.image.get_rect()
        self.radius = int(self.rect.width *0.95 / 2)
        # pygame.draw.circle(self.image,RED,self.rect.center,self.radius)
        self.rect.x = random.randrange(WIDTH - self.rect.width)
        self.rect.y = random.randrange(-100,-40,step=10)
        self.speedy = random.randrange(5,10,step=5)
        self.speedx = random.randrange(-3,3)
    def update(self):
        self.rect.y += self.speedy
        self.rect.x += self.speedx
        if self.rect.top > HEIGHT + 10 or self.rect.left < 0 or self.rect.right > WIDTH:
            self.rect.x = random.randrange(WIDTH - self.rect.width)
            self.rect.y = random.randrange(-100, -40)
            self.speedy = random.randrange(1, 8)

class Bullet(pygame.sprite.Sprite):
    def __init__(self,x,y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.transform.scale(bullet_img,(10,20))

        self.rect = self.image.get_rect()
        self.rect.bottom = y
        self.rect.centerx = x
        self.speedy = bulletspeed
    def update(self):
        self.rect.y += self.speedy
        if self.rect.top < 0:
            self.kill()
class ScoreBoard():
    def __init__(self, font_size=20, score=0):
        self.x = WIDTH - 150
        self.y = 20
        self.score = score
        self.font = pygame.font.Font('freesansbold.ttf', font_size)

    def display(self, score):
        result_srf = self.font.render('Score : %s' % score, True, WHITE)
        result_rect = result_srf.get_rect()
        result_rect.topleft = (WIDTH - 150, 20)
        screen.blit(result_srf, result_rect.topleft)
class Explosion(pygame.sprite.Sprite):
    def __init__(self, center, size):
        pygame.sprite.Sprite.__init__(self)
        self.size = size
        self.image = explosion_anim[self.size][0]
        self.rect = self.image.get_rect()
        self.rect.center = center
        self.frame = 0
        self.last_update = pygame.time.get_ticks()
        self.frame_rate = 30
    def update(self):
        now = pygame.time.get_ticks()
        if now - self.last_update > self.frame_rate:
            self.last_update = now
            self.frame += 1
            if self.frame == len(explosion_anim[self.size]):
                self.kill()
            else:
                center = self.rect.center
                self.image = explosion_anim[self.size][self.frame]
                self.rect = self.image.get_rect()
                self.rect.center = center


#Spawn new enemy
def new_enemy():
    evil = Enemy()
    all_sprites.add(evil)
    enemy.add(evil)
#init button
def text_objects(text, font):
    textSurface = font.render(text, True, WHITE)
    return textSurface, textSurface.get_rect()

def button(msg, x, y, w, h, ic, ac, action=None):
    mouse = pygame.mouse.get_pos()
    click = pygame.mouse.get_pressed()

    if x + w > mouse[0] > x and y + h > mouse[1] > y:
        pygame.draw.rect(screen, ac, (x, y, w, h))
        if click[0] == 1 and action != None:
            action()
    else:
        pygame.draw.rect(screen, ic, (x, y, w, h))

    smallText = pygame.font.Font("freesansbold.ttf", 20)
    textSurf, textRect = text_objects(msg, smallText)
    textRect.center = ((x + (w / 2)), (y + (h / 2)))
    screen.blit(textSurf, textRect)

#init start menu
def start_menu():
    global starting
    starting = True


    while starting:
        screen.fill(BLACK)
        screen.blit(background, (0,0))
        largeText = pygame.font.Font('freesansbold.ttf', 30)
        TextSurf, TextRect = text_objects("Space shooter", largeText)
        TextRect.center = ((WIDTH / 2), (HEIGHT / 2))
        screen.blit(TextSurf, TextRect)
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                pygame.quit()
        button("Keyboard", WIDTH / 2 - 50, HEIGHT / 2 + 200, 100, 40, YELLOW, bright_yellow,change1 )
        button("Webcam", WIDTH / 2 - 50, HEIGHT / 2 + 250, 100, 40, GREEN, bright_green,change2 )
        button("ABOUT",10,700,100,40, BLACK,bright_black, about)
        button("QUIT", WIDTH / 2 - 50, HEIGHT / 2 + 300, 100, 40, RED, bright_red, quit1)
        #     if event.type == pygame.KEYUP:
        #         starting = False
        pygame.display.flip()

#thay doi bien phu
def change1():
    global starting, bien_phu
    starting = False
    bien_phu = -1
def change2():
    global starting,bien_phu
    starting = False
    bien_phu = -2
#quit game
def quit1():
    global starting,ending
    starting = False
    ending = False
    pygame.quit()
    quit()

#thong tin info
def about():
    global abot
    abot = True
    while abot:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
        screen.fill(BLACK)
        screen.blit(background, background_rect)
        largeText = pygame.font.Font('freesansbold.ttf', 40)
        largeText1 = pygame.font.Font('freesansbold.ttf', 30)

        TextSurf, TextRect = text_objects("Developed by :", largeText)
        TextRect.center = ((WIDTH / 2), (HEIGHT / 2 - 220))
        screen.blit(TextSurf, TextRect)

        TextSurf1, TextRect1 = text_objects("Trinh Tuan Long", largeText1)
        TextSurf2, TextRect2 = text_objects("Nguyen Tien Nhan", largeText1)
        TextSurf3, TextRect3 = text_objects("Le Minh Viet", largeText1)
        TextSurf4, TextRect4 = text_objects("Chu Minh Hoang", largeText1)

        TextRect1.center = ((WIDTH / 2), (HEIGHT / 2 - 160))
        TextRect2.center = ((WIDTH / 2), (HEIGHT / 2 - 120))
        TextRect3.center = ((WIDTH / 2), (HEIGHT / 2 - 80))
        TextRect4.center = ((WIDTH / 2), (HEIGHT / 2 - 40))

        screen.blit(TextSurf1, TextRect1)
        screen.blit(TextSurf2, TextRect2)
        screen.blit(TextSurf3, TextRect3)
        screen.blit(TextSurf4, TextRect4)

        button("BACK", 50, 50, 110, 40, BLUE, bright_blue, back)

        pygame.display.flip()

def back():
    global abot
    abot = False
    start_menu()
#end menu
def end_menu():
    global ending, game_over
    ending = True
    while ending:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
        clock.tick(FPS)
        screen.fill(BLACK)
        screen.blit(background, background_rect)
        largeText = pygame.font.Font('freesansbold.ttf', 40)
        TextSurf, TextRect = text_objects(str(score.score), largeText)
        TextSurf1, TextRect1 = text_objects("Your score :", largeText)
        TextRect1.center = ((WIDTH/2), (HEIGHT / 2 - 300))
        TextRect.center = ((WIDTH/2), (HEIGHT /1.75 - 280))
        screen.blit(TextSurf, TextRect)
        screen.blit(TextSurf1, TextRect1)
        button("AGAIN", WIDTH / 2 - 50, HEIGHT / 2 + 200, 100, 40, GREEN, bright_green, again )
        button("QUIT", WIDTH / 2 - 50, HEIGHT / 2 + 250, 100, 40, RED, bright_red, quit1)
        pygame.display.flip()
#tro lai vong lap
def again():
    global ending,game_over
    ending = False
    game_over = True

#thanh shield bar
def draw_shield_bar(surf,x,y,pct):
    if pct < 0:
        pct = 0
    bar_length = 100
    bar_height = 20
    fill = (pct/200)*bar_length
    outline_rect = pygame.Rect(x,y,bar_length,bar_height)
    fill_rect = pygame.Rect(x,y,fill,bar_height)
    pygame.draw.rect(surf,GREEN,fill_rect)
    pygame.draw.rect(surf,WHITE,outline_rect,2)

#thanh lives
def draw_lives(surf,x,y,lives,img):
    for i in range(lives):
        img_rect = img.get_rect()
        img_rect.x = x + 30*i
        img_rect.y = y
        surf.blit(img,img_rect)



# Load images
background = pygame.image.load(os.path.join(my_path, "D:\\Download by Nhan\\galaxy.jpg")).convert()
background_rect = background.get_rect()
ship_img = pygame.image.load(os.path.join(my_path, "Image\\player.png")).convert()
ship_mini_img = pygame.transform.scale(ship_img, (30,30))
ship_mini_img.set_colorkey(BLACK)
bullet_img = pygame.image.load(os.path.join(my_path, "D:\\Download by Nhan\\sperm.png"))
enemy_img = []
enemy_list = ['enemy0.png','enemy1.png','enemy2.png','enemy3.png',]
for img in enemy_list:
    enemy_img.append(pygame.image.load(os.path.join(my_path, "Image\\"+img)).convert())
size_list = [(40,40),(70,70),(20,20),(30,30),(50,50),(60,60)]
##explosion
explosion_anim={}
explosion_anim['lg'] = []
for i in range(9):
    file_name = 'Image\\regularExplosion0{}.png'.format(i)
    img = pygame.image.load(os.path.join(my_path, file_name)).convert()
    img.set_colorkey(BLACK)
    img_lg = pygame.transform.scale(img, (75,75))
    explosion_anim['lg'].append(img_lg)
##sonic explosion
explosion_anim['sn'] = []
for i in range(9):
    file_name1 = 'Image\\sonicExplosion0{}.png'.format(i)
    img = pygame.image.load(os.path.join(my_path, file_name1)).convert()
    img.set_colorkey(BLACK)
    explosion_anim['sn'].append(img)


#Load music
explosion_music = pygame.mixer.Sound(os.path.join(my_path, "Sound\\explosion.wav"))
bullet_music = pygame.mixer.Sound(os.path.join(my_path, "Sound\\bullet.wav"))
pygame.mixer.music.load("Sound\\nhacnen.wav")
pygame.mixer.music.set_volume(2)

#Game loop
running = True
game_over = True
bien_phu = -100
c = -1

pygame.mixer.music.play(loops = -1)
while running:
    if game_over:
        start_menu()
        cam = True
        game_over = False
        # Main
        all_sprites = pygame.sprite.Group()
        player = Player()
        score = ScoreBoard()
        enemy = pygame.sprite.Group()
        bullets = pygame.sprite.Group()
        all_sprites.add(player)
        for i in range(30):
            new_enemy()
        score.score = 0
    # keep loop running at the same speed
    clock.tick(FPS)
    # Process input (events)
    for event in pygame.event.get():
       # closing window
        if event.type == pygame.QUIT:
            running = False
    keys = pygame.key.get_pressed()
    if bien_phu == -1:
        if keys[pygame.K_LEFT]:
            player.rect.x -= 10
        if keys[pygame.K_RIGHT]:
            player.rect.x += 10
        if keys[pygame.K_UP]:
            player.rect.y -= 10
        if keys[pygame.K_DOWN]:
            player.rect.y += 10
        player.shoot()
    if bien_phu == -2:
        if cam:
            vision = newWebcam.Webcam()
            vision.thread_webcam(1,1)
            cam = False
        posX, posY = vision.get_currentPos()
        if posX != 0 and posY != 0:
            player.rect.x = 2*posX
            player.rect.y = 2*posY
        if vision.get_len() != 0:
            print("0")
    if keys[pygame.K_p]:
        FPS += 3
    # Update
    all_sprites.update()

    #hits
    hits1 = pygame.sprite.groupcollide(bullets,enemy,True,True)
    for hit in hits1:
        bullet_music.play()
        new_enemy()
        expl_lg = Explosion(hit.rect.center,'lg')
        all_sprites.add(expl_lg)
    hits2 = pygame.sprite.spritecollide(player,enemy,True,pygame.sprite.collide_circle)
    for hit in hits2:
        player.shield -= hit.radius *2
        new_enemy()
        if player.shield <= 0:
            explosion_music.play()
            expl_sn = Explosion(hit.rect.center,'sn')
            all_sprites.add(expl_sn)
            player.hide()
            player.lives -= 1
            player.shield = 200
    if player.lives == 0 and not expl_sn.alive():
        if not cam:
            vision.endend()
        end_menu()
        pygame.time.delay(100)



    # Draw / render
    screen.fill(BLACK)
    screen.blit(background, background_rect)
    all_sprites.draw(screen)
    if hits1:
        score.score += 1
    score.display(score.score)
    draw_shield_bar(screen,5,5,player.shield)
    draw_lives(screen,5,30,player.lives,ship_mini_img)
    # *after* drawing everything, flip the display
    pygame.display.flip()



pygame.quit()


















