import curses
import random
import secrets
import pygame
import time

# Initialize Pygame for sound
pygame.mixer.init()

# Define sound notes
notes = {
    'C': pygame.mixer.Sound('C.wav'),
    'D': pygame.mixer.Sound('D.wav'),
    'E': pygame.mixer.Sound('E.wav'),
    'F': pygame.mixer.Sound('F.wav')
}

# Map keys to note names
note_keys = {'c': 'C', 'd': 'D', 'e': 'E', 'f': 'F'}

def main(stdscr):
    # Initialize curses
    curses.curs_set(0)  # Hide cursor
    stdscr.nodelay(True)  # Non-blocking input
    stdscr.timeout(100)  # Refresh every 100ms
    
    # Player properties
    player = {'x': 1, 'y': 1, 'char': '@'}  # Player starts at (1, 1)

# Generate a random 12-digit seed for the entire gameplay
    game_seed = secrets.randbelow(10**12)  # Random 12-digit number
    stdscr.addstr(0, 0, f"Game Seed: {game_seed}")  # Display the seed for replay purposes
    stdscr.refresh()
    time.sleep(1)


    # Generate multiple stages
    num_stages = 3
    stages = generate_stages(2, 20, 10, game_seed)
    current_stage = 1  # Start at stage 1

    # Store puzzles for each stage
    puzzles = [generate_music_puzzle(current_stage) for current_stage in range(num_stages)]
    puzzle_solved = [False] * num_stages  # Track whether the puzzle is solved for each stage

    # Track if the music puzzle has been attempted
    puzzle_failed = False
    last_position = (player['x'], player['y'])

    while True:
        stdscr.clear()  # Clear the screen

        # Draw the current stage map
        draw_stage(stdscr, stages[current_stage]['map'])

        # Draw the player
        stdscr.addch(player['y'], player['x'], player['char'])

        # Handle player movement
        key = stdscr.getch()
        if key == curses.KEY_UP and player['y'] > 1 and stages[current_stage]['map'][player['y'] - 1][player['x']] != '#':
            player['y'] -= 1
        elif key == curses.KEY_DOWN and player['y'] < len(stages[current_stage]['map']) - 2 and stages[current_stage]['map'][player['y'] + 1][player['x']] != '#':
            player['y'] += 1
        elif key == curses.KEY_LEFT and player['x'] > 1 and stages[current_stage]['map'][player['y']][player['x'] - 1] != '#':
            player['x'] -= 1
        elif key == curses.KEY_RIGHT and player['x'] < len(stages[current_stage]['map'][0]) - 2 and stages[current_stage]['map'][player['y']][player['x'] + 1] != '#':
            player['x'] += 1
        elif key == ord('q'):
            break  # Quit the game

        # If the player moved, reset the puzzle_failed flag if they left the tile
        if (player['x'], player['y']) != last_position:
            last_position = (player['x'], player['y'])  # Update last known position
            if stages[current_stage]['map'][player['y']][player['x']] != 'M':
                puzzle_failed = False  # Reset if the player moved off the music tile

        # Check if the player reaches the music lock
        if stages[current_stage]['map'][player['y']][player['x']] == 'M' and not puzzle_solved[current_stage] and not puzzle_failed:
            success = music_puzzle(stdscr, puzzles[current_stage])
            if success:
                stdscr.addstr(0, 0, "You unlocked the music lock!")
                puzzle_solved[current_stage] = True  # Mark puzzle as solved for this stage
            else:
                stdscr.addstr(0, 0, "Failed the music puzzle. Try again.")
                play_sound('you_are_a_loser.wav')
                puzzle_failed = True  # Mark puzzle as failed, don't replay until player moves away
            stdscr.refresh()
            time.sleep(1)

        # Check if the player reaches the exit
        if stages[current_stage]['map'][player['y']][player['x']] == '+':
            if not puzzle_solved[current_stage]:
                play_sound("door_locked.wav")
            else:
                if current_stage < num_stages - 1:
                    current_stage += 1  # Go to the next stage
                    player['x'], player['y'] = 1, 1  # Reset player to the starting position
                else:
                    play_sound('end0.wav')
                    play_sound('end1.wav')
                    play_sound('end2.wav')
                    play_sound('end3.wav')
                    stdscr.addstr(0, 0, "You finished all stages! Press 'q' to quit.")
                    stdscr.refresh()
                    stdscr.timeout(-1)
                    while stdscr.getch() != ord('q'):
                        pass
                    break

