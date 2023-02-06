def check_length(selected_option):
    # Check that the length of the movie list is correct
    if selected_option != 5:
        print("The length of the movie list is incorrect, remember that the list of movies is in the variable called 'movies'")
        print('Please, try again, and don\'t continue until you get the correct length')
        return False
    else:
        print('Great! The length of the movie list is correct - 5')
        print('You can continue to the next task')
        return True

def check_first_movie(selected_option_movie, selected_option_dtype, task_1):
    if not task_1:
        print("You haven't completed the previous task correctly")
        return False
    if selected_option_movie != 'The Shawshank Redemption':
        print("The selected movie is incorrect. Remember that you can access the first movie in the list indexing the list with the number 0")
        print('Please, try again, and don\'t continue until you get the correct first movie')
        return False
    elif selected_option_dtype != 'dict':
        print("The selected movie is not a dictionary. Remember that you can check the type of a variable using the type() function")
        print('Please, try again, and don\'t continue until you get the correct first movie')
        return False
    else:
        print('Great! The first movie in the list is correct - The Shawshank Redemption')
        print('You can continue to the next task')
        return True

def check_last_characters(selected_option, task_2):
    if not task_2:
        print("You haven't completed the previous tasks correctly")
        return False
    if selected_option != 'chttp_tt_1':
        print("The last 10 characters in the url are incorrect. Remember that you can index a dictionary with the key to get the value")
        print('Please, try again, and don\'t continue until you get the correct last characters')
        return False
    else:
        print('Great! The last 10 characters in the url are correct - chtt_tt_1')
        print('Great! You have completed the first milestone of the project')