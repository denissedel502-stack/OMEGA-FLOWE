import pygame
import random
import sys
import math

pygame.init()

WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("OMEGA FLOWEY")

clock = pygame.time.Clock()

# ---------- IMAGES ----------

flowey_img = pygame.image.load("flowey.png").convert_alpha()
flowey_img = pygame.transform.scale(flowey_img, (400, 200))

heart_img = pygame.image.load("heart.png").convert()
heart_img.set_colorkey((0,0,0))
heart_img = pygame.transform.scale(heart_img, (90,80))

# ---------- FLOWEY ANIM ----------

flowey_x = 200
flowey_y = 0
flowey_time = 0

# ---------- BOX ----------

box = pygame.Rect(200, 200, 400, 300)
player = pygame.Rect(box.centerx, box.centery, 16, 16)

speed = 3

max_hp = 30
hp = max_hp

flowey_hp = 200

bullets = []
rain_bullets = []
circle_bullets = []
wall_bullets = []

spawn_timer = 0

phase = 1

soul_help = False
used_souls = False

fight_mode = False
attack_cooldown = 0

font = pygame.font.SysFont("arial", 28)

messages = ["DIE","HAHAHA","NO ESCAPE"]
flowey_text = ""
text_timer = 0

# ---------- ATTACKS ----------

def spawn_bullet():

    side = random.choice(["top","bottom","left","right"])

    if side == "top":
        x=random.randint(box.left,box.right)
        y=box.top
        dx,dy=random.uniform(-2,2),3

    elif side=="bottom":
        x=random.randint(box.left,box.right)
        y=box.bottom
        dx,dy=random.uniform(-2,2),-3

    elif side=="left":
        x=box.left
        y=random.randint(box.top,box.bottom)
        dx,dy=3,random.uniform(-2,2)

    else:
        x=box.right
        y=random.randint(box.top,box.bottom)
        dx,dy=-3,random.uniform(-2,2)

    bullets.append([x,y,dx,dy])


def spawn_rain():

    for i in range(6):

        x=random.randint(box.left,box.right)
        y=box.top

        dx=random.uniform(-1,1)
        dy=random.uniform(4,6)

        rain_bullets.append([x,y,dx,dy])


def spawn_circle():

    cx=box.centerx
    cy=box.centery

    for a in range(0,360,20):

        rad=math.radians(a)

        dx=math.cos(rad)*4
        dy=math.sin(rad)*4

        circle_bullets.append([cx,cy,dx,dy])


def spawn_wall():

    y=random.randint(box.top,box.bottom)

    for i in range(10):

        x=box.left

        dx=4
        dy=random.uniform(-1,1)

        wall_bullets.append([x,y,dx,dy])


# ---------- LOOP ----------

running=True

