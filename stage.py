import random

def generate_stage(width, height):
    stage = [["#" for _ in range(width)] for _ in range(height)]
    for i in range(1, height-1):
        for j in range(1, width-1):
            if random.random() < 0.3:  # 30% chance to create an empty space
                stage[i][j] = "."
    return stage

def move_player(stage, player_pos, direction):
    x, y = player_pos
    new_pos = player_pos

    if direction == "w":  # Up
        new_pos = (x - 1, y)
    elif direction == "s":  # Down
        new_pos = (x + 1, y)
    elif direction == "a":  # Left
        new_pos = (x, y - 1)
    elif direction == "d":  # Right
        new_pos = (x, y + 1)

    # Check if new position is within bounds and walkable
    if 0 <= new_pos[0] < len(stage) and 0 <= new_pos[1] < len(stage[0]):
        if stage[new_pos[0]][new_pos[1]] == "." or stage[new_pos[0]][new_pos[1]] == "E":
            return new_pos
    return player_pos

def check_for_exit(stage, player_pos):
    x, y = player_pos
    return stage[x][y] == "E"

def generate_exit(stage):
    empty_spaces = [(i, j) for i, row in enumerate(stage) for j, cell in enumerate(row) if cell == "."]
    exit_pos = random.choice(empty_spaces)
    stage[exit_pos[0]][exit_pos[1]] = "E"

def render_stage(stage, player_pos):
    for i, row in enumerate(stage):
        for j, cell in enumerate(row):
            if (i, j) == player_pos:
                print("@", end="")
            else:
                print(cell, end="")
        print()  # Newline after each row

def main():
    width, height = 10, 10
    player_pos = (1, 1)
    
    stage = generate_stage(width, height)
    generate_exit(stage)
    
    while True:
        render_stage(stage, player_pos)
        move = input("Move (WASD): ").lower()
        player_pos = move_player(stage, player_pos, move)
        
        if check_for_exit(stage, player_pos):
            print("You've reached the exit! Generating new stage...")
            stage = generate_stage(width, height)
            generate_exit(stage)
            player_pos = (1, 1)  # Reset player position for new stage

if __name__ == "__main__":
    main()
