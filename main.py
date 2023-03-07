import pygame,sys, csv, time, math, random
from Button import *

pygame.init()

window = pygame.display.set_mode((1280, 720))

# zmienne okna gry
WIN_WIDTH = 1280
WIN_HEIGHT = 720

# ustawienia plynnosci gry
fps = 60
clock = pygame.time.Clock()
font = pygame.font.Font(None, 32)
wybor = 0

# ustawienia gry
tile_size = 32
level = 1
ROWS = 51
COLS = 90
if level == 2:
    ROWS = 34
    COLS = 60

tile_types = 35
x_player = 0
y_player = 0
damage = 300
health = 100

potka = 3
potka_x = 1
potka_y = 1
potka_x_prev = potka_x
potka_y_prev = potka_y

current_map = (f'lvl{level}')
portal_rect = (1,1,1,1)
endportal_rect = (1,1,1,1)

# ini zdjec
drzwi_lewo = pygame.image.load('img/mapa_labirynt/24.png').convert_alpha()
drzwi_gora = pygame.image.load('img/mapa_labirynt/30.png').convert_alpha()
drzwi_prawo = pygame.image.load('img/mapa_labirynt/31.png').convert_alpha()
drzwi_dol = pygame.image.load('img/mapa_labirynt/22.png').convert_alpha()
healthbar_img = pygame.image.load('img/Healthbar/healthbar.png').convert_alpha()
heal_card = pygame.image.load('img/potions/heal_card.png').convert_alpha()
speed_card = pygame.image.load('img/potions/speed_card.png').convert_alpha()
damage_card = pygame.image.load('img/potions/damage_card.png').convert_alpha()
speedbar_img = pygame.image.load('img/potions/speed_bar.png').convert_alpha()
damage_bar = pygame.image.load('img/potions/damage_bar.png').convert_alpha()
start_btn_img = pygame.image.load('img/menu/start.png').convert_alpha()
exit_btn_img = pygame.image.load('img/menu/exit.png').convert_alpha()
start_img = pygame.image.load('img/menu/menu.png').convert_alpha()

# inicjalizacja zdj tal
img_list = []
for x in range(tile_types):
    img = pygame.image.load(f'img/mapa_labirynt/{x}.png').convert_alpha()
    img_list.append(img)


# camera move
camera_offset = [0, 0]
# funkcja aktualizująca kamerę
def update_camera(player_pos):
    global camera_offset
    # wyznaczamy pozycję gracza względem środka ekranu
    camera_offset[0] = -player_pos[0] + WIN_WIDTH / 2
    camera_offset[1] = -player_pos[1] + WIN_HEIGHT / 2


class Potions(pygame.sprite.Sprite):
    def __init__(self, x, y, type):
        pygame.sprite.Sprite.__init__(self)
        if type == 1:
            self.image = pygame.image.load('img/potions/health.png').convert_alpha()
        elif type == 2:
            self.image = pygame.image.load('img/potions/speed.png').convert_alpha()
        elif type == 3:
            self.image = pygame.image.load('img/potions/damage.png').convert_alpha()
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.grab = False
        self.type = type

    def custom_update(self):
        if self.grab:
            self.kill()


