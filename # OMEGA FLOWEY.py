import pygame
import random
import sys
import math

pygame.init()
pygame.mixer.init()

WIDTH, HEIGHT = 900, 820
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("OMEGA FLOWEY V3 HARD")

clock = pygame.time.Clock()
font = pygame.font.SysFont("arial", 28)
small_font = pygame.font.SysFont("arial", 22)

# ---------- IMAGES ----------
flowey_img = pygame.image.load("flowey.png").convert_alpha()
flowey_img = pygame.transform.scale(flowey_img, (400, 350))

heart_img = pygame.image.load("heart.png").convert()
heart_img.set_colorkey((0, 0, 0))
heart_img = pygame.transform.scale(heart_img, (90, 80))

# ---------- MUSIC ----------
pygame.mixer.music.load("omega flowey undertale.mp3")
pygame.mixer.music.play(-1)
attack_sound = pygame.mixer.Sound("Voicy_Undertale Sound Effect - Attack.mp3")
# ---------- CONSTANTS ----------
box = pygame.Rect(200, 250, 400, 300)
menu_options = ["FIGHT", "ACT", "ITEM", "MERCY"]
messages = ["DIE", "HAHAHA", "NO ESCAPE", "YOU'RE TOO SLOW", "RUN.", "YOU CAN'T WIN."]
act_messages = [
    "You glare at Flowey.",
    "Flowey laughs at you.",
    "You stay determined.",
    "Flowey seems annoyed."
]

# ---------- RESET ----------
def reset_game():
    return {
        "player": pygame.Rect(box.centerx, box.centery, 16, 16),
        "speed": 2.0,

        "max_hp": 20,
        "hp": 20,

        "flowey_max_hp": 400,
        "flowey_hp": 400,

        "bullets": [],
        "rain_bullets": [],
        "circle_bullets": [],
        "wall_bullets": [],

        "attack_state": "idle",
        "attack_timer": 0,

        "fight_mode": False,
        "fight_bar_x": 0,
        "fight_bar_dir": 1,
        "fight_bar_speed": 10,

        "menu_index": 0,
        "turn_state": "menu",   # menu / attack / message / gameover / win

        "message_text": "Stay determined.",
        "message_timer": 90,

        "flowey_text": "",
        "flowey_text_timer": 0,

        "soul_help": False,
        "used_souls": False,

        "items": 1,

        "game_over": False,
        "win": False
    }

game = reset_game()

# ---------- FLOWEY ANIM ----------
flowey_x = 200
flowey_y = 0
flowey_time = 0

# ---------- HELPERS ----------
def clear_all_bullets():
    game["bullets"].clear()
    game["rain_bullets"].clear()
    game["circle_bullets"].clear()
    game["wall_bullets"].clear()

def set_message(text, duration=90):
    game["message_text"] = text
    game["message_timer"] = duration
    game["turn_state"] = "message"

def start_fight_mode():
    game["fight_mode"] = True
    game["turn_state"] = "menu"
    game["fight_bar_x"] = box.left + 20
    game["fight_bar_dir"] = 1
    game["fight_bar_speed"] = 10

def start_attack():
    if game["game_over"] or game["win"]:
        return

    attack = random.choice(["bullet", "rain", "circle", "wall"])
    game["attack_state"] = attack
    game["turn_state"] = "attack"
    game["fight_mode"] = False

    
    if attack == "bullet":
        game["attack_timer"] = 600   
    elif attack == "rain":
        game["attack_timer"] = 500
    elif attack == "circle":
        game["attack_timer"] = 440
    elif attack == "wall":
        game["attack_timer"] = 500

# ---------- ATTACK UPDATE ----------
    if game["attack_state"] == "bullet":
        game["attack_timer"] -= 1
        if game["attack_timer"] % 15 == 0:  
            spawn_bullet()
        if game["attack_timer"] <= 0:
            end_attack()

    elif game["attack_state"] == "rain":
        game["attack_timer"] -= 1
        if game["attack_timer"] % 10 == 0:
            spawn_rain()
        if game["attack_timer"] <= 0:
            end_attack()

    elif game["attack_state"] == "circle":
        game["attack_timer"] -= 1
        
        for t in [400, 350, 300, 250, 200, 150, 100, 50]:
            if game["attack_timer"] == t:
                spawn_circle()
        if game["attack_timer"] <= 0:
            end_attack()

    elif game["attack_state"] == "wall":
        game["attack_timer"] -= 1
        if game["attack_timer"] % 18 == 0:
            spawn_wall()
        if game["attack_timer"] <= 0:
            end_attack()   

def end_attack():
    clear_all_bullets()
    game["attack_state"] = "idle"
    game["turn_state"] = "menu"

