import random

def get_computer_choice():
    return random.choice(['Rock', 'Paper', 'Scissors'])

def get_user_choice():
    while True:
        user_choice = input('Please enter your choice (Rock, Paper, Scissors): ')
        if user_choice in ['Rock', 'Paper', 'Scissors']:
            return user_choice
        else:
            print('Invalid choice. Please try again.')

def get_winner(computer_choice, user_choice):
    if computer_choice == user_choice:
        print('It is a tie!')
    elif computer_choice == 'Rock' and user_choice == 'Paper':
        print('You won!')
    elif computer_choice == 'Paper' and user_choice == 'Scissors':
        print('You won!')
    elif computer_choice == 'Scissors' and user_choice == 'Rock':
        print('You won!')
    else:
        print('You lost')

def play():
    computer_choice = get_computer_choice()
    user_choice = get_user_choice()
    get_winner(computer_choice, user_choice)