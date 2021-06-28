from os import environ
environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "True"
import pygame
import os
import time
import random
import datetime
import sys
pygame.init()
pygame.font.init()
pygame.mixer.init()
icon = pygame.image.load(os.path.join(
    os.path.dirname(__file__), r"assets\icon.jpg"))
shoot1 = pygame.mixer.Sound(os.path.join(
    os.path.dirname(__file__), r"assets\Shoot1.wav"))
shoot2 = pygame.mixer.Sound(os.path.join(
    os.path.dirname(__file__), r"assets\Shoot2.wav"))
playerExplode = pygame.mixer.Sound(os.path.join(
    os.path.dirname(__file__), r"assets\P-explode.wav"))
enemyExplode = pygame.mixer.Sound(os.path.join(
    os.path.dirname(__file__), r"assets\E-explode.ogg"))
WIDTH, HEIGHT = 950, 800
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Space Shooter")
pygame.display.set_icon(icon)
# Load images
RED_SPACE_SHIP = pygame.image.load(os.path.join(
    os.path.dirname(__file__), r"assets\pixel_ship_red_small.png"))
GREEN_SPACE_SHIP = pygame.image.load(os.path.join(
    os.path.dirname(__file__), r"assets\pixel_ship_green_small.png"))
BLUE_SPACE_SHIP = pygame.image.load(os.path.join(
    os.path.dirname(__file__), r"assets\pixel_ship_blue_small.png"))

# Player player
YELLOW_SPACE_SHIP = pygame.image.load(os.path.join(
    os.path.dirname(__file__), r"assets\pixel_ship_yellow.png"))

# Lasers
RED_LASER = pygame.image.load(os.path.join(
    os.path.dirname(__file__), r"assets\pixel_laser_red.png"))
GREEN_LASER = pygame.image.load(os.path.join(
    os.path.dirname(__file__), r"assets\pixel_laser_green.png"))
BLUE_LASER = pygame.image.load(os.path.join(
    os.path.dirname(__file__), r"assets\pixel_laser_blue.png"))
YELLOW_LASER = pygame.image.load(os.path.join(
    os.path.dirname(__file__), r"assets\pixel_laser_yellow.png"))

# Background
BG = pygame.transform.scale(pygame.image.load(os.path.join(
    os.path.dirname(__file__), r"assets\background-black.png")), (WIDTH, HEIGHT))

# Fonts
titlefont = pygame.font.SysFont('comicsans', 150)
font = pygame.font.SysFont('comicsans', 10)
NORM_FONT = ("Helvetica", 10)

# Color
WHITE = (255, 255, 255)


class Ship:
    def __init__(self, x, y, health=100):
        self.x = x
        self.y = y
        self.health = health
        self.ship_img = None
        self.laser_img = None
        self.lasers = []
        self.cool_down_counter = 0
        self.laser_vel = 7
        self.hit = False
        self.mask = None
        self.laser_mask = None

    def draw(self, window):
        # pygame.draw.rect(window, (255,0,0), (self.x, self.y, 50, 50))
        window.blit(self.ship_img, (self.x, self.y))

    def get_width(self):
        return self.ship_img.get_width()

    def get_height(self):
        return self.ship_img.get_height()

    def get_coords(self):
        return (self.x, self.y)

    def laserAdd(self, CDtime):
        if CDtime > 500:
            self.lasers.append(
                [self.x, self.y, pygame.mask.from_surface(self.laser_img)])
            returno = True
        else:
            returno = False
        return returno

    def delete(self):
        return self.hit

    def shootUpdate(self, window, enemies, isevil=False, score=0, sound=None):
        for laser in self.lasers:
            if isevil:
                laser[1] += self.laser_vel
            else:
                laser[1] -= self.laser_vel
            window.blit(self.laser_img, tuple(laser[0:2]))
            for enemy in enemies:
                ec = enemy.get_coords()
                offset = ec[0] - laser[0], ec[1] - laser[1]
                overlap = self.mask.overlap(laser[2], offset)
                if overlap:
                    self.lasers.remove(laser)
                    enemies.remove(enemy)
                    pygame.mixer.Sound.play(sound)
                    score += 1
        return enemies, score

    def ifBoom(self, player):
        kil = False
        play = player.get_coords()
        offset = self.x - play[0], self.y - play[1]
        overlap = self.mask.overlap(player.getMask(), offset)
        if overlap:
            player.gotHit(12)
            kil = True
        return kil