def spawn_bullet():
    side = random.choice(["top", "bottom", "left", "right"])

    if side == "top":
        x = random.randint(box.left, box.right)
        y = box.top
        dx, dy = random.uniform(-2.5, 2.5), 4
    elif side == "bottom":
        x = random.randint(box.left, box.right)
        y = box.bottom
        dx, dy = random.uniform(-2.5, 2.5), -4
    elif side == "left":
        x = box.left
        y = random.randint(box.top, box.bottom)
        dx, dy = 4, random.uniform(-2.5, 2.5)
    else:
        x = box.right
        y = random.randint(box.top, box.bottom)
        dx, dy = -4, random.uniform(-2.5, 2.5)

    game["bullets"].append([x, y, dx, dy])

def spawn_rain():
    for _ in range(6):
        x = random.randint(box.left, box.right)
        y = box.top
        dx = random.uniform(-0.6, 0.6)
        dy = random.uniform(5.0, 6.5)
        game["rain_bullets"].append([x, y, dx, dy])

def spawn_circle():
    cx = box.centerx
    cy = box.centery

    for a in range(0, 360, 25):
        rad = math.radians(a)
        dx = math.cos(rad) * 3.8
        dy = math.sin(rad) * 3.8
        game["circle_bullets"].append([cx, cy, dx, dy])

def spawn_wall():
    y = random.randint(box.top + 30, box.bottom - 30)

    for i in range(8):
        x = box.left - i * 30
        dx = 5
        dy = 0
        game["wall_bullets"].append([x, y, dx, dy])

# ---------- FIGHT ----------
def do_fight_hit():
    center_x = box.centerx
    distance = abs(game["fight_bar_x"] - center_x)

    if distance < 10:
        attack_sound.play()
        damage = 25
    elif distance < 25:
        attack_sound.play()
        damage = 20
    elif distance < 45:
        attack_sound.play()
        damage = 12
    else:
        attack_sound.play()
        damage = 10

    game["flowey_hp"] -= damage
    if game["flowey_hp"] < 0:
        game["flowey_hp"] = 0

    game["fight_mode"] = False

    if game["flowey_hp"] <= 0:
        game["win"] = True
        game["turn_state"] = "win"
        clear_all_bullets()
    else:
        set_message(f"You dealt {damage} damage!", 60)

# ---------- MENU ACTIONS ----------
def use_menu_option():
    option = menu_options[game["menu_index"]]

    if option == "FIGHT":
        start_fight_mode()

    elif option == "ACT":
        set_message(random.choice(act_messages), 80)

    elif option == "ITEM":
        if game["items"] > 0 and game["hp"] < game["max_hp"]:
            game["items"] -= 1
            heal = 10
            game["hp"] = min(game["max_hp"], game["hp"] + heal)
            set_message(f"You used a potion. +{heal} HP", 80)
        elif game["items"] <= 0:
            set_message("No items left!", 70)
        else:
            set_message("HP is already full!", 70)

    elif option == "MERCY":
        if game["flowey_hp"] <= 20:
            game["win"] = True
            game["turn_state"] = "win"
            clear_all_bullets()
        else:
            set_message("Flowey refuses mercy.", 70)

# ---------- MAIN LOOP ----------
running = True

