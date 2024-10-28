import curses
import random
import secrets
import time
import pygame

# Initialize pygame for sound
pygame.init()

# Notes
notes = {
    'C': pygame.mixer.Sound('C.wav'),
    'D': pygame.mixer.Sound('D.wav'),
    'E': pygame.mixer.Sound('E.wav'),
    'F': pygame.mixer.Sound('F.wav')
}
keys = ['a', 's', 'd', 'f']  # Mapping: a = C, s = D, etc.
mapping = {'a': 'C', 's': 'D', 'd': 'E', 'f': 'F'}


def main(stdscr):
    curses.curs_set(0)  # Hide the cursor
    stdscr.nodelay(False)  # Wait for user input in command mode
    stdscr.timeout(-1)  # No timeout in command mode

    # Generate a random 12-digit seed for the entire gameplay
    game_seed = secrets.randbelow(10**12)  # Random 12-digit number
    stdscr.addstr(0, 0, f"Game Seed: {game_seed}")  # Display the seed for replay purposes
    stdscr.refresh()
    time.sleep(1)

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
        elif key == ord('>'):
            if stages[current_stage]['map'][player['y']][player['x']] == '+':  # Player is standing on the exit
                success = music_puzzle(stdscr,level=current_stage)
                if success:
                    if current_stage < 12:  # Move to the next stage if they pass the puzzle
                        current_stage += 1
                        player['x'], player['y'] = 1, 1  # Reset player to starting position
                        stdscr.addstr(height - 1, 0, f"Moved to stage {current_stage}!")  # Notify stage change
                        stdscr.refresh()
                        time.sleep(1)
                        break  # Exit movement mode after stage transition
                else:
                    stdscr.addstr(height - 1, 0, "Failed the music puzzle! Try again.")  # Notify failure
                    stdscr.refresh()
                    time.sleep(1)

        elif stages[current_stage]['map'][player['y']][player['x']] == 'M':  # Player steps on a music lock
            stdscr.addstr(0, 0, "You have encountered a music lock!")
            stdscr.refresh()
            time.sleep(1)
            success = music_puzzle(stdscr,current_stage)  # Trigger the music puzzle

            if success:
                stdscr.addstr(1, 0, "You unlocked the music lock.")
            else:
                stdscr.addstr(1, 0, "Failed to unlock the music lock. Try again.")
            
            stdscr.refresh()
            time.sleep(1)

            if stages[current_stage]['map'][player['y']][player['x']] == 'M':  # Player steps on a music lock
                success = music_puzzle(stdscr, current_stage)  # Trigger the music puzzle

                if success:
                    stdscr.addstr(1, 0, "You unlocked the music lock!")
                else:
                    stdscr.addstr(1, 0, "Failed to unlock the music lock. Try again.")

                stdscr.refresh()
                time.sleep(1)



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
                    time.sleep(1)
                    break  # Exit movement mode after stage transition

    return current_stage  # Return the new current stage after exiting movement mode

def music_mode(stdscr, current_stage):
    # This mode is for testing notes and playing sequences anytime
    sequence_length = current_stage + 2  # The sequence gets longer as the stage increases
    sequence = [random.choice(['C', 'D', 'E', 'F']) for _ in range(sequence_length)]
    
    while True:
        stdscr.clear()
        stdscr.addstr(0, 0, "Music Mode: Press 't' to test notes, 'p' to play a sequence, 'i' to input the sequence, 'q' to quit music mode.")
        stdscr.refresh()
        key = stdscr.getch()

        # if key == ord('t'):
        #     test_notes(stdscr)  # Let the player test individual notes
        if key == ord('p'):
            play_sequence(sequence)  # Play a random sequence for practice (not tied to the music lock)
        elif key == ord('i'):
            # Get the user input using the curses-based get_user_input
            user_input = get_user_input(stdscr, len(sequence))
            user_sequence = [mapping[char] for char in user_input]  # Convert user input to note sequence
            
            # Check if the user input matches the sequence
            if user_sequence == sequence:
                stdscr.addstr(1, 0, "Correct! The lock is unlocked.")
                stdscr.refresh()
                time.sleep(1)
                break  # Exit music mode on success
            else:
                stdscr.addstr(1, 0, "Incorrect sequence. Try again.")
                stdscr.refresh()
                time.sleep(1)
        elif key == ord('q'):
            break  # Quit music mode

# def test_notes():
#     while True:
#         print("Test notes by pressing 'a', 's', 'd', or 'f'. Press 'q' to quit.")
#         user_input = input("Enter a note (or 'q' to quit): ").strip().lower()
#         if user_input == 'q':
#             break
#         elif user_input in mapping:
#             notes[mapping[user_input]].play()  # Play the corresponding note
#         else:
#             print("Invalid input. Try again.")


def music_puzzle(stdscr, level):
    """Play a sequence of notes and ask the player to reproduce it."""
    sequence_length = level + 2  # The sequence length increases with the level
    sequence = [random.choice(['C', 'D', 'E', 'F']) for _ in range(sequence_length)]  # Generate a random note sequence

    # Display instructions
    height, width = stdscr.getmaxyx()
    stdscr.clear()
    stdscr.addstr(0, 0, "Music Puzzle: Listen to the sequence and repeat it.")
    stdscr.addstr(1, 0, "Press 'a', 's', 'd', or 'f' to input the sequence. Press 'q' to quit.")
    stdscr.refresh()
    
    # Play the generated sequence
    play_sequence(sequence, stdscr)

    # Get user input and compare
    user_input = get_user_input(stdscr, len(sequence))  # Get the player's input for the same length as the sequence
    user_sequence = [mapping[char] for char in user_input]  # Convert the input keys to note sequence

    # Check if the user's input matches the generated sequence
    if user_sequence == sequence:
        stdscr.addstr(2, 0, "Correct! You solved the puzzle.")
        stdscr.refresh()
        time.sleep(1)
        return True  # Success
    else:
        stdscr.addstr(2, 0, "Incorrect sequence. Try again.")
        stdscr.refresh()
        time.sleep(1)
        return False  # Failure


def play_sequence(sequence, stdscr):
    """Plays a sequence of notes using pygame and updates the terminal."""
    for note in sequence:
        stdscr.clear()
        stdscr.addstr(0, 0, f"Playing note: {note}")  # Display the note being played
        stdscr.refresh()
        notes[note].play()  # Play the sound using pygame
        pygame.time.delay(500)  # Add a 500ms delay between notes
        time.sleep(0.5)  # Pause in the terminal to let the player process


def get_user_input(stdscr, length):
    """Get user input for a sequence of notes, limited by the length of the sequence."""
    user_input = []
    height, width = stdscr.getmaxyx()

    # Prompt the user to enter the sequence
    stdscr.addstr(height - 2, 0, "Enter the sequence: ")
    stdscr.refresh()

    while len(user_input) < length:
        key = stdscr.getch()

        # Capture only valid keys ('a', 's', 'd', 'f')
        if chr(key) in mapping:
            user_input.append(chr(key))  # Store the valid input character
            stdscr.addch(height - 2, len("Enter the sequence: ") + len(user_input) - 1, chr(key))  # Display the character

    return user_input  # Return the list of valid keys pressed

def generate_sequence(user_input):
    return [mapping[char] for char in user_input]


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
