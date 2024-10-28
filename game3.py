import curses

def main(stdscr):
    # Initialize curses
    curses.curs_set(0)  # Hide cursor
    stdscr.nodelay(True)  # Non-blocking input
    stdscr.timeout(100)  # Refresh every 100ms
    
    # Player properties
    player = {'x': 1, 'y': 1, 'char': '@'}  # Player starts at (1, 1)

    # Generate a basic stage with walls and an exit
    stage = generate_stage(20, 10)

    while True:
        stdscr.clear()  # Clear the screen

        # Draw the stage
        draw_stage(stdscr, stage)

        # Draw the player
        stdscr.addch(player['y'], player['x'], player['char'])

        # Handle player movement
        key = stdscr.getch()
        if key == curses.KEY_UP and player['y'] > 1 and stage[player['y'] - 1][player['x']] != '#':
            player['y'] -= 1
        elif key == curses.KEY_DOWN and player['y'] < len(stage) - 2 and stage[player['y'] + 1][player['x']] != '#':
            player['y'] += 1
        elif key == curses.KEY_LEFT and player['x'] > 1 and stage[player['y']][player['x'] - 1] != '#':
            player['x'] -= 1
        elif key == curses.KEY_RIGHT and player['x'] < len(stage[0]) - 2 and stage[player['y']][player['x'] + 1] != '#':
            player['x'] += 1
        elif key == ord('q'):
            break  # Quit the game

        # Check if the player reaches the exit
        if stage[player['y']][player['x']] == '+':
            stdscr.addstr(0, 0, "You reached the exit! Press 'q' to quit.")
            stdscr.refresh()
            stdscr.timeout(-1)  # Wait for the user to quit
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

    return stage

def draw_stage(stdscr, stage):
    """Draw the stage to the screen."""
    for y, row in enumerate(stage):
        for x, ch in enumerate(row):
            stdscr.addch(y, x, ch)

if __name__ == "__main__":
    curses.wrapper(main)
