# OMEGA FLOWEY V3
import pygame
import random
import sys
import math

pygame.init()

WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("OMEGA FLOWEY V3")

clock = pygame.time.Clock()

box = pygame.Rect(200, 200, 400, 300)

player = pygame.Rect(box.centerx, box.centery, 16, 16)

speed = 3

max_hp = 30
hp = max_hp

bullets = []
lasers = []
bombs = []
vines = []

spawn_timer = 0
laser_timer = 0
bomb_timer = 0
vine_timer = 0

phase = 1
soul_help = False
shake = 0

font = pygame.font.SysFont("arial", 28)

messages = ["DIE", "HAHAHA", "SAVE ME?", "NO ESCAPE", "YOU IDIOT"]


# ---------- SPAWN ----------

def spawn_bullet():

    side = random.choice(["top","bottom","left","right"])

    if side == "top":
        x = random.randint(box.left, box.right)
        y = box.top
        dx,dy = random.uniform(-2,2),3

    elif side == "bottom":
        x = random.randint(box.left, box.right)
        y = box.bottom
        dx,dy = random.uniform(-2,2),-3

    elif side == "left":
        x = box.left
        y = random.randint(box.top, box.bottom)
        dx,dy = 3,random.uniform(-2,2)

    else:
        x = box.right
        y = random.randint(box.top, box.bottom)
        dx,dy = -3,random.uniform(-2,2)

    bullets.append([x,y,dx,dy,(255,255,255)])


def spawn_circle():

    for a in range(0,360,15):

        r = math.radians(a)

        dx = math.cos(r)*4
        dy = math.sin(r)*4

        bullets.append([box.centerx,box.centery,dx,dy,(255,0,255)])


def spawn_spiral():

    t = pygame.time.get_ticks()/100

    for i in range(12):

        ang = t+i

        dx = math.cos(ang)*3
        dy = math.sin(ang)*3

        bullets.append([box.centerx,box.centery,dx,dy,(0,255,255)])


def spawn_laser():

    x = random.randint(box.left, box.right-20)

    lasers.append({
        "rect":pygame.Rect(x,box.top,20,box.height),
        "timer":60
    })


def spawn_bomb():

    x = random.randint(box.left, box.right)
    y = random.randint(box.top, box.bottom)

    bombs.append([x,y,60])


def spawn_vine():

    x = random.randint(box.left, box.right)

    vines.append({
        "rect":pygame.Rect(x,box.top,10,box.height),
        "timer":80
    })


# ---------- LOOP ----------

running = True

while running:

    clock.tick(60)

    offset_x = random.randint(-shake, shake)
    offset_y = random.randint(-shake, shake)

    screen.fill((0,0,0))

    # glitch bg
    for i in range(20):

        pygame.draw.line(
            screen,
            (random.randint(0,70),0,0),
            (0, random.randint(0,HEIGHT)),
            (WIDTH, random.randint(0,HEIGHT))
        )

    pygame.draw.rect(screen,(255,255,255),box,3)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running=False

    # MOVE
    keys = pygame.key.get_pressed()

    dx=0
    dy=0

    if keys[pygame.K_LEFT]: dx-=speed
    if keys[pygame.K_RIGHT]: dx+=speed
    if keys[pygame.K_UP]: dy-=speed
    if keys[pygame.K_DOWN]: dy+=speed

    player.x+=dx
    player.y+=dy

    player.clamp_ip(box)

    # PHASES

    if hp < max_hp*0.7:
        phase=2

    if hp < max_hp*0.4:
        phase=3

    if hp < max_hp*0.2:
        phase=4

    spawn_timer+=1
    laser_timer+=1
    bomb_timer+=1
    vine_timer+=1

    speed_spawn=20

    if phase==2: speed_spawn=12
    if phase==3: speed_spawn=7
    if phase==4: speed_spawn=4

    if spawn_timer>speed_spawn:

        spawn_bullet()

        if phase>=2 and random.randint(1,3)==1:
            spawn_circle()

        if phase>=3 and random.randint(1,2)==1:
            spawn_spiral()

        spawn_timer=0

    if phase>=2 and laser_timer>120:
        spawn_laser()
        laser_timer=0

    if phase>=3 and bomb_timer>100:
        spawn_bomb()
        bomb_timer=0

    if phase>=4 and vine_timer>90:
        spawn_vine()
        vine_timer=0

    # BULLETS

    for b in bullets[:]:

        b[0]+=b[2]
        b[1]+=b[3]

        pygame.draw.circle(screen,b[4],(int(b[0]),int(b[1])),6)

        if player.collidepoint(b[0],b[1]):

            if not soul_help:
                hp-=1
                shake=8

            bullets.remove(b)

        elif not box.collidepoint(b[0],b[1]):
            bullets.remove(b)

    # LASERS

    for l in lasers[:]:

        pygame.draw.rect(screen,(0,255,0),l["rect"])

        if player.colliderect(l["rect"]):
            hp-=0.3
            shake=5

        l["timer"]-=1

        if l["timer"]<=0:
            lasers.remove(l)

    # BOMBS

    for b in bombs[:]:

        pygame.draw.circle(screen,(255,100,0),(b[0],b[1]),10)

        b[2]-=1

        if b[2]<=0:

            spawn_circle()
            bombs.remove(b)

    # VINES

    for v in vines[:]:

        pygame.draw.rect(screen,(0,200,0),v["rect"])

        if player.colliderect(v["rect"]):
            hp-=0.5

        v["timer"]-=1

        if v["timer"]<=0:
            vines.remove(v)

    # PLAYER

    pygame.draw.circle(screen,(255,0,0),player.center,8)

    # SOUL HELP

    if hp<max_hp/2 and not soul_help:
        soul_help=True

    if soul_help:

        t=font.render("SOULS HELP",True,(0,255,255))
        screen.blit(t,(300,100))

        hp=min(max_hp,hp+0.05)

        if hp>=max_hp:
            soul_help=False

    # FLOWEY TEXT

    if phase>=2 and random.randint(1,60)==1:

        m=random.choice(messages)

        t=font.render(m,True,(255,0,0))
        screen.blit(t,(350,150))

    # HP BAR

    ratio=hp/max_hp

    pygame.draw.rect(screen,(0,0,0),(300,550,150,15))
    pygame.draw.rect(screen,(255,255,0),(300,550,150*ratio,15))
    pygame.draw.rect(screen,(255,255,255),(300,550,150,15),3)

    # GAME OVER

    if hp<=0:

        t=font.render("FLOWEY LAUGHS",True,(255,0,0))
        screen.blit(t,(300,300))

        pygame.display.flip()
        pygame.time.delay(3000)

        running=False

    if shake>0:
        shake-=1

    pygame.display.flip()

pygame.quit()
sys.exit()