import curses
import random
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
note_keys = {'a': 'C', 's': 'D', 'd': 'E', 'f': 'F'}

def main(stdscr):
    # Initialize curses
    curses.curs_set(0)  # Hide cursor
    stdscr.nodelay(True)  # Non-blocking input
    stdscr.timeout(100)  # Refresh every 100ms
    
    # Player properties
    player = {'x': 1, 'y': 1, 'char': '@'}  # Player starts at (1, 1)

    # Generate multiple stages
    num_stages = 3
    stages = [generate_stage(20, 10) for _ in range(num_stages)]
    current_stage = 0

    # Track if the music puzzle has been attempted
    puzzle_failed = False
    last_position = (player['x'], player['y'])

    while True:
        stdscr.clear()  # Clear the screen

        # Draw the current stage
        draw_stage(stdscr, stages[current_stage])

        # Draw the player
        stdscr.addch(player['y'], player['x'], player['char'])

        # Handle player movement
        key = stdscr.getch()
        if key == curses.KEY_UP and player['y'] > 1 and stages[current_stage][player['y'] - 1][player['x']] != '#':
            player['y'] -= 1
        elif key == curses.KEY_DOWN and player['y'] < len(stages[current_stage]) - 2 and stages[current_stage][player['y'] + 1][player['x']] != '#':
            player['y'] += 1
        elif key == curses.KEY_LEFT and player['x'] > 1 and stages[current_stage][player['y']][player['x'] - 1] != '#':
            player['x'] -= 1
        elif key == curses.KEY_RIGHT and player['x'] < len(stages[current_stage][0]) - 2 and stages[current_stage][player['y']][player['x'] + 1] != '#':
            player['x'] += 1
        elif key == ord('q'):
            break  # Quit the game

        # If the player moved, reset the puzzle_failed flag if they left the tile
        if (player['x'], player['y']) != last_position:
            last_position = (player['x'], player['y'])  # Update last known position
            if stages[current_stage][player['y']][player['x']] != 'M':
                puzzle_failed = False  # Reset if the player moved off the music tile

        # Check if the player reaches the music lock
        if stages[current_stage][player['y']][player['x']] == 'M' and not puzzle_failed:
            success = music_puzzle(stdscr, current_stage)
            if success:
                stdscr.addstr(0, 0, "You unlocked the music lock!")
                puzzle_failed = True
            else:
                stdscr.addstr(0, 0, "Failed the music puzzle. Try again.")
                puzzle_failed = True  # Mark puzzle as failed, don't replay until player moves away
            stdscr.refresh()
            time.sleep(1)

        # Check if the player reaches the exit
        if stages[current_stage][player['y']][player['x']] == '+':
            if current_stage < num_stages - 1:
                current_stage += 1  # Go to the next stage
                player['x'], player['y'] = 1, 1  # Reset player to the starting position
            else:
                stdscr.addstr(0, 0, "You finished all stages! Press 'q' to quit.")
                stdscr.refresh()
                stdscr.timeout(-1)
                while stdscr.getch() != ord('q'):
                    pass
                break

def generate_stage(width, height):
    """Generate a basic stage with boundary walls and an exit."""
    stage = []
    for y in range(height):
        row = []
        for x in range(width):
            if y == 0 or y == height - 1 or x == 0 or x == width - 1:
                row.append('#')  # Boundary walls
            else:
                row.append(' ')  # Empty space
        stage.append(row)

    # Add an exit at a random position on the right side of the stage
    exit_x = width - 2
    exit_y = height // 2  # Place exit at the middle of the right side
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

def music_puzzle(stdscr, level):
    """Play a sequence of notes and ask the player to reproduce it."""
    sequence_length = level + 2  # The sequence length increases with the level
    sequence = [random.choice(['C', 'D', 'E', 'F']) for _ in range(sequence_length)]  # Generate a random note sequence

    # Play the generated sequence
    play_sequence(sequence, stdscr)

    # Get user input and compare
    user_input = get_user_input(stdscr, len(sequence))  # Get the player's input for the same length as the sequence
    user_sequence = [note_keys[char] for char in user_input]  # Convert the input keys to note sequence

    # Check if the user's input matches the generated sequence
    if user_sequence == sequence:
        return True  # Success
    else:
        return False  # Failure

def play_sequence(sequence, stdscr):
    """Plays a sequence of notes using pygame and updates the terminal."""
    for note in sequence:
        stdscr.clear()
        stdscr.addstr(0, 0, f"Playing note: {note}")  # Display the note being played
        stdscr.refresh()
        notes[note].play()  # Play the sound using pygame
        time.sleep(0.5)  # Pause between notes

def get_user_input(stdscr, length):
    """Get user input for a sequence of notes, limited by the length of the sequence."""
    user_input = []
    height, width = stdscr.getmaxyx()

    # Prompt the user to enter the sequence
    stdscr.addstr(height - 2, 0, "Enter the sequence (use 'a', 's', 'd', 'f'): ")
    stdscr.refresh()

    while len(user_input) < length:
        key = stdscr.getch()

        if key in map(ord, 'asdf'):  # Only accept valid input keys
            char = chr(key)
            user_input.append(char)
            stdscr.addch(height - 2, len("Enter the sequence (use 'a', 's', 'd', 'f'): ") + len(user_input) - 1, char)
            stdscr.refresh()

    return user_input

if __name__ == "__main__":
    curses.wrapper(main)
