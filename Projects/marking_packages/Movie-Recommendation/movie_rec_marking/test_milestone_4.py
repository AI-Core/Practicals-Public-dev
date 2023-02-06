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
def check_get_user_genre_choice(func):
    # Check that the function asks for an input and then it prints
    # the number of unique genres based on the input
    try:
        f = StringIO()
        with redirect_stdout(f):
            with patch('builtins.input', return_value='Action'):
                genre = func()
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

    if not genre:
        print('The "get_user_genre_choice" doesn\'t return anything')
        print('Make sure it uses the "return" keyword to return the genres set')
        print('Please, try again, and don\'t continue until you get the correct output')
        return False

    if not isinstance(genre, str):
        print('The "get_user_genre_choice" function doesn\'t return a string')
        print('Please, try again, and don\'t continue until you get the correct output')
        return False

    if genre != 'Action':
        print('The "get_user_genre_choice" function doesn\'t return the correct genre')
        print('It should simply return the genre that you input')
        print('Please, try again, and don\'t continue until you get the correct output')
        return False
        
    if not f.getvalue():
        print('The "get_user_genre_choice" function doesn\'t print anything')
        print('You have to print all the unique genres')
        print('Please, try again, and don\'t continue until you get the correct output')
        return False

    print('Great! The "get_user_genre_choice" function prints the correct genre')
    print('You can continue to the next task')
    return True

def check_get_movies_in_genre(first_movie, second_movie, third_movie, task_1):
    if not task_1:
        print('Please, complete the previous task before continuing')
        return False

    wrong = False
    # The function should return a list of movies in a given genre
    if first_movie != 'Gladiator':
        print('The first option is incorrect')
        wrong = True
    if second_movie != 'Parasite':
        print('The second option is incorrect')
        wrong = True
    if third_movie != 'No Country for Old Men':
        print('The third option is incorrect')
        wrong = True

    if wrong:
        print('Remember that you need to increase the index by 1 each time you print a movie')
        print('Please, try again, and don\'t continue until you get the correct output')
        return False

    print('Great! The "get_movies_in_genre" function returns the correct movies')
    print('You can continue to the next task')
    return True

@timeout_decorator.timeout(5, timeout_exception=TimeoutError)
def check_get_movie_by_index(func, task_2):
    if not task_2:
        print('Please, complete the previous task before continuing')
        return False
    
    # The function should ask for an input twice
    # One for asking the genre, and another for asking the ID

    try:
        f = StringIO()
        with redirect_stdout(f):
            with patch('builtins.input', side_effect=['Action', '4']):
                movie = func()
    except TimeoutError:
        print('The "get_movie_by_index" function takes too long to run')
        print('Make sure you use the "input" function TWICE to ask for the genre and the index')
        print('Please, try again, and don\'t continue until you get the correct output')
        return False

    except:
        print('The "get_movie_by_index" function is not defined correctly')
        print('Make sure you call the "get_unique_genres" and "get_unique_genres" functions inside the "get_movie_by_index" function')
        print('Make sure you can run it without any errors, and that the function doesn\'t take any arguments')
        print('Please, try again, and don\'t continue until you get the correct output')
        return False

    if movie:
        print('The "get_movie_by_index" should not return anything, but just print the movie')
        print('Please, try again, and don\'t continue until you get the correct output')
        return False

    output = f.getvalue()
    if 'description' not in output:
        print('The "get_movie_by_index" function doesn\'t print the key "description"')
        print('Once you get the movie, you should print each key and its value')
        print('Please, try again, and don\'t continue until you get the correct output')
        return False
    
    if 'Inception' not in output:
        print('The "get_movie_by_index" function doesn\'t print the correct movie')
        print('The marking system was entering Action and 4, and the correct movie is "Inception"')
        print('Please, try again, and don\'t continue until you get the correct output')
        return False

    print('Great! The "get_movie_by_index" function is defined correctly')
    print('You have completed the fourth milestone of the project! Congratulations!')