class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        # Health and player status
        self.health = health
        self.max_health = self.health
        self.alive = True
        self.shoot_cd = 0
        self.heal_potion_amount = 1
        self.speed_potion_amount = 10
        self.damage_potion_amount = 1
        self.runs = False
        self.speed_potion_cd = 0
        self.heal_potion_cd = 0
        self.damage_potion_cd = 0
        self.prev_damage = 10

        # Movement
        self.speed = 1
        self.flip = False
        self.direction = 1

        # player animations
        self.animation_list = []
        self.index = 0
        self.animation_list1 = []
        self.index1 = 0
        self.u_time = pygame.time.get_ticks()
        for i in range(5):
            image = pygame.image.load(f'img/postac/stay_animation/p{i}.png').convert_alpha()
            image = pygame.transform.scale(image, (int(image.get_width()), int(image.get_height())))
            self.animation_list.append(image)
        for i in range(7):
            image1 = pygame.image.load(f'img/postac/animation/p{i}.png').convert_alpha()
            image1 = pygame.transform.scale(image1, (int(image1.get_width()), int(image1.get_height())))
            self.animation_list1.append(image1)
        self.img = self.animation_list[self.index]
        self.img1 = self.animation_list1[self.index1]

        # player hitbox, cordinates and create player rectangle
        self.hitbox = pygame.rect.Rect(x, y, self.img.get_width(), self.img.get_height())
        self.rect = self.img.get_rect()
        self.rect.center = (x, y)
        self.width = self.img.get_width()
        self.height = self.img.get_height()

    def alive_check(self):
        if self.health > self.max_health:
            self.health = self.max_health
        if self.health <= 0:
            self.alive = False
        if self.shoot_cd > 0:
            self.shoot_cd -= 1

            # --- POTIONS ----- #

        if self.speed_potion_cd > 0:
            self.speed_potion_cd -= 1

        if self.speed_potion_cd == 0:
            self.speed = 1

        if self.speed >= 2:
            self.speed = 2

        if self.heal_potion_cd > 0:
            self.heal_potion_cd -= 1

        if self.damage_potion_cd > 0:
            self.damage_potion_cd -= 1

        if self.damage_potion_cd == 1:
            global damage
            damage = damage / 2


    def shoot(self):
            if self.shoot_cd == 0:
                if pygame.mouse.get_pressed()[0]:
                    bullet_direction = pygame.math.Vector2(pygame.mouse.get_pos()) - player.rect.center
                    bullet_direction = bullet_direction.normalize()
                    bullet = Bullet(player.rect.centerx, player.rect.centery, bullet_direction.x, bullet_direction.y,
                                    'bullet')
                    bullet_group.add(bullet)
                    self.shoot_cd = 40

    def move(self):
        # player velocity
        dx = 0
        dy = 0
        keys = pygame.key.get_pressed()

        if keys[pygame.K_d]:
            dx += self.speed
            self.runs = True
            self.direction = 1
        if keys[pygame.K_a]:
            dx -= self.speed
            self.runs = True
            self.direction = -1
        if keys[pygame.K_w]:
            self.runs = True
            dy -= self.speed
        if keys[pygame.K_s]:
            self.runs = True
            dy += self.speed
        if keys[pygame.K_a] or keys[pygame.K_d] or keys[pygame.K_w] or keys[pygame.K_s]:
            self.runs = True
        else:
            self.runs = False

        # drink potions
        if self.heal_potion_amount > 0:
            if self.heal_potion_cd == 0:
                if keys[pygame.K_q]:
                    self.health += self.max_health / 2
                    self.heal_potion_amount -= 1
                    self.heal_potion_cd = 10
        if self.speed_potion_amount > 0:
            if self.speed_potion_cd == 0:
                if keys[pygame.K_e]:
                    self.speed += 1
                    self.speed_potion_amount -= 1
                    self.speed_potion_cd = 400
        if self.damage_potion_amount > 0:
            if self.damage_potion_cd == 0:
                if keys[pygame.K_r]:
                    global damage
                    self.prev_damage = damage
                    damage = damage * 2
                    self.damage_potion_cd = 400

        # collisions
        for tile in world.obstacle_list:
            if tile[1].colliderect(self.rect.x + dx, self.rect.y, self.width, self.height):
                dx = 0
            if tile[1].colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
                if dy < 0:
                    dy = tile[1].bottom - self.rect.top
                elif dy >= 0:
                    dy = tile[1].top - self.rect.bottom

        level_complete = False
        if self.rect.colliderect(portal_rect):
            level_complete = True

        for bosses in boss_group:
            if bosses.health <= 0:
                if self.rect.colliderect(endportal_rect):
                    global health
                    health += 100
                    self.max_health = health
                    damage += 20
                    level_complete = True

        for potion in potions_group:
            if self.rect.colliderect(potion.rect):
                potion.grab = True
                if potion.type == 2:
                    self.speed_potion_amount += 1
                if potion.type == 1:
                    self.heal_potion_amount += 1
                if potion.type == 3:
                    self.damage_potion_amount += 1

        self.rect.x += dx
        self.rect.y += dy

        return level_complete

    def update_animation(self):
        cd = 200
        self.img = self.animation_list[self.index]
        self.img1 = self.animation_list1[self.index1]
        if self.runs:
            if pygame.time.get_ticks() - self.u_time > cd:
                self.index1 += 1
                if self.index1 == 5:
                    self.index1 = 1
        if pygame.time.get_ticks() - self.u_time > cd:
            self.index += 1
            if self.index == 5:
                self.index = 1
            self.u_time = pygame.time.get_ticks()

    def draw(self):
        if self.runs:
            window.blit(pygame.transform.flip(self.img1, self.flip, False), self.rect)
        else:
            window.blit(pygame.transform.flip(self.img, self.flip, False), self.rect)