class Player(Ship):
    def __init__(self, x, y, health=50):
        super().__init__(x, y, health)
        self.ship_img = YELLOW_SPACE_SHIP
        self.laser_img = YELLOW_LASER
        self.mask = pygame.mask.from_surface(self.ship_img)
        self.laser_mask = pygame.mask.from_surface(self.laser_img)
        self.max_health = health
        self.health = health

    def gotHit(self, impact):
        self.health -= impact

    def getHealth(self):
        return self.health

    def drawBar(self):
        pygame.draw.rect(WIN, (255, 0, 0), (self.x, self.y +
                         self.ship_img.get_height()+10, 100, 10))
        if self.health >= 0:
            pygame.draw.rect(WIN, (0, 255, 0), (self.x, self.y +
                             self.ship_img.get_height()+10, self.health*2, 10))

    def getMask(self):
        return self.mask


class Enemy(Ship):
    def __init__(self, x, y, color, health=100):
        super().__init__(x, y, health)
        COLOR_MAP = {
            "red": (RED_SPACE_SHIP, RED_LASER),
            "green": (GREEN_SPACE_SHIP, GREEN_LASER),
            "blue": (BLUE_SPACE_SHIP, BLUE_LASER)
        }
        self.ship_img, self.laser_img = COLOR_MAP[color]
        self.mask = pygame.mask.from_surface(self.ship_img)
        self.laser_mask = pygame.mask.from_surface(self.laser_img)

    def move(self, vel):
        self.y -= vel

    def checkOut(self, lives):
        out = False
        if self.y > HEIGHT:
            lives -= 1
            out = True
        return lives, out