def play_sound(arg):
    sound= pygame.mixer.Sound(arg)
    sound.play()
    pygame.time.wait(int(sound.get_length() * 1000)) 

def generate_stages(num_stages, width, height, game_seed):
    stages = {}
    for i in range(1, num_stages + 1):
        stage = generate_stage(width, height, game_seed, i)  # Use game_seed and stage number for uniqueness
        stages[i] = {'map': stage, 'width': width, 'height': height}
    return stages

def generate_stage(width, height, game_seed, stage_number):
    stage = []

    # Seed the random generator with the game seed combined with the stage number
    random.seed(game_seed + stage_number)

    # Generate empty stage with boundary walls
    for y in range(height):
        row = []
        for x in range(width):
            if y == 0 or y == height - 1 or x == 0 or x == width - 1:
                row.append('#')  # Boundary walls
            else:
                row.append(' ')  # Empty space inside
        stage.append(row)

    # Place obstacles randomly
    obstacle_count = 10
    for _ in range(obstacle_count):
        while True:
            x = random.randint(1, width - 2)
            y = random.randint(1, height - 2)
            if stage[y][x] == ' ':
                stage[y][x] = '#'
                break

    # Add an exit at a random position on the right side of the stage
    exit_x = width - 2
    exit_y = random.randint(1, height - 2)
    stage[exit_y][exit_x] = '+'

    # Add a music lock at a random position
    music_lock_x = random.randint(1, width - 2)
    music_lock_y = random.randint(1, height - 2)
    stage[music_lock_y][music_lock_x] = 'M'  # Music lock tile

    return stage


def draw_stage(stdscr, stage):
    """Draw the stage to the screen."""
    for y, row in enumerate(stage):
        for x, ch in enumerate(row):
            stdscr.addch(y, x, ch)

def generate_music_puzzle(level):
    """Generate a permanent sequence of notes for the current stage."""
    sequence_length = level + 2  # The sequence length increases with the level
    sequence = [random.choice(['C', 'D', 'E', 'F']) for _ in range(sequence_length)]
    return sequence

def music_puzzle(stdscr, sequence):
    """Play a sequence of notes and ask the player to reproduce it."""
    # Play the stored sequence
    play_sequence(sequence, stdscr)

    # Get user input and compare
    user_input = get_user_input(stdscr, len(sequence))  # Get the player's input for the same length as the sequence
    user_sequence = [note_keys[char] for char in user_input]  # Convert the input keys to note sequence

    # Check if the user's input matches the stored sequence
    if user_sequence == sequence:
        return True  # Success
    else:
        return False  # Failure

def play_sequence(sequence, stdscr):
    """Plays a sequence of notes using pygame and updates the terminal."""
    height, s = stdscr.getmaxyx()
    for note in sequence:
        
        stdscr.addstr(height - 1, 0, f"Playing note: {note}")  # Display the note being played
        stdscr.refresh()
        notes[note].play()  # Play the sound using pygame
        time.sleep(0.5)  # Pause between notes
    stdscr.addstr(height - 1, 0, "                                                        ")  # Display the note being played

def get_user_input(stdscr, length):
    """Get user input for a sequence of notes, limited by the length of the sequence."""
    user_input = []
    height, width = stdscr.getmaxyx()

    # Prompt the user to enter the sequence
    stdscr.addstr(height - 2, 0, "Enter the sequence (use 'c', 'd', 'e', 'f'): ")
    stdscr.refresh()

    while len(user_input) < length:
        key = stdscr.getch()

        if key in map(ord, 'cdef'):  # Only accept valid input keys
            char = chr(key)
            user_input.append(char)
            stdscr.addch(height - 2, len("Enter the sequence (use 'c', 'd', 'e', 'f'): ") + len(user_input) - 1, char)
            stdscr.refresh()
    user_sequence = [note_keys[char] for char in user_input]
    play_sequence(user_sequence,stdscr)
    return user_input

if __name__ == "__main__":
    curses.wrapper(main)