class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, directionx, directiony, file):
        pygame.sprite.Sprite.__init__(self)
        # move
        self.speed = 3
        self.directionx = directionx
        self.directiony = directiony

        # images and create rectangle of bullet
        self.image = pygame.image.load(f'img/postac/{file}.png').convert_alpha()
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)

    def update(self):
        # bullet direction flight
        self.rect.x += (self.directionx * self.speed)
        self.rect.y += (self.directiony * self.speed)

        # collison for bullet
        if self.rect.right < 0 or self.rect.left > 1920:
            self.kill()
        for tile in world.obstacle_list:
            if tile[1].colliderect(self.rect):
                self.kill()
        # if pygame.sprite.spritecollide(p, bullet_group, False):
        #     if p.alive:
        #         p.health -= 5
        #         self.kill()

        # deal damage
        for enemy in enemies_group:
            if pygame.sprite.spritecollide(enemy, bullet_group, False):
                if enemy.alive:
                    enemy.health -= damage
                    self.kill()
        for bosses in boss_group:
            if pygame.sprite.spritecollide(bosses, bullet_group, False):
                if bosses.alive:
                    bosses.health -= damage
                    self.kill()


class World():
    def __init__(self):
        self.world_list = []
        self.decoration_list = []
        self.obstacle_list = []
        self.enemies_group = pygame.sprite.Group()
    def process_data(self, data):
        for y, row in enumerate(data):
            for x, tile in enumerate(row):
                if tile >= -1:
                    img = img_list[tile]
                    img_rect = img.get_rect()
                    img_rect.x = x * tile_size
                    img_rect.y = y * tile_size
                    tile_data = (img, img_rect)
                    if tile == 34:
                        global endportal_rect
                        endportal_rect = (img_rect)
                    if tile == 23:
                        global portal_rect
                        portal_rect = (img_rect)
                    if tile == 32:
                        if level == 2:
                            bosses = Boss(x * tile_size, y * tile_size, 'b', 5, 600)
                            boss_group.add(bosses)
                    if tile == 14:
                        if level == 1 or level == 2:
                            enemy = Enemy(x * tile_size, y * tile_size, 1, 100, 'z')
                            enemies_group.add(enemy)
                        if level == 3:
                            enemy = Enemy(x * tile_size, y * tile_size, 5, 450, 'g')
                            enemies_group.add(enemy)
                    if tile != -1 and tile != 14 and tile != 32:
                        self.world_list.append(tile_data)
                    if tile == 6 and tile != 23 and tile != 34 and tile == 24 and tile == 31 and tile == 22 and tile == 30 and tile == 4 and tile == 5 and tile == 12 and tile == 13 and tile == 20 and tile == 21 and tile == 25 and tile == 26 and tile == 27:
                        self.decoration_list.append(tile_data)
                    if tile != -1 and tile != 23 and tile != 34 and tile != 6 and tile != 24 and tile != 31 and tile != 22 and tile != 30 and tile != 4 and tile != 5 and tile != 12 and tile != 13 and tile != 20 and tile != 21 and tile != 25 and tile != 26 and tile != 27 and tile != 14 and tile != 32:
                        self.obstacle_list.append(tile_data)
                    if tile == 6:
                        global x_player
                        global y_player
                        x_player = x * tile_size
                        y_player = y * tile_size

    def draw(self):
        for tile in self.world_list:
            window.blit(tile[0], tile[1])


