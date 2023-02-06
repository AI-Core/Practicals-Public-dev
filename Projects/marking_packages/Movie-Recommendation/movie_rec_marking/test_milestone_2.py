from io import StringIO
from unittest.mock import patch
import json
import urllib.request

urllib.request.urlretrieve("https://aicore-files.s3.amazonaws.com/Movie-Recommendation/movies-head.json", "movies-head.json")

with open('movies-head.json') as f:
    movies = json.load(f)

def get_avg_movie_description_length():
    total_len = 0
    for movie in movies:
        total_len += len(movie["description"])
    avg_description_len = total_len / len(movies)
    avg_description_len = round(avg_description_len, 1)
    return avg_description_len


def get_max_movie_name_length():
    title_of_movie_with_longest_title = None
    length_of_longest_movie_title = 0
    for movie in movies:
        title = movie["title"]
        if len(title) > length_of_longest_movie_title:
            length_of_longest_movie_title = len(title)
            title_of_movie_with_longest_title = title
    return length_of_longest_movie_title, title_of_movie_with_longest_title

def check_print_every_movie_title(func):
    # Check that the function prints every movie name
    with patch('sys.stdout', new=StringIO()) as fake_out:
        func()
        output = fake_out.getvalue()
    
    if not output:
        print("The function doesn't print anything")
        print('Please, try again, and don\'t continue until you get the correct output')
        return False

    movie_list = ['The Shawshank Redemption',
                  'The Godfather',
                  'The Dark Knight',
                  'The Godfather: Part II',
                  '12 Angry Men']
    for movie in movie_list:
        if movie not in output:
            print("The function doesn't print every movie name. For example, it doesn't print the name of the movie: ", movie)
            print('Please, try again, and don\'t continue until you get the correct output')
            return False
    print('Great! The function prints every movie name')
    print('You can continue to the next task')
    return True

def check_get_movie_description_length(func, task_1):
    # Check that the function returns the correct length of the description\
    if not task_1:
        print("You haven't completed the previous task correctly")
        return False
    movie = movies[1]
    try:
        actual = func(movie)
    except Exception as e:
        print("Running the function with a movie as an argument results in an error")
        print('Check the error here: ', e)
        print('Please, try again, and don\'t continue until you get the correct output')
        return False
    if not actual:
        print("The function doesn't return anything")
        print('Please, try again, and don\'t continue until you get the correct output')
        return False
    elif not isinstance(actual, int):
        print("The function doesn't return an integer")
        print('Please, try again, and don\'t continue until you get the correct output')
        return False
    expected = len(movie['description'])
    if actual != expected:
        print("The function doesn't return the correct length of the description")
        print('Please, try again, and don\'t continue until you get the correct output')
        return False
    else:
        print('Great! The function returns the correct length of the description: ', actual)
        print('You can continue to the next task')
        return True

def check_get_avg_movie_description_length(func, task_2):
    if not task_2:
        print("You haven't completed the previous task correctly")
        return False
    try:
        actual = func()
    except Exception as e:
        print('Running the "get_avg_movie_description_length" function results in an error')
        print('Check the error here: ', e)
        print('Please, try again, and don\'t continue until you get the correct output')
        return False
    if not actual:
        print("The function doesn't return anything")
        print('Please, try again, and don\'t continue until you get the correct output')
        return False
    elif not isinstance(actual, float):
        print("The function doesn't return a float, which results from dividing two integers")
        print('Please, try again, and don\'t continue until you get the correct output')
        return False
    expected = get_avg_movie_description_length()
    if actual - expected > 1:
        print('The "get_avg_movie_description_length" function doesn\'t return the correct average length of the description')
        print('Please, try again, and don\'t continue until you get the correct output')
        return False
    else:
        print('Great! The "get_avg_movie_description_length" function returns the correct average length of the description')
        print('You can continue to the next task')
        return True


def check_get_max_movie_name_length(func, task_3):
    if not task_3:
        print("You haven't completed the previous task correctly")
        return False
    try:
        actual = func()
    except Exception as e:
        print('Running the "get_max_movie_name_length" function results in an error')
        print('Check the error here: ', e)
        print('Please, try again, and don\'t continue until you get the correct output')
        return False
    if not actual:
        print("The function doesn't return anything")
        print('Please, try again, and don\'t continue until you get the correct output')
        return False
    elif len(actual) != 2:
        print("The function doesn't return two elements")
        print('Please, try again, and don\'t continue until you get the correct output')
        return False
    elif not isinstance(actual[0], int):
        print("The first returned element is not an integer")
        print('Please, try again, and don\'t continue until you get the correct output')
        return False
    elif not isinstance(actual[1], str):
        print("The second returned element is not a string")
        print('Please, try again, and don\'t continue until you get the correct output')
        return False
    expected = get_max_movie_name_length()
    if actual[0] != expected[0]:
        print('The "get_max_movie_name_length" function doesn\'t return the correct maximum length of the movie name')
        print('Please, try again, and don\'t continue until you get the correct output')
        return False
    elif actual[1] != expected[1]:
        print('The "get_max_movie_name_length" function doesn\'t return the correct movie name')
        print('Please, try again, and don\'t continue until you get the correct output')
        return False
    else:
        print('Great! The "get_max_movie_name_length" function returns the correct maximum length of the movie name: ', actual)
        print('Nice job! You have complete the second milestone of the project!')
