import os
import time
import random
import sys
import select


def clear_screen():
    os.system("clear")


def get_terminal_size():
    return os.get_terminal_size().columns, os.get_terminal_size().lines


def draw_scene(dino_y, obstacles, score):
    width, height = get_terminal_size()
    scene = [[" " for _ in range(width)] for _ in range(height)]

    for i in range(width):
        scene[height - 1][i] = "_"

    dino_x = 5
    scene[height - dino_y - 1][dino_x] = "A"
    scene[height - dino_y - 1][dino_x] = "|"
    scene[height - dino_y - 1][dino_x - 1] = "/"
    scene[height - dino_y - 1][dino_x + 1] = "\\"

    for obs_x, obs_height in obstacles:
        for i in range(obs_height):
            scene[height - i - 1][obs_x] = "|"

    score_str = f"Score: {score}"
    for i, char in enumerate(score_str):
        scene[0][width - len(score_str) + i] = char

    for row in scene:
        print("".join(row))


def is_collision(dino_y, obstacles):
    return any(obs_x == 5 and height > dino_y for obs_x, height in obstacles)


def main():
    width, height = get_terminal_size()
    dino_y = 0
    jump_height = 5
    jump_duration = 10
    jump_counter = 0
    obstacles = []
    score = 0
    game_speed = 0.1

    while True:
        clear_screen()

        if sys.stdin in select.select([sys.stdin], [], [], 0)[0]:
            key = sys.stdin.read(1)
            if key == " " and dino_y == 0:
                jump_counter = jump_duration

        if jump_counter > 0:
            dino_y = int(jump_height * (1 - (jump_counter / jump_duration) ** 2))
            jump_counter -= 1
        else:
            dino_y = 0

        obstacles = [(x - 1, h) for x, h in obstacles if x > 0]
        if not obstacles or obstacles[-1][0] < width - 20:
            if random.random() < 0.1:
                obstacles.append((width - 1, random.randint(2, 4)))

        if is_collision(dino_y, obstacles):
            print("Game Over!")
            break

        draw_scene(dino_y, obstacles, score)

        score += 1

        game_speed = max(0.01, game_speed - 0.0001)

        time.sleep(game_speed)


if __name__ == "__main__":
    os.system("stty -echo")
    os.system("stty cbreak")
    try:
        main()
    finally:
        os.system("stty echo")
        os.system("stty -cbreak")