class Enemy(pygame.sprite.Sprite):
    def __init__(self, x ,y, damage, health,file):
        pygame.sprite.Sprite.__init__(self)

        # Health and enemy status
        self.health = health
        self.alive = True
        self.last_shot_time = 0
        self.attack = False
        self.flip = True
        self.right_attack = None
        self.left_attack = None
        self.speed = 2
        self.distance_for_move = 150
        self.dx = 0
        self.dy = 0
        self.damage = damage

        # enemy animation
        self.animation_list = []
        self.index = 0

        self.animation_list1 = []
        self.index1 = 0

        self.u_time = pygame.time.get_ticks()
        for i in range(5):
            image = pygame.image.load(f'img/enemies/enemystay/{file}{i}.png').convert_alpha()
            image = pygame.transform.scale(image, (int(image.get_width()), int(image.get_height())))
            self.animation_list.append(image)

        for i in range(7):
            image1 = pygame.image.load(f'img/enemies/attack_animation_enemy/{file}{i}.png').convert_alpha()
            image1 = pygame.transform.scale(image1, (int(image1.get_width()), int(image1.get_height())))
            self.animation_list1.append(image1)

        self.img1 = self.animation_list1[self.index1]
        self.img = self.animation_list[self.index]

        # enmemy cordinates and create rectangle
        self.hitbox = pygame.rect.Rect(x, y, self.img.get_width(), self.img.get_height())
        self.rect = self.img.get_rect()
        self.rect.center = (x, y)
        self.width = self.img.get_width()
        self.height = self.img.get_height()

    def alive_check(self):
        if self.health <= 0:
            self.alive = False

    def draw(self):

        if player.rect.colliderect(self.rect.x + 32, self.rect.y, self.rect.width, self.rect.height):
            self.right_attack = True
            self.left_attack = False
            if self.attack:
                window.blit(self.img1, self.rect)
            else:
                window.blit(self.img, self.rect)

        elif player.rect.colliderect(self.rect.x - 32, self.rect.y, self.rect.width, self.rect.height):
            self.left_attack = True
            self.right_attack = False
            if self.attack:
                window.blit(pygame.transform.flip(self.img1, self.flip, False), self.rect)
            else:
                window.blit(pygame.transform.flip(self.img, self.flip, False), self.rect)

        else:
            self.right_attack = False
            self.left_attack = False
            if self.attack:
                window.blit(self.img1, self.rect)
            else:
                window.blit(self.img, self.rect)

    def custom_update(self):
        self.dx = 0
        self.dy = 0

        player_right = False
        player_left = False
        player_up = False
        player_down = False

        # calculate distance to player
        distance_to_player = math.sqrt((player.rect.x - self.rect.x) ** 2 + (player.rect.y - self.rect.y) ** 2)

        if distance_to_player < self.distance_for_move:

            # Checking if the player is on the right side, if so, the enemy moves towards the player
            if player.rect.x > self.rect.x :
                player_right = True
            # Checking if the player is on the left side, if so, the enemy moves towards the player
            if player.rect.x < self.rect.x:
                player_left = True
            # Checking if the player is at the bottom, if so, the enemy moves towards the player
            if player.rect.y > self.rect.y:
                player_down = True
            # Checking if the player is at the top, if so, the enemy moves towards the player
            if player.rect.y < self.rect.y:
                player_up = True

        if player_right:
            self.dx += self.speed
        if player_left:
            self.dx -= self.speed
        if player_down:
            self.dy += self.speed
        if player_up:
            self.dy -= self.speed

        if self.dx > 1:
            self.dx = 1
        if self.dy > 1:
            self.dy = 1

        # collisions
        if self.dx > 0 or self.dy > 0 or self.dy < 0 or self.dx < 0:
            for tile in world.obstacle_list:
                if tile[1].colliderect(self.rect.x + self.dx, self.rect.y, self.width, self.height):
                    self.dx = 0
                if tile[1].colliderect(self.rect.x, self.rect.y + self.dy, self.width, self.height):
                    if self.dy < 0:
                        self.dy = tile[1].bottom - self.rect.top
                    elif self.dy >= 0:
                        self.dy = tile[1].top - self.rect.bottom

        self.rect.x += self.dx
        self.rect.y += self.dy

    def update_animation(self):
        cd = 20
        self.img = self.animation_list[self.index]
        self.img1 = self.animation_list1[self.index1]
        if self.attack:
            if pygame.time.get_ticks() - self.u_time > cd:
                self.index1 += 1
                if self.index1 == 7:
                    self.index1 = 1
        if pygame.time.get_ticks() - self.u_time > cd:
            self.index += 1
            if self.index == 5:
                self.index = 0
            self.u_time = pygame.time.get_ticks()

    def atack(self):
        distance_to_player = math.sqrt((player.rect.x - self.rect.x) ** 2 + (player.rect.y - self.rect.y) ** 2)
        if distance_to_player <= 32 and self.alive == True  and time.time() - self.last_shot_time > 1:
            self.attack = True
            player.health -= self.damage
            self.last_shot_time = time.time()
        elif distance_to_player > 32 :
            self.attack = False


