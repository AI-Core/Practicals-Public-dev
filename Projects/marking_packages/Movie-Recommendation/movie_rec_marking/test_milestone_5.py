from io import StringIO
from contextlib import redirect_stdout
from unittest.mock import patch
import json
import urllib.request
import timeout_decorator

urllib.request.urlretrieve("https://aicore-files.s3.amazonaws.com/Movie-Recommendation/movies.json", "movies.json")

with open('movies.json') as f:
    movies = json.load(f)

n_movies = len(movies)
def get_unique_genres():
    genres = [m["genre"] for m in movies] # one line filter
    genres = set(genres)
    return genres

genres = get_unique_genres()
n_unique_genres = len(genres)

def get_movies_in_genre(genre):
    return [movie for movie in movies if movie["genre"] == genre]

@timeout_decorator.timeout(5, timeout_exception=TimeoutError)
def check_first_get_user_genre_choice(func):
    try:
        f = StringIO()
        with redirect_stdout(f):
            with patch('builtins.input', return_value='Action'):
                func()
    except TimeoutError:
        print('The "get_user_genre_choice" function takes too long to run')
        print('Make sure you use the "input" function ONLY ONCE to ask for the genre')
        print('Please, try again, and don\'t continue until you get the correct output')
        return False
    except:
        print('Something went wrong with the "get_user_genre_choice" function')
        print('Make sure you call the "get_unique_genres" function inside the "get_user_genre_choice" function')
        print('Make sure you can run it without any errors, and that the function doesn\'t take any arguments')
        print('Please, try again, and don\'t continue until you get the correct output')
        return False
    
    try:
        f = StringIO()
        with redirect_stdout(f):
            with patch('builtins.input', return_value='Rubbish Input'):
                movies_in = func()
    except:
        if 'movies_in' in locals():
            print('The "get_user_genre_choice" function should not return anything when the entered genre is not in the list')
            print('It should simply raise a general exception')
            print('Please, try again, and don\'t continue until you get the correct output')
            return False
        print('Great! The "get_user_genre_choice" function raises an error when you use a genre that is not in the dataset')
        print('You can continue to the next task')
        return True
    else:
        print('The "get_user_genre_choice" function should raise an error when you use a genre that is not in the dataset')
        print('Please, try again, and don\'t continue until you get the correct output')
        return False


@timeout_decorator.timeout(5, timeout_exception=TimeoutError)
def check_second_get_user_genre_choice(func, task_1):
    # Now the user should use a ValueError exception
    if not task_1:
        print('Please, complete the previous task before continuing')
        return False

    try:
        f = StringIO()
        with redirect_stdout(f):
            with patch('builtins.input', return_value='Action'):
                func()
    except TimeoutError:
        print('The "get_user_genre_choice" function takes too long to run')
        print('Make sure you use the "input" function ONLY ONCE to ask for the genre')
        print('Please, try again, and don\'t continue until you get the correct output')
        return False
    except:
        print('The "get_user_genre_choice" function is not defined correctly')
        print('Make sure you call the "get_unique_genres" function inside the "get_user_genre_choice" function')
        print('Make sure you can run it without any errors, and that the function doesn\'t take any arguments')
        print('Please, try again, and don\'t continue until you get the correct output')
        return False
    try:
        # Capture the printed output
        f = StringIO()
        with redirect_stdout(f):
            with patch('builtins.input', return_value='Rubbish Input'):
                movies_in = func()
    except ValueError:
        if 'movies_in' in locals():
            print('The "get_user_genre_choice" function should not return anything when the entered genre is not in the list')
            print('It should simply raise a ValueError exception')
            print('Please, try again, and don\'t continue until you get the correct output')
            return False
        print('Great! The "get_user_genre_choice" function raises a ValueError exception when you use a genre that is not in the dataset')
        print('You can continue to the next task')
        return True
    except TimeoutError:
        print('The "get_user_genre_choice" function takes too long to run')
        print('Make sure you use the "input" function ONLY ONCE to ask for the genre')
        print('Please, try again, and don\'t continue until you get the correct output')
        return False
    except:
        print('The "get_user_genre_choice" function should raise a ValueError exception when you use a genre that is not in the dataset')
        print('In your case, it raises a different exception')
        print('Please, try again, and don\'t continue until you get the correct output')
        return False
    else:
        print('The "get_user_genre_choice" function should raise a ValueError exception when you use a genre that is not in the dataset')
        print('In your case, it doesn\'t raise any exception')
        print('Please, try again, and don\'t continue until you get the correct output')
        return False


@timeout_decorator.timeout(5, timeout_exception=TimeoutError)
def check_third_get_user_genre_choice(func, task_2):
    if not task_2:
        print('Please, complete the previous task before continuing')
        return False
    
    try:
        f = StringIO()
        with redirect_stdout(f):
            with patch('builtins.input', return_value='Action'):
                func()
    except TimeoutError:
        print('The "get_user_genre_choice" function takes too long to run')
        print('Make sure you use the "input" function ONLY ONCE to ask for the genre')
        print('Please, try again, and don\'t continue until you get the correct output')
        return False
    except:
        print('The "get_user_genre_choice" function is not defined correctly')
        print('Make sure you call the "get_unique_genres" function inside the "get_user_genre_choice" function')
        print('Make sure you can run it without any errors, and that the function doesn\'t take any arguments')
        print('Please, try again, and don\'t continue until you get the correct output')
        return False

    # Ask for two rubbish inputs and one correct input
    try:
        f = StringIO()
        with redirect_stdout(f):
            with patch('builtins.input', side_effect=['Rubbish Input', 'Rubbish Input 2', 'Action']):
                movies_in = func()
    # In the last attempt, the script should not raise an exception
    except ValueError:
        print('The "get_user_genre_choice" function should catch the ValueError exception, make sure you use a "try-except" block inside the function')
        print('Please, try again, and don\'t continue until you get the correct output')
        return False
    except TimeoutError:
        print('The "get_user_genre_choice" function takes too long to run')
        print('Make sure you use the "input" function ONLY ONCE to ask for the genre')
        print('The "input" function should be called once to ask for the genre, and if the user enters a wrong genre, it should be called again')
        print('Please, try again, and don\'t continue until you get the correct output')
        return False

    # output = f.getvalue()
    if 'movies_in' not in locals():
        print('The "get_user_genre_choice" function doesn\'t return anything')
        print('Please, try again, and don\'t continue until you get the correct output')
        return False
    if not movies_in:
        print('The "get_user_genre_choice" function should return the selected genre when the user enters a correct genre')
        print('Please, try again, and don\'t continue until you get the correct output')
        return False
    if movies_in == 'Rubbish Input':
        print('The "get_user_genre_choice" function should iteratively ask for the genre until the user enters a correct genre')
        print('The marking system enters "Rubbish Input" as the first input, so the next action for the function should be to ask for the genre again')
        print('Please, try again, and don\'t continue until you get the correct output')
        return False
    if movies_in != 'Action':
        print('The "get_user_genre_choice" function should return the selected genre when the user enters a correct genre')
        print('In your case, it returns a different genre')
        print('Please, try again, and don\'t continue until you get the correct output')
        return False
    print('Great! The "get_user_genre_choice" function works correctly')
    print("Congratulations! You completed the project!")

        