while running:
    clock.tick(60)

    # FLOWEY MOVE
    flowey_time += 1
    flowey_y = 5 * math.sin(flowey_time * 0.05)
    flowey_x = 200 + random.randint(-1, 1)

    # ---------- EVENTS ----------
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            if (game["game_over"] or game["win"]) and event.key == pygame.K_r:
                game = reset_game()
                continue

            if not game["game_over"] and not game["win"]:
                if game["fight_mode"]:
                    if event.key == pygame.K_SPACE:
                        do_fight_hit()

                elif game["turn_state"] == "menu":
                    if event.key == pygame.K_LEFT:
                        game["menu_index"] = (game["menu_index"] - 1) % len(menu_options)
                    elif event.key == pygame.K_RIGHT:
                        game["menu_index"] = (game["menu_index"] + 1) % len(menu_options)
                    elif event.key == pygame.K_SPACE:
                        use_menu_option()

    # ---------- TIMERS ----------
    if game["flowey_text_timer"] > 0:
        game["flowey_text_timer"] -= 1

    if game["turn_state"] == "message":
        if game["message_timer"] > 0:
            game["message_timer"] -= 1
        else:
            start_attack()

    # ---------- PLAYER MOVE ----------
    if game["turn_state"] == "attack" and not game["game_over"] and not game["win"]:
        keys = pygame.key.get_pressed()
        dx = 0
        dy = 0

        if keys[pygame.K_LEFT]:
            dx -= game["speed"]
        if keys[pygame.K_RIGHT]:
            dx += game["speed"]
        if keys[pygame.K_UP]:
            dy -= game["speed"]
        if keys[pygame.K_DOWN]:
            dy += game["speed"]

        game["player"].x += dx
        game["player"].y += dy
        game["player"].clamp_ip(box)

    # ---------- RANDOM FLOWEY TEXT ----------
    if game["flowey_text_timer"] == 0 and random.randint(1, 160) == 1 and not game["game_over"] and not game["win"]:
        game["flowey_text"] = random.choice(messages)
        game["flowey_text_timer"] = 100

    # ---------- SOUL HELP ----------
    if game["hp"] < game["max_hp"] / 2 and not game["soul_help"] and not game["used_souls"]:
        game["soul_help"] = True
        game["used_souls"] = True

    if game["soul_help"]:
        game["hp"] = min(game["max_hp"], game["hp"] + 0.03)
        if game["hp"] >= game["max_hp"]:
            game["soul_help"] = False

    # ---------- FIGHT BAR ----------
    if game["fight_mode"]:
        game["fight_bar_x"] += game["fight_bar_speed"] * game["fight_bar_dir"]

        left_limit = box.left + 20
        right_limit = box.right - 20

        if game["fight_bar_x"] <= left_limit:
            game["fight_bar_x"] = left_limit
            game["fight_bar_dir"] = 1

        if game["fight_bar_x"] >= right_limit:
            game["fight_bar_x"] = right_limit
            game["fight_bar_dir"] = -1

    # ---------- ATTACK UPDATE ----------
    if game["attack_state"] == "bullet":
        game["attack_timer"] -= 1

        if game["attack_timer"] % 18 == 0:
            spawn_bullet()

        if game["attack_timer"] <= 0:
            end_attack()

    elif game["attack_state"] == "rain":
        game["attack_timer"] -= 1

        if game["attack_timer"] % 14 == 0:
            spawn_rain()

        if game["attack_timer"] <= 0:
            end_attack()

    elif game["attack_state"] == "circle":
        game["attack_timer"] -= 1

        if game["attack_timer"] == 190:
            spawn_circle()
        if game["attack_timer"] == 140:
            spawn_circle()
        if game["attack_timer"] == 90:
            spawn_circle()
        if game["attack_timer"] == 40:
            spawn_circle()

        if game["attack_timer"] <= 0:
            end_attack()

    elif game["attack_state"] == "wall":
        game["attack_timer"] -= 1

        if game["attack_timer"] % 22 == 0:
            spawn_wall()

        if game["attack_timer"] <= 0:
            end_attack()

    # ---------- DRAW ----------
    screen.fill((0, 0, 0))
    screen.blit(flowey_img, (flowey_x, flowey_y))
    pygame.draw.rect(screen, (255, 255, 255), box, 3)

    # ---------- BULLETS ----------
    for b in game["bullets"][:]:
        b[0] += b[2]
        b[1] += b[3]
        pygame.draw.circle(screen, (255, 255, 255), (int(b[0]), int(b[1])), 6)

        if game["player"].collidepoint(b[0], b[1]):
            if not game["soul_help"]:
                game["hp"] -= 1
            game["bullets"].remove(b)
        elif not box.collidepoint(b[0], b[1]):
            game["bullets"].remove(b)

    for b in game["rain_bullets"][:]:
        b[0] += b[2]
        b[1] += b[3]
        pygame.draw.circle(screen, (0, 255, 255), (int(b[0]), int(b[1])), 6)

        if game["player"].collidepoint(b[0], b[1]):
            game["hp"] -= 1
            game["rain_bullets"].remove(b)
        elif not box.collidepoint(b[0], b[1]):
            game["rain_bullets"].remove(b)

    for b in game["circle_bullets"][:]:
        b[0] += b[2]
        b[1] += b[3]
        pygame.draw.circle(screen, (255, 0, 255), (int(b[0]), int(b[1])), 6)

        if game["player"].collidepoint(b[0], b[1]):
            game["hp"] -= 1
            game["circle_bullets"].remove(b)
        elif not box.collidepoint(b[0], b[1]):
            game["circle_bullets"].remove(b)

    for b in game["wall_bullets"][:]:
        b[0] += b[2]
        b[1] += b[3]
        pygame.draw.circle(screen, (255, 255, 0), (int(b[0]), int(b[1])), 6)

        if game["player"].collidepoint(b[0], b[1]):
            game["hp"] -= 1
            game["wall_bullets"].remove(b)
        elif not box.collidepoint(b[0], b[1]):
            game["wall_bullets"].remove(b)

    # ---------- HEART ----------
    screen.blit(
        heart_img,
        (
            game["player"].centerx - heart_img.get_width() // 2,
            game["player"].centery - heart_img.get_height() // 2
        )
    )

    # ---------- FLOWEY TEXT ----------
    if game["flowey_text_timer"] > 0:
        t = font.render(game["flowey_text"], True, (255, 0, 0))
        screen.blit(t, (300, 190))

    # ---------- SOUL HELP TEXT ----------
    if game["soul_help"]:
        t = small_font.render("SOULS HELP YOU", True, (0, 255, 255))
        screen.blit(t, (310, 165))

    # ---------- FLOWEY HP ----------
    f_ratio = game["flowey_hp"] / game["flowey_max_hp"]
    bar_x = box.x + 110
    bar_y = box.y - 28

    pygame.draw.rect(screen, (0, 0, 0), (bar_x, bar_y, 180, 16))
    pygame.draw.rect(screen, (255, 0, 0), (bar_x, bar_y, 180 * f_ratio, 16))
    pygame.draw.rect(screen, (255, 255, 255), (bar_x, bar_y, 180, 16), 2)

    # ---------- PLAYER HP ----------
    hp_ratio = game["hp"] / game["max_hp"]
    hp_bar_x = 270
    hp_bar_y = 650

    pygame.draw.rect(screen, (0, 0, 0), (hp_bar_x, hp_bar_y, 180, 16))
    pygame.draw.rect(screen, (255, 255, 0), (hp_bar_x, hp_bar_y, 180 * hp_ratio, 16))
    pygame.draw.rect(screen, (255, 255, 255), (hp_bar_x, hp_bar_y, 180, 16), 2)

    hp_text = small_font.render(f"HP {int(game['hp'])}/{game['max_hp']}", True, (255, 255, 255))
    screen.blit(hp_text, (460, 646))
    # ---------- MENU UI ----------
    menu_y = 700
    menu_xs = [90, 280, 470, 670]

    for i, option in enumerate(menu_options):
        color = (255, 255, 0) if i == game["menu_index"] and game["turn_state"] == "menu" and not game["fight_mode"] else (255, 255, 255)

        if option == "MERCY" and game["flowey_hp"] <= 20:
            color = (255, 255, 0)

        txt = font.render(option, True, color)
        screen.blit(txt, (menu_xs[i], menu_y))

    # ---------- ITEM COUNT ----------
    item_text = small_font.render(f"ITEMS: {game['items']}", True, (255, 255, 255))
    screen.blit(item_text, (20, 20))

    # ---------- MESSAGE BOX ----------
    msg_box = pygame.Rect(40, 560, 700, 60)
    pygame.draw.rect(screen, (0, 0, 0), msg_box)
    pygame.draw.rect(screen, (255, 255, 255), msg_box, 2)

    if game["turn_state"] == "message":
        msg = small_font.render(game["message_text"], True, (255, 255, 255))
        screen.blit(msg, (60, 570))
    elif game["turn_state"] == "menu" and not game["fight_mode"]:
        msg = small_font.render("Choose an action. LEFT/RIGHT + SPACE", True, (255, 255, 255))
        screen.blit(msg, (60, 570))
    elif game["turn_state"] == "attack":
        msg = small_font.render("DODGE!", True, (255, 255, 255))
        screen.blit(msg, (60, 570))

    # ---------- FIGHT BAR UI ----------
    if game["fight_mode"]:
        meter_y = 620
        meter_left = box.left + 20
        meter_width = box.width - 40

        pygame.draw.rect(screen, (255, 255, 255), (meter_left, meter_y, meter_width, 14), 2)

        center_zone = pygame.Rect(box.centerx - 10, meter_y, 20, 14)
        pygame.draw.rect(screen, (255, 0, 0), center_zone)

        pygame.draw.rect(screen, (255, 255, 0), (game["fight_bar_x"] - 3, meter_y - 4, 6, 22))

        tip = small_font.render("PRESS SPACE!", True, (255, 255, 255))
        screen.blit(tip, (60, 570))

    # ---------- GAME OVER / WIN ----------
    if game["flowey_hp"] <= 0 and not game["win"]:
        game["win"] = True
        game["turn_state"] = "win"
        clear_all_bullets()

    if game["hp"] <= 0 and not game["game_over"]:
        game["game_over"] = True
        game["turn_state"] = "gameover"
        game["fight_mode"] = False
        clear_all_bullets()

    if game["win"]:
        t = font.render("YOU WIN", True, (255, 255, 0))
        screen.blit(t, (340, 280))
        t2 = small_font.render("Press R to Restart", True, (255, 255, 255))
        screen.blit(t2, (315, 320))

    if game["game_over"]:
        t = font.render("FLOWEY LAUGHS", True, (255, 0, 0))
        screen.blit(t, (280, 280))
        t2 = small_font.render("Press R to Restart", True, (255, 255, 255))
        screen.blit(t2, (315, 320))

    pygame.display.flip()

pygame.quit()
sys.exit()