class Boss(pygame.sprite.Sprite):
    def __init__(self, x, y, file, damage, health):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load(f'img/enemies/{file}0.png')
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.damage = damage
        self.attack = False
        self.health = health
        self.max_health = self.health
        self.alive = True
        self.dx = 0
        self.dy = 0
        self.speed = 1
        self.distance_for_move = 256

        self.last_shot_time = 0
        self.animation_list = []
        self.index = 0
        self.u_time = pygame.time.get_ticks()
        for i in range(5):
            image = pygame.image.load(f'img/enemies/boss_attack/{file}{i}.png').convert_alpha()
            image = pygame.transform.scale(image, (int(image.get_width()), int(image.get_height())))
            self.animation_list.append(image)
        self.img = self.animation_list[self.index]
        self.width = self.img.get_width()
        self.height = self.img.get_height()

    def update_animation(self):
        cd = 20
        self.img = self.animation_list[self.index]
        if pygame.time.get_ticks() - self.u_time > cd:
            self.index += 1
            if self.index == 5:
                self.index = 0
            self.u_time = pygame.time.get_ticks()

    def attack_(self):
        distance_to_player = math.sqrt((player.rect.x - self.rect.x) ** 2 + (player.rect.y - self.rect.y) ** 2)
        if distance_to_player < 50 and time.time() - self.last_shot_time > 1:
            self.attack = True
            player.health -= self.damage
            self.last_shot_time = time.time()
        if distance_to_player > 50:
            self.attack = False

    def ai(self):
        player_right = False
        player_left = False
        player_up = False
        player_down = False

        if not self.attack:
            # calculate distance to player
            distance_to_player = math.sqrt((player.rect.x - self.rect.x) ** 2 + (player.rect.y - self.rect.y) ** 2)

            if distance_to_player < self.distance_for_move:

                # Checking if the player is on the right side, if so, the enemy moves towards the player
                if player.rect.x > self.rect.x:
                    player_right = True
                # Checking if the player is on the left side, if so, the enemy moves towards the player
                if player.rect.x < self.rect.x:
                    player_left = True
                # Checking if the player is at the bottom, if so, the enemy moves towards the player
                if player.rect.y > self.rect.y:
                    player_down = True
                # Checking if the player is at the top, if so, the enemy moves towards the player
                if player.rect.y < self.rect.y:
                    player_up = True

            if player_right:
                self.dx += self.speed
            if player_left:
                self.dx -= self.speed
            if player_down:
                self.dy += self.speed
            if player_up:
                self.dy -= self.speed

            if self.dx > 1:
                self.dx = 1
            if self.dy > 1:
                self.dy = 1

        self.rect.x += self.dx
        self.rect.y += self.dy

    def draw(self):
        if self.attack:
            window.blit(self.img, (self.rect))
        else:
            window.blit(self.image, self.rect)
    def custom_update(self):
        if self.health <= 0:
            self.alive = False


