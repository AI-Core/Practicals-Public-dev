import json
import urllib.request

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

def check_load_movies_data(func):
    try:
        movies_in = func()
    except:
        print('The "load_movies_data" function is not defined correctly')
        print('Make sure you can run it without any errors, and that the function doesn\'t take any arguments')
        print('Please, try again, and don\'t continue until you get the correct output')
        return False

    if not movies_in:
        print('The "load_movies_data" doesn\'t return anything')
        print('Make sure it uses the "return" keyword to return the movies list')
        print('Please, try again, and don\'t continue until you get the correct output')
        return False

    if not isinstance(movies_in, list):
        print('The "load_movies_data" function doesn\'t return a list')
        print('Please, try again, and don\'t continue until you get the correct output')
        return False

    if len(movies_in) != n_movies:
        print('The "load_movies_data" function doesn\'t return the correct number of movies')
        print('Please, try again, and don\'t continue until you get the correct output')
        return False

    else:
        print('Great! The "load_movies_data" function returns the correct number of movies')
        print('You can continue to the next task')
        return True

def check_get_unique_genres(func, task_1):
    if not task_1:
        print('Please, complete the previous task before continuing')
        return False
    # The function should return a set of unique genres
    try:
        genres = func()
    except:
        print('The "get_unique_genres" function is not defined correctly')
        print('Make sure you can run it without any errors, and that the function doesn\'t take any arguments')
        print('Please, try again, and don\'t continue until you get the correct output')
        return False

    if not genres:
        print('The "get_unique_genres" doesn\'t return anything')
        print('Make sure it uses the "return" keyword to return the genres set')
        print('Please, try again, and don\'t continue until you get the correct output')
        return False

    if not isinstance(genres, set):
        print('The "get_unique_genres" function doesn\'t return a set')
        print('Please, try again, and don\'t continue until you get the correct output')
        return False

    if len(genres) != n_unique_genres:
        print('The "get_unique_genres" function doesn\'t return the correct number of genres')
        print(f'There should be {n_unique_genres} unique genres, but your function returns {len(genres)}')
        print('Please, try again, and don\'t continue until you get the correct output')
        return False

    else:
        print('Great! The "get_unique_genres" function returns the correct genres')
        print('You can continue to the next task')
        return True

def check_get_movies_in_genre(func, task_2):
    if not task_2:
        print('Please, complete the previous task before continuing')
        return False
    # The function should return a list of movies in a given genre
    try:
        movies_in = func("Action")
    except:
        print('The "get_movies_in_genre" function is not defined correctly')
        print('Make sure you can run it without any errors, and that the function takes one argument: the genre that you look for')
        print('Please, try again, and don\'t continue until you get the correct output')
        return False

    if not movies_in:
        print('The "get_movies_in_genre" doesn\'t return anything')
        print('Make sure it uses the "return" keyword to return the movies list')
        print('Please, try again, and don\'t continue until you get the correct output')
        return False

    if not isinstance(movies_in, list):
        print('The "get_movies_in_genre" function doesn\'t return a list')
        print('Please, try again, and don\'t continue until you get the correct output')
        return False


    for genre in genres:
        movies_in = func(genre)
        movies_genre = get_movies_in_genre(genre)
        if len(movies_in) != len(movies_genre):
            print('The "get_movies_in_genre" function doesn\'t return the correct number of movies')
            print(f'There should be {len(movies_genre)} movies in the "{genre}" genre, but your function returns {len(movies_in)}')
            print('Please, try again, and don\'t continue until you get the correct output')
            return False

    else:
        print('Great! The "get_movies_in_genre" function returns the correct number of movies')
        print('Amazing! You have complete the third milestone of the project! Two more to go!')
