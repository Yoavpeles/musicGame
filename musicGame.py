import pygame
import random

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

def play_sequence(seq):
    for note in seq:
        notes[note].play()
        pygame.time.delay(500)  # Delay between notes

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

def show_main_menu():
    print("\nOptions:")
    print("p - Play the sequence again")
    print("i - Input manue")
    print("q - Quit the game")
    choice = input("Select an option: ").lower()
    return choice

def show_input_menu():
    print("\nOptions:")
    print("i - Input sequence")
    print("t - Test notes")
    print("b - go back")

    choice = input("Select an option: ").lower()
    return choice

def test_notes():
    while True:
         user_input = get_user_input()
         if user_input == "q":
             break
         user_sequence = generate_sequence(user_input)
         play_sequence(user_sequence)


def generate_sequence(user_input):
    print(user_input)
    return [mapping[char] for char in user_input]



def main():
    level = 1
    while True:
        print(f"\nLevel {level}")
        sequence = [random.choice(['C', 'D', 'E', 'F']) for _ in range(level + 2)]
        
        # Play the sequence
        play_sequence(sequence)
        
        while True:
            choice = show_main_menu()
            
            if choice == 'p':
                # Replay the sequence
                play_sequence(sequence)
            elif choice == 'i':

                choice = show_input_menu()
                
                if choice == "i":
                # Input the answer
                    user_input = get_user_input()
                    user_sequence = generate_sequence(user_input)
                    play_sequence(user_sequence)
                    
                    if user_sequence == sequence:
                        print("Correct! Moving to next level.")
                        level += 1
                        break
                    else:
                        print("Incorrect, try again.")
                if choice == "t":
                    test_notes()
                    
            elif choice == 'q':
                # Quit the game
                print("Thanks for playing!")
                pygame.quit()
                exit()
            else:
                print("Invalid option. Please choose again.")

if __name__ == "__main__":
    main()