class Attack(pygame.sprite.Sprite):
    def __init__(self):
        # direction of player for draw
        self.flip = True
        # animation
        self.animation_list = []
        self.index = 0
        self.u_time = pygame.time.get_ticks()
        for i in range(7):
            image = pygame.image.load(f'img/enemies/attack_animation/{i}.png').convert_alpha()
            image = pygame.transform.scale(image, (int(image.get_width()), int(image.get_height())))
            self.animation_list.append(image)
        self.img = self.animation_list[self.index]

    def update_animation(self):
        cd = 20
        self.img = self.animation_list[self.index]
        if pygame.time.get_ticks() - self.u_time > cd:
            self.index += 1
            if self.index == 7:
                self.index = 0
            self.u_time = pygame.time.get_ticks()

    def draw(self, rect, right, left):
        if right:
            window.blit(self.img, (rect.x + 15, rect.y , rect.width, rect.height))
        elif left:
            window.blit(pygame.transform.flip(self.img,self.flip, False), (rect.x - 15, rect.y, rect.width, rect.height))
        else:
            window.blit(self.img, (rect.x + 15, rect.y , rect.width, rect.height))

class HealthBar():
    def __init__(self, x, y, health, max_health):
        self.x = x
        self.y = y
        self.health = health
        self.max_health = max_health

    def draw(self, health, max_health):
        #update with new health
        self.health = health
        #calculate health ratio
        ratio = self.health / max_health
        pygame.draw.rect(window, (210, 199, 220), (self.x, self.y, 100 * ratio, 30))


def vignette(x, y):
    image = pygame.image.load('img/winieta.png').convert_alpha()
    window.blit(image, (x, y))

def reset():
    bullet_group.empty()
    enemies_group.empty()
    boss_group.empty()

    data = []
    for row in range(ROWS):
        r = [-1] * COLS
        data.append(r)

    return data

world_data = []
for row in range(ROWS):
    r = [-1] * COLS
    world_data.append(r)

with open(f'img/map/{current_map}.csv', newline='') as csvfile:
    reader = csv.reader(csvfile, delimiter=',')
    for x, row in enumerate(reader):
        for y, tile in enumerate(row):
            world_data[x][y] = int(tile)

# initialization groups
enemies_group = pygame.sprite.Group()
bullet_group = pygame.sprite.Group()
boss_group = pygame.sprite.Group()
potions_group = pygame.sprite.Group()


# initialization other units
world = World()
world.process_data(world_data)
player = Player(x_player, y_player)
attack = Attack()
healthbar = HealthBar(45, 10, player.health, player.max_health)
speed_potion_duration = HealthBar(45, 50, player.speed_potion_cd, 400)
damage_potion_duration = HealthBar(45,100, player.damage_potion_cd, 400)
start_btn = Button(550,450 , start_btn_img, 0.5)
exit_btn = Button(550, 530, exit_btn_img, 0.5)