while running:

    clock.tick(60)

    if attack_cooldown>0:
        attack_cooldown-=1

    if text_timer>0:
        text_timer-=1

    # FLOWEY MOVE

    flowey_time+=1
    flowey_y=5*math.sin(flowey_time*0.05)
    flowey_x=200+random.randint(-1,1)

    screen.fill((0,0,0))

    screen.blit(flowey_img,(flowey_x,flowey_y))

    pygame.draw.rect(screen,(255,255,255),box,3)

    # EVENTS

    for event in pygame.event.get():

        if event.type==pygame.QUIT:
            running=False

        if event.type==pygame.KEYDOWN:

            if fight_mode and event.key==pygame.K_SPACE:

                if attack_cooldown<=0:
                    flowey_hp-=10
                    attack_cooldown=20

    # MOVE

    keys=pygame.key.get_pressed()

    dx=0
    dy=0

    if keys[pygame.K_LEFT]: dx-=speed
    if keys[pygame.K_RIGHT]: dx+=speed
    if keys[pygame.K_UP]: dy-=speed
    if keys[pygame.K_DOWN]: dy+=speed

    player.x+=dx
    player.y+=dy

    player.clamp_ip(box)

    # ---------- PHASE ----------

    if hp<max_hp*0.5 and phase==1:
        phase=2
        fight_mode=True
        spawn_timer=0

    spawn_timer+=1

    if phase==1:
        speed_spawn=20
    else:
        speed_spawn=8

    if spawn_timer>=speed_spawn:

        spawn_bullet()

        if phase==2:

            r=random.randint(1,4)

            if r==1:
                spawn_rain()

            elif r==2:
                spawn_circle()

            elif r==3:
                spawn_wall()

            else:
                spawn_bullet()

        spawn_timer=0

    # ---------- BULLETS ----------

    for b in bullets[:]:

        b[0]+=b[2]
        b[1]+=b[3]

        pygame.draw.circle(screen,(255,255,255),(int(b[0]),int(b[1])),6)

        if player.collidepoint(b[0],b[1]):

            if not soul_help:
                hp-=1

            bullets.remove(b)

        elif not box.collidepoint(b[0],b[1]):
            bullets.remove(b)

    for b in rain_bullets[:]:

        b[0]+=b[2]
        b[1]+=b[3]

        pygame.draw.circle(screen,(0,255,255),(int(b[0]),int(b[1])),6)

        if player.collidepoint(b[0],b[1]):
            hp-=1
            rain_bullets.remove(b)

        elif not box.collidepoint(b[0],b[1]):
            rain_bullets.remove(b)

    for b in circle_bullets[:]:

        b[0]+=b[2]
        b[1]+=b[3]

        pygame.draw.circle(screen,(255,0,255),(int(b[0]),int(b[1])),6)

        if player.collidepoint(b[0],b[1]):
            hp-=1
            circle_bullets.remove(b)

        elif not box.collidepoint(b[0],b[1]):
            circle_bullets.remove(b)

    for b in wall_bullets[:]:

        b[0]+=b[2]
        b[1]+=b[3]

        pygame.draw.circle(screen,(255,255,0),(int(b[0]),int(b[1])),6)

        if player.collidepoint(b[0],b[1]):
            hp-=1
            wall_bullets.remove(b)

        elif not box.collidepoint(b[0],b[1]):
            wall_bullets.remove(b)

    # HEART

    screen.blit(
        heart_img,
        (
            player.centerx-heart_img.get_width()//2,
            player.centery-heart_img.get_height()//2
        )
    )

    # SOUL HELP

    if hp<max_hp/2 and not soul_help and not used_souls:
        soul_help=True
        used_souls=True

    if soul_help:

        hp=min(max_hp,hp+0.05)

        t=font.render("SOULS HELP YOU",True,(0,255,255))
        screen.blit(t,(280,100))

        if hp>=max_hp:
            soul_help=False

    # FLOWEY TEXT

    if text_timer==0 and phase>=2 and random.randint(1,120)==1:
        flowey_text=random.choice(messages)
        text_timer=120

    if text_timer>0:
        t=font.render(flowey_text,True,(255,0,0))
        screen.blit(t,(350,150))

    # PLAYER HP

    ratio=hp/max_hp

    pygame.draw.rect(screen,(0,0,0),(300,550,150,15))
    pygame.draw.rect(screen,(255,255,0),(300,550,150*ratio,15))
    pygame.draw.rect(screen,(255,255,255),(300,550,150,15),3)

    # FLOWEY HP

    f_ratio=flowey_hp/200

    bar_x=box.x+125
    bar_y=box.y-25

    pygame.draw.rect(screen,(0,0,0),(bar_x,bar_y,150,15))
    pygame.draw.rect(screen,(255,0,0),(bar_x,bar_y,150*f_ratio,15))
    pygame.draw.rect(screen,(255,255,255),(bar_x,bar_y,150,15),3)

    # FIGHT BUTTON

    if fight_mode:

        btn_w=140
        btn_h=40

        btn_x=box.centerx-btn_w//2
        btn_y=box.centery-btn_h//2

        pygame.draw.rect(screen,(255,255,255),(btn_x,btn_y,btn_w,btn_h),2)

        txt=font.render("FIGHT",True,(255,255,255))
        screen.blit(txt,(btn_x+30,btn_y+5))

    # WIN

    if flowey_hp<=0:

        t=font.render("YOU WIN",True,(255,255,0))
        screen.blit(t,(350,300))

        pygame.display.flip()
        pygame.time.delay(4000)

        running=False

    # GAME OVER

    if hp<=0:

        t=font.render("FLOWEY LAUGHS",True,(255,0,0))
        screen.blit(t,(300,300))

        pygame.display.flip()
        pygame.time.delay(3000)

        running=False

    pygame.display.flip()

pygame.quit()
sys.exit()