def main():
    WIN.blit(BG, (0, 0))
    run = True
    FPS = 1000
    clock = pygame.time.Clock()
    level = 0
    lives = 5
    player_vel = 5
    main_font = pygame.font.SysFont("comicsans", 50)
    enemies = []
    wave_length = 5
    enemiesDone = 0
    enemy_vel = 1
    enemies_dead = 100000
    player = Player(300, 650)
    time1 = datetime.datetime.today()
    BCDT = datetime.datetime.today()
    MT = datetime.datetime.today()
    score = 0

    def redraw_window(lives, enemies=[], score=0):
        WIN.blit(BG, (0, 0))
        # draw text
        lives_label = main_font.render(f"Lives : {lives}", 1, (255, 255, 255))
        level_label = main_font.render(f"Wave : {level+1}", 1, (255, 255, 255))
        score_label = main_font.render(f"Score : {score}", 1, (255, 255, 255))

        WIN.blit(lives_label, (10, 10))
        WIN.blit(level_label, (WIDTH - level_label.get_width() - 10, 10))
        WIN.blit(score_label, (int(WIDTH/2)-50, 10))
        for enemy in enemies:
            enemy.move(-enemy_vel)
            lives, out = enemy.checkOut(lives)
            rand = random.choice(range(150))
            if rand == 1:
                enemy.laserAdd(10000)
                pygame.mixer.Sound.play(shoot2)
            if out:
                enemies.remove(enemy)
            emeis, unneeded = enemy.shootUpdate(
                WIN, [player], True, sound=playerExplode)
            kil = enemy.ifBoom(player)
            if kil:
                enemies.remove(enemy)
                pygame.mixer.Sound.play(enemyExplode)
                pygame.mixer.Sound.play(playerExplode)
            if emeis != [player]:
                player.gotHit(1)
                pygame.mixer.Sound.play(playerExplode)
                time.sleep(0.1)
            enemy.draw(WIN)
        enemies, score = player.shootUpdate(
            WIN, enemies, score=score, sound=playerExplode)
        player.drawBar()
        player.draw(WIN)
        pygame.display.update()
        return enemies, lives, score

    def loseScreen(nlost=False, score=0):
        music = pygame.mixer.music.load(os.path.join(
            os.path.dirname(__file__), r"assets\bleeping-demo.mp3"))
        pygame.mixer.music.play(-1)
        pygame.display.flip()
        WIN.blit(BG, (0, 0))
        x = 0
        while True:
            for event in pygame.event.get():

                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
            keys = pygame.key.get_pressed()
            # if keys[pygame.K_RETURN] or keys[pygame.K_SPACE]:
            if keys[pygame.K_RETURN]:
                WIN.blit(BG, (0, 0))
                """for num in range(3, 0, -1):
                    numtext = titlefont.render(str(num), 1, (255, 255, 255))
                    WIN.blit(numtext, (int(WIDTH/2)-10, int(HEIGHT/2)-15))
                    pygame.display.flip()
                    time.sleep(1)
                    WIN.blit(BG, (0, 0))"""
                if nlost:
                    break
                else:
                    main()
            if nlost:
                score_label = main_font.render(
                    f"Press ENTER to start!", 1, (255, 255, 255))
            else:
                score_label = main_font.render(
                    f"You Lost! Your score was {score}.", 1, (255, 255, 255))
                description = main_font.render(
                    "To try agin, press ENTER!", 1, (255, 255, 255))
                WIN.blit(description, (300-x, 400))
            WIN.blit(score_label, (280-x, 200))
            pygame.display.flip()
    loseScreen(True, score=score)
    music = pygame.mixer.music.load(os.path.join(
        os.path.dirname(__file__), r"assets\voxel-revolution.wav"))
    pygame.mixer.music.play(-1)
    bushoot = False
    gonein = True
    while run:
        clock.tick(FPS)
        enemies, lives, score = redraw_window(lives, enemies, score)

        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                bushoot = True

        keys = pygame.key.get_pressed()

        if (keys[pygame.K_a] or keys[pygame.K_LEFT]) and player.x - player_vel > 0:
            player.x -= player_vel

        if (keys[pygame.K_d] or keys[pygame.K_RIGHT]) and player.x + player_vel + player.get_width() < WIDTH:
            player.x += player_vel

        if (keys[pygame.K_w] or keys[pygame.K_UP]) and player.y - player_vel > 0:
            player.y -= player_vel

        if (keys[pygame.K_s] or keys[pygame.K_DOWN]) and player.y + player_vel + player.get_height() < HEIGHT:
            player.y += player_vel

        if keys[pygame.K_SPACE] or bushoot:
            time_deltaB = (datetime.datetime.today() - BCDT)
            tof = player.laserAdd(round(time_deltaB.total_seconds()*1000))
            if tof:
                BCDT = datetime.datetime.today()
                pygame.mixer.Sound.play(shoot1)
            bushoot = False
        time_delta = (datetime.datetime.today() - time1)
        if round(time_delta.total_seconds()) > 15/wave_length:
            thisEnemy = Enemy(random.randrange(
                100, WIDTH - 100), -80, random.choice(["red", "green", "blue"]))
            enemies.append(thisEnemy)
            enemiesDone += 1
            time1 = datetime.datetime.today()

        if enemiesDone == wave_length and enemies_dead >= wave_length:
            enemiesDone = 0
            wave_length += 3
            level += 1

        if lives == 0:
            loseScreen(score=score)

        if player.getHealth() <= 0:
            loseScreen(score=score)

        time_delta = (datetime.datetime.today() - MT)
        if (player.getHealth() <= 15 or lives <= 2) and gonein == True:
            music = pygame.mixer.music.load(os.path.join(
                os.path.dirname(__file__), r"assets\impact-prelude.wav"))
            pygame.mixer.music.play(-1)
            gonein = False


if __name__ == '__main__':
    main()