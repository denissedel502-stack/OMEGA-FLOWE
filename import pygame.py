import pygame
import random
import sys
import math

pygame.init()

WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("OMEGA FLOWEY")

clock = pygame.time.Clock()

# Battle box
box = pygame.Rect(200, 200, 400, 300)

# Player
player_size = 16
player = pygame.Rect(box.centerx, box.centery, player_size, player_size)
speed = 3
max_hp = 20
hp = max_hp

# Attack containers
bullets = []
lasers = []
circle_attacks = []

# Timers
spawn_timer = 0
laser_timer = 0

# Phase
phase = 1
soul_help = False

font = pygame.font.SysFont("arial", 28)

# ----- FUNCTIONS -----

def spawn_bullet():
    side = random.choice(["top","bottom","left","right"])
    if side == "top":
        x = random.randint(box.left, box.right)
        y = box.top
        dx, dy = random.uniform(-2,2), 3
    elif side == "bottom":
        x = random.randint(box.left, box.right)
        y = box.bottom
        dx, dy = random.uniform(-2,2), -3
    elif side == "left":
        x = box.left
        y = random.randint(box.top, box.bottom)
        dx, dy = 3, random.uniform(-2,2)
    else:
        x = box.right
        y = random.randint(box.top, box.bottom)
        dx, dy = -3, random.uniform(-2,2)

    color = (255,255,255)
    if phase == 2:
        color = (255,255,255)

    bullets.append([x,y,dx,dy,color])

def spawn_laser():
    x = random.randint(box.left, box.right - 20)
    lasers.append({"rect": pygame.Rect(x, box.top, 20, box.height),
                   "timer": 60})  # Laser stays 1 second

def spawn_circle_attack():
    for angle in range(0, 360, 15):
        rad = math.radians(angle)
        dx = 4 * math.cos(rad)
        dy = 4 * math.sin(rad)
        bullets.append([box.centerx, box.centery, dx, dy, (255,0,255)])

# ----- GAME LOOP -----
running = True
while running:
    clock.tick(60)
    screen.fill((0,0,0))

    # TV-style glitch background
    for i in range(20):
        pygame.draw.line(screen,
                         (random.randint(0,50),0,0),
                         (0, random.randint(0,HEIGHT)),
                         (WIDTH, random.randint(0,HEIGHT)))

    # Draw battle box
    pygame.draw.rect(screen, (255,255,255), box, 3)

    # Events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Player movement
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]: player.x -= speed
    if keys[pygame.K_RIGHT]: player.x += speed
    if keys[pygame.K_UP]: player.y -= speed
    if keys[pygame.K_DOWN]: player.y += speed
    player.clamp_ip(box)

    # Phase logic
    spawn_timer += 1
    spawn_speed = 20
    if phase == 2:
        spawn_speed = 8

    if spawn_timer > spawn_speed:
        spawn_bullet()
        # Circle attack chance in phase 2
        if phase == 2 and random.randint(1,200) == 1:
            spawn_circle_attack()
        spawn_timer = 0

    # Laser timer
    laser_timer += 1
    if phase == 2 and laser_timer > 120:
        spawn_laser()
        laser_timer = 0

    # Activate phase 2 if HP low
    if hp <= max_hp/2 and not soul_help:
        soul_help = True
        phase = 2

    # Update bullets
    for bullet in bullets[:]:
        bullet[0] += bullet[2]
        bullet[1] += bullet[3]

        pygame.draw.circle(screen, bullet[4], (int(bullet[0]), int(bullet[1])), 6)

        if player.collidepoint(bullet[0], bullet[1]):
            if not soul_help:
                hp -= 1
            bullets.remove(bullet)
            continue

        if not box.collidepoint(bullet[0], bullet[1]):
            bullets.remove(bullet)

    # Update lasers
    for laser in lasers[:]:
        pygame.draw.rect(screen, (0,255,0), laser["rect"])
        if player.colliderect(laser["rect"]):
            hp -= 0.3
        laser["timer"] -= 1
        if laser["timer"] <= 0:
            lasers.remove(laser)

    # Draw player heart
    pygame.draw.circle(screen, (255,0,0), player.center, 8)

    # Soul help mode
    if soul_help:
        heal_text = font.render("SOULS ARE HELPING YOU!", True, (0,255,255))
        screen.blit(heal_text, (WIDTH//2 - 170, 100))
        hp = min(max_hp, hp + 0.05)
        if hp == max_hp:
            soul_help = False

    # UNDERTALE STYLE HP BAR
    bar_width = 150
    bar_height = 15
    bar_x = 300
    bar_y = 550
    hp_ratio = hp / max_hp
    current_width = bar_width * hp_ratio

    pygame.draw.rect(screen, (0,0,0), (bar_x, bar_y, bar_width, bar_height))  # background
    pygame.draw.rect(screen, (255,255,0), (bar_x, bar_y, current_width, bar_height))  # HP
    pygame.draw.rect(screen, (255,255,255), (bar_x, bar_y, bar_width, bar_height), 3)  # frame

    # Game Over
    if hp <= 0:
        over = font.render("FLOWEY LAUGHS...", True, (255,0,0))
        screen.blit(over, (WIDTH//2 - 150, HEIGHT//2))
        pygame.display.flip()
        pygame.time.delay(3000)
        running = False

    pygame.display.flip()

pygame.quit()
sys.exit()