# initialization variables
m_up = False
m_down = False
m_left = False
m_right = False
runs = False
start = False
run = True
while run:
    if start == False:
        window.blit(start_img, (0, 0))
        if start_btn.draw(window):
            start = True
        if exit_btn.draw(window):
            run = False
    else:
        heal_potion_text = font.render(str(player.heal_potion_amount), True, (210, 199, 220))
        speed_potion_text = font.render(str(player.speed_potion_amount), True, (210, 199, 220))
        damage_potion_text = font.render(str(player.damage_potion_amount), True, (210, 199, 220))
        clock.tick(fps)
        window.fill((255,255,255))
        world.draw()

        # update position camera
        update_camera(player.rect.center)

        # przesuwamy obiekty gry o przesunięcie kamery // move objects
        for tile in world.world_list:
            tile[1].x += camera_offset[0]
            tile[1].y += camera_offset[1]

        for enemy in enemies_group:
            enemy.rect.x += camera_offset[0]
            enemy.rect.y += camera_offset[1]

        for bosses in boss_group:
            bosses.rect.x += camera_offset[0]
            bosses.rect.y += camera_offset[1]

        for potion in potions_group:
            potion.rect.x += camera_offset[0]
            potion.rect.y += camera_offset[1]

        for enemy in enemies_group:
            if enemy.health <= 0:
                damage += 1
                potka = random.randint(1,9)
                potka_x = enemy.rect.x
                potka_y = enemy.rect.y
                if potka >= 4 or potka <= 9:
                    pass
                if potka == 2:
                    potion = Potions(potka_x, potka_y, potka)
                    potions_group.add(potion)
                if potka == 1:
                    potion = Potions(potka_x, potka_y, potka)
                    potions_group.add(potion)
                if potka == 3:
                    potion = Potions(potka_x, potka_y, potka)
                    potions_group.add(potion)

                enemy.kill()

            if enemy.alive:
                enemy.draw()
                enemy.update_animation()
                enemy.alive_check()
                enemy.atack()
                enemy.custom_update()
                if enemy.attack:
                    attack.update_animation()
                    attack.draw(enemy.rect, enemy.right_attack, enemy.left_attack)

        for bosses in boss_group:
            if bosses.alive:
                bosses.draw()
                bosses.update_animation()
                bosses.attack_()
                bosses.custom_update()
                bosses.ai()

        player.rect.x += camera_offset[0]
        player.rect.y += camera_offset[1]

        # player calls
        if player.alive:
            player.update_animation()
            player.draw()
            player.alive_check()
            player.move()
            player.shoot()
            level_complete = player.move()
            if level_complete:
                portal_rect = (0, 0, 0, 0)
                level += 1
                world_data = reset()
                with open(f'img/map/lvl{level}.csv', newline='') as csvfile:
                    reader = csv.reader(csvfile, delimiter=',')
                    for x, row in enumerate(reader):
                        for y, tile in enumerate(row):
                            world_data[x][y] = int(tile)
                world = World()
                world.process_data(world_data)
                player = Player(x_player, y_player)
                # update position camera
                update_camera(player.rect.center)

        # bullet calls
        bullet_group.update()
        bullet_group.draw(window)

        potions_group.draw(window)
        for potion in potions_group:
            potion.custom_update()

        vignette(0, 0)
        healthbar.draw(player.health, player.max_health)

        if player.speed_potion_cd > 0:
            speed_potion_duration.draw(player.speed_potion_cd, 400)
            window.blit(speedbar_img, (0, 40))
        if player.damage_potion_cd > 0:
            damage_potion_duration.draw(player.damage_potion_cd, 400)
            window.blit(damage_bar, (0, 90))
        window.blit(healthbar_img, (0, 0))
        window.blit(heal_card, (110, 600))
        window.blit(speed_card, (10, 600))
        window.blit(heal_potion_text, (110, 580))
        window.blit(speed_potion_text, (10, 580))
        window.blit(damage_card, (210, 600))
        window.blit(damage_potion_text, (210, 580))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit(0)
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            run = False
    print(damage, player.health)
    pygame.display.update()