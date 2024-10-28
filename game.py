import curses
import random
import secrets
import pygame

pygame.init()

notes = {
    'C': pygame.mixer.Sound('C.wav'),
    'D': pygame.mixer.Sound('D.wav'),
    'E': pygame.mixer.Sound('E.wav'),
    'F': pygame.mixer.Sound('F.wav')
}

keys = ['a', 's', 'd', 'f']  # Mapping: a = C, s = D, etc.
mapping = {'a': 'C', 's': 'D', 'd': 'E', 'f': 'F'}

def get_user_input():
    inp = input("Enter the sequence (use 'a', 's', 'd', 'f'): ").strip()
    if not inp:  # Check if the input is empty
        print("Input cannot be empty. Please enter a valid sequence.")
        return get_user_input()  # Ask for input again

    for char in inp:
        if char not in mapping and char != "q":
            print("Invalid option. Please choose again.")
            return get_user_input()
        else:
            return inp

def play_sequence(seq):
    for note in seq:
        notes[note].play()
        pygame.time.delay(500)  # Delay between notes

def main(stdscr):
    curses.curs_set(0)  # Hide the cursor
    stdscr.nodelay(False)  # Wait for user input in command mode
    stdscr.timeout(-1)  # No timeout in command mode

    # Generate a random 12-digit seed for the entire gameplay
    game_seed = secrets.randbelow(10**12)  # Random 12-digit number
    stdscr.addstr(0, 0, f"Game Seed: {game_seed}")  # Display the seed for replay purposes
    stdscr.refresh()

    # Define stages (12 unique stages)
    stages = generate_stages(12, 20, 10, game_seed)
    current_stage = 1  # Start at stage 1

    player = {'x': 1, 'y': 1, 'char': '@'}  # Player starts at (1, 1)

    while True:
        stdscr.clear()  # Clear the screen

        # Draw the current stage
        draw_stage(stdscr, stages[current_stage]['map'])

        # Draw the player
        stdscr.addch(player['y'], player['x'], player['char'])

        # Handle command input (allow the player to type commands)
        command = handle_command_input(stdscr)

        if command == 'm':
            # Enter movement mode
            current_stage = movement_mode(stdscr, stages, current_stage, player)
            
        elif command == 'music':
            # Enter music mode (testing and playing notes anytime)
            music_mode(stdscr, current_stage)

        elif command == 'quit':
            break  # Quit the game


def generate_sequence(user_input):
    print(user_input)
    return [mapping[char] for char in user_input]



def music_mode(stdscr, current_stage):
    # This mode is for testing notes and playing sequences anytime
    while True:
        # Display the music mode menu
        stdscr.clear()
        stdscr.addstr(0, 0, "Music Mode: Press 't' to test notes, 'p' to play a sequence, 'q' to quit music mode.")
        stdscr.refresh()
        key = stdscr.getch()

        if key == ord('t'):
            test_notes()  # Let the player test individual notes
        elif key == ord('p'):
            # Play a random sequence for practice (not tied to the music lock)
            sequence = [random.choice(['C', 'D', 'E', 'F']) for _ in range(current_stage + 2)]
            play_sequence(sequence)  # Play the sequence
        elif key == ord('q'):
            break  # Quit music mode

def test_notes():
    while True:
        print("Test notes by pressing 'a', 's', 'd', or 'f'. Press 'q' to quit.")
        user_input = input("Enter a note (or 'q' to quit): ").strip().lower()
        if user_input == 'q':
            break
        elif user_input in mapping:
            notes[mapping[user_input]].play()  # Play the corresponding note
        else:
            print("Invalid input. Try again.")


def movement_mode(stdscr, stages, current_stage, player):
    curses.curs_set(0)  # Hide cursor in movement mode
    stdscr.nodelay(True)  # Non-blocking input in movement mode
    stdscr.timeout(100)  # Refresh rate in movement mode

    height, width = stdscr.getmaxyx()

    while True:
        stdscr.clear()  # Clear screen

        # Draw the current stage
        draw_stage(stdscr, stages[current_stage]['map'])

        # Draw the player
        stdscr.addch(player['y'], player['x'], player['char'])

        # Show the command menu at the bottom while moving
        stdscr.addstr(height - 1, 0, "In movement mode. Press '>' on the exit to go to the next stage or 'q' to quit movement.")
        stdscr.refresh()

        key = stdscr.getch()

        # Handle player movement
        if key == curses.KEY_UP and player['y'] > 1 and stages[current_stage]['map'][player['y'] - 1][player['x']] != '#':
            player['y'] -= 1
        elif key == curses.KEY_DOWN and player['y'] < stages[current_stage]['height'] - 2 and stages[current_stage]['map'][player['y'] + 1][player['x']] != '#':
            player['y'] += 1
        elif key == curses.KEY_LEFT and player['x'] > 1 and stages[current_stage]['map'][player['y']][player['x'] - 1] != '#':
            player['x'] -= 1
        elif key == curses.KEY_RIGHT and player['x'] < stages[current_stage]['width'] - 2 and stages[current_stage]['map'][player['y']][player['x'] + 1] != '#':
            player['x'] += 1
        elif stages[current_stage]['map'][player['y']][player['x']] == 'M':  # Player steps on a music lock
            stdscr.addstr(0, 0, "You have encountered a music lock!")
            stdscr.refresh()
            success = music_puzzle(current_stage)  # Trigger the music puzzle

            if success:
                stdscr.addstr(1, 0, "You unlocked the music lock.")
            else:
                stdscr.addstr(1, 0, "Failed to unlock the music lock. Try again.")
            
            stdscr.refresh()
            curses.napms(1000)  # Pause for a moment to show the result
        

        elif key == ord('q'):
            break  # Exit movement mode

        # Handle stage transition
        elif key == ord('>'):
            if stages[current_stage]['map'][player['y']][player['x']] == '+':  # Player is standing on the exit
                if current_stage < 12:  # Move to the next stage
                    current_stage += 1
                    player['x'], player['y'] = 1, 1  # Reset player to starting position
                    stdscr.addstr(height - 1, 0, f"Moved to stage {current_stage}!")  # Notify stage change
                    stdscr.refresh()
                    break  # Exit movement mode after stage transition

    return current_stage  # Return the new current stage after exiting movement mode

def music_puzzle(level):
    # The sequence length increases with the level
    sequence_length = level + 2
    sequence = [random.choice(['C', 'D', 'E', 'F']) for _ in range(sequence_length)]
    
    # Play the sequence
    play_sequence(sequence)
    
    # Get user input
    user_input = get_user_input()
    user_sequence = generate_sequence(user_input)
    
    # Check if the input matches the sequence
    if user_sequence == sequence:
        print("Correct! Moving to the next stage.")
        return True  # Success
    else:
        print("Incorrect sequence.")
        return False  # Failure


def handle_command_input(stdscr):
    """Handles the command input at the bottom of the screen, showing typed characters."""
    height, width = stdscr.getmaxyx()
    command = ""  # Initialize an empty command

    while True:
        # Show the prompt and the current command typed
        stdscr.addstr(height - 1, 0, "Enter 'm' to move, 'music' for music mode, 'quit' to quit the game. Command: ")
        stdscr.addstr(height - 1, len("Enter 'm' to move, 'music' for music mode, 'quit' to quit the game. Command: "), command)
        stdscr.refresh()

        key = stdscr.getch()  # Get user input

        if key == 10:  # Enter key
            break  # End command input on Enter
        elif key in (curses.KEY_BACKSPACE, 127, 8):  # Handle backspace
            if command:
                command = command[:-1]  # Remove last character
        elif 32 <= key <= 126:  # Printable characters
            if len(command) < width - len("Enter 'm' to move, 'music' for music mode, 'quit' to quit the game. Command: ") - 1:
                command += chr(key)  # Add the typed character to the command

        stdscr.addstr(height - 1, len("Enter 'm' to move, 'music' for music mode, 'quit' to quit the game. Command: "), " " * (width - len("Enter 'm' to move, 'music' for music mode, 'quit' to quit the game. Command: ") - 1))
        stdscr.refresh()

    stdscr.addstr(height - 1, 0, " " * (width - 1))  # Clear the entire command line after Enter
    stdscr.refresh()

    return command.strip()  # Return the typed command, stripped of whitespace

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
    for y, row in enumerate(stage):
        for x, ch in enumerate(row):
            stdscr.addch(y, x, ch)



if __name__ == "__main__":
    curses.wrapper(main)
