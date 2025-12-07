import os
import sys
import time
import random
import threading
import termios
import tty
import shutil

# ===== VIRTUAL RESOLUTION (YOUR REQUEST) =====
VIRTUAL_WIDTH = 60
VIRTUAL_HEIGHT = 18

# ===== AUTO SCALE TO TERMINAL =====
term_cols, term_rows = shutil.get_terminal_size()
SCALE_X = VIRTUAL_WIDTH // term_cols
SCALE_Y = VIRTUAL_HEIGHT // term_rows

WIDTH = max(40, term_cols)
HEIGHT = max(20, term_rows - 4)

# ===== GAME STATE =====
direction = "RIGHT"
game_over = False
paused = False
score = 0
lives = 3
speed = 0.12
high_score = 0

snake = [(5, 5), (4, 5), (3, 5)]
food = (10, 10)
obstacles = []

# ===== LOAD HIGH SCORE =====
if os.path.exists("highscore.txt"):
    with open("highscore.txt", "r") as f:
        high_score = int(f.read().strip())

# ===== TERMINAL CLEAR =====
def clear():
    os.system("cls" if os.name == "nt" else "clear")

# ===== FOOD SPAWN =====
def spawn_food():
    global food
    while True:
        f = (
            random.randint(1, WIDTH - 2),
            random.randint(1, HEIGHT - 2)
        )
        if f not in snake and f not in obstacles:
            food = f
            return

# ===== OBSTACLES =====
def spawn_obstacles():
    obstacles.clear()
    for _ in range(10):
        r = (
            random.randint(3, WIDTH - 4),
            random.randint(3, HEIGHT - 4)
        )
        obstacles.append(r)

# ===== INPUT THREAD =====
def input_thread():
    global direction, game_over, paused
    while not game_over:
        ch = sys.stdin.read(1)

        if ch == "w" and direction != "DOWN":
            direction = "UP"
        elif ch == "s" and direction != "UP":
            direction = "DOWN"
        elif ch == "a" and direction != "RIGHT":
            direction = "LEFT"
        elif ch == "d" and direction != "LEFT":
            direction = "RIGHT"
        elif ch == "p":
            paused = not paused
        elif ch == "q":
            game_over = True

# ===== GAME MOVE =====
def move():
    global game_over, lives, score, speed

    if paused:
        return

    head_x, head_y = snake[0]

    if direction == "UP":
        head_y -= 1
    elif direction == "DOWN":
        head_y += 1
    elif direction == "LEFT":
        head_x -= 1
    elif direction == "RIGHT":
        head_x += 1

    new_head = (head_x, head_y)

    # WALL OR OBSTACLE HIT
    if (
        head_x <= 0 or head_x >= WIDTH - 1 or
        head_y <= 0 or head_y >= HEIGHT - 1 or
        new_head in snake or
        new_head in obstacles
    ):
        lives -= 1
        sys.stdout.write("\a")  # beep
        sys.stdout.flush()
        time.sleep(0.3)

        if lives <= 0:
            game_over = True
            return
        else:
            reset_round()
            return

    snake.insert(0, new_head)

    if new_head == food:
        score += 10
        speed = max(0.05, speed - 0.005)
        spawn_food()
    else:
        snake.pop()

# ===== RESET AFTER DEATH =====
def reset_round():
    global snake, direction
    snake = [(5, 5), (4, 5), (3, 5)]
    direction = "RIGHT"

# ===== DRAW FRAME =====
def draw():
    clear()

    print(f" SCORE: {score} | LIVES: {'❤' * lives} | HIGH: {high_score} | SPEED: {round(speed,3)}")
    print("=" * WIDTH)

    for y in range(HEIGHT):
        for x in range(WIDTH):
            if x == 0 or x == WIDTH - 1 or y == 0 or y == HEIGHT - 1:
                print("█", end="")
            elif (x, y) == food:
                print("🍎", end="")
            elif (x, y) in obstacles:
                print("▒", end="")
            elif (x, y) in snake:
                print("🟩", end="")
            else:
                print(" ", end="")
        print()

    print(" Controls: W A S D | P = Pause | Q = Quit")

# ===== MAIN LOOP =====
def main():
    global high_score

    spawn_food()
    spawn_obstacles()

    threading.Thread(target=input_thread, daemon=True).start()

    while not game_over:
        move()
        draw()
        time.sleep(speed)

    if score > high_score:
        with open("highscore.txt", "w") as f:
            f.write(str(score))

    clear()
    print(" GAME OVER ")
    print(" FINAL SCORE:", score)
    print(" HIGH SCORE:", max(score, high_score))

# ===== RAW TERMINAL INIT =====
if __name__ == "__main__":
    fd = sys.stdin.fileno()
    old = termios.tcgetattr(fd)
    tty.setcbreak(fd)

    try:
        main()
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old)
