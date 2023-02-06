import unittest
import os
import ast
import timeout_decorator
from unittest.mock import patch
import io
from contextlib import redirect_stdout

def check_play_body(node):
    for subnode in node.body:
        if subnode.name == 'play':
            return subnode
    return None


class CompVisTestCase(unittest.TestCase):
    def setUp(self) -> None:
        path = 'manual_rps.py'
        try:
            with open(path, 'r') as f:
                self.code = f.read()
        except:
            self.fail(' : You should have a file named manual_rps.py in your repository. If you created it, make sure it is in the root directory of your repository')

        self.node_functions = ast.parse(self.code)
        self.node_imports = ast.parse(self.code)
        
        # Execute the class definition
        # Create an instance for the class
        self.node_functions.body = [cs for cs in self.node_functions.body if isinstance(cs, ast.FunctionDef)]
        # Create an instance to import any possible module used by the user
        self.function_names = [name.name for name in self.node_functions.body]
        self.assertGreaterEqual(len(self.function_names), 2, 'You should define at least two functions in your manual_rps.py file: `get_computer_choice` and `get_user_choice`.')

        self.assertIn('get_computer_choice', self.function_names, 'You should have a function named `get_computer_choice` in your manual_rps.py file')
        self.assertIn('get_user_choice', self.function_names, 'You should have a function named `get_user_choice` in your manual_rps.py file')

        # Run the function definitions

        eval(compile(self.node_functions, '', 'exec'), globals())

        # Create an instance to import any possible module used by the user
        imports = [imp for imp in self.node_imports.body if isinstance(imp, ast.Import)]
        for imp in imports:
            try:
                eval(compile(f'import {imp.names[0].name}', '', 'exec'), globals())
            except:
                error_msg = f' : You have imported a module that is not available ({imp.names[0].name}) in the system. For manual_rps.py, you should only import the `random` module.'
                self.fail(error_msg)

    @timeout_decorator.timeout(10, timeout_exception=TimeoutError)
    def test_get_computer_choice_user_choice(self):
        try:
            computer_choice = get_computer_choice()
            self.assertIn(computer_choice, ['Rock', 'Paper', 'Scissors', 'rock', 'paper', 'scissors'], 'The function `get_computer_choice` should `return` a string with the value `Rock`, `Paper` or `Scissors`.')
        except TimeoutError:
            self.fail(' : Something went wrong when running the function `get_computer_choice`. Make sure you have defined the function correctly in the manual_rps.py file and that it does not have any infinite loop.')
        except:
            self.fail(' : Something went wrong when running the function `get_computer_choice`. Make sure you have defined the function correctly in the manual_rps.py file and that it does not accept any parameter. Also, make sure that the list of options is defined inside the function.')

        try:
            with patch('builtins.input', return_value='Rock'):
                user_choice = get_user_choice()
            self.assertIn(user_choice, ['Rock', 'rock'], 'The function `get_user_choice` should ask the user for an input and then `return` that input.')
        except TimeoutError:
            self.fail(' : Something went wrong when running the function `get_user_choice`. Make sure you have defined the function correctly in the manual_rps.py file and that it does not have any infinite loop.')
        except:
            self.fail(' : Something went wrong when running the function `get_user_choice`. Make sure you have defined the function correctly in the manual_rps.py file and that it does not accept any parameter.')

    @timeout_decorator.timeout(10, timeout_exception=TimeoutError)
    def test_get_winner(self):
        self.assertIn('get_winner', self.function_names, 'You should have a function named `get_winner` in your manual_rps.py file')
        try:
            try:
                f = io.StringIO()
                with redirect_stdout(f):
                    get_winner('Rock', 'Rock')
                    message = f.getvalue()
                first_line = message.split('\n')[0]
                self.assertEqual(first_line, 'It is a tie!', 'The function `get_winner` should print `It is a tie!` if the user and the computer have the same choice. Also, the choices you used in the if-elif-else statement should be `Rock`, `Paper` and `Scissors`')
            except AssertionError:
                f = io.StringIO()
                with redirect_stdout(f):
                    get_winner('rock', 'rock')
                    message = f.getvalue()
                first_line = message.split('\n')[0]
                self.assertEqual(first_line, 'It is a tie!', 'The function `get_winner` should print `It is a tie!` if the user and the computer have the same choice. Also, the choices you used in the if-elif-else statement should be `Rock`, `Paper` and `Scissors`')
            try:
                f = io.StringIO()
                with redirect_stdout(f):
                    get_winner('Paper', 'Rock')
                    message = f.getvalue()
                first_line = message.split('\n')[0]
                self.assertEqual(first_line, 'You lost', 'The function `get_winner` should print `You lost` if the computer wins the game. If you think you did everything correctly, make sure that the first argument of your `get_winner` function is `computer_choice` and the second argument is `user_choice`. Also, the choices you used in the if-elif-else statement should be `Rock`, `Paper` and `Scissors`')
            except AssertionError:
                f = io.StringIO()
                with redirect_stdout(f):
                    get_winner('paper', 'rock')
                    message = f.getvalue()
                first_line = message.split('\n')[0]
                self.assertEqual(first_line, 'You lost', 'The function `get_winner` should print `You lost` if the computer wins the game. If you think you did everything correctly, make sure that the first argument of your `get_winner` function is the output of `computer_choice` and the second argument is the output of `user_choice`. Also, the choices you used in the if-elif-else statement should be `Rock`, `Paper` and `Scissors`. ')
            try:
                f = io.StringIO()
                with redirect_stdout(f):
                    get_winner('Paper', 'Scissors')
                    message = f.getvalue()
                first_line = message.split('\n')[0]
                self.assertEqual(first_line, 'You won!', 'The function `get_winner` should print `You won!` if you win the game. If you think you did everything correctly, make sure that the first argument of your `get_winner` function is `computer_choice` and the second argument is `user_choice`. Also, the choices you used in the if-elif-else statement should be `Rock`, `Paper` and `Scissors`')
            except AssertionError:
                f = io.StringIO()
                with redirect_stdout(f):
                    get_winner('paper', 'scissors')
                    message = f.getvalue()
                first_line = message.split('\n')[0]
                self.assertEqual(first_line, 'You won!', 'The function `get_winner` should print `You won!` if you win the game. If you think you did everything correctly, make sure that the first argument of your `get_winner` function is the output of `computer_choice` and the second argument is the output of `user_choice`. Also, the choices you used in the if-elif-else statement should be `Rock`, `Paper` and `Scissors`')
        except TimeoutError:
            self.fail(' : Something went wrong when running the function `get_winner`. Make sure you have defined the function correctly in the manual_rps.py file and that it does not have any infinite loop.')
        except:
            self.fail(' : Something went wrong when running the function `get_winner`. Make sure you have defined the function correctly in the manual_rps.py file and that it accepts two parameters: `computer_choice` and `user_choice` in that order. Also, the choices you used in the if-elif-else statement should be `Rock`, `Paper` and `Scissors`.')

    def test_play_game(self):
        self.assertIn('play', self.function_names, 'You should have a function named `play` in your manual_rps.py file. It doesn\'t need to accept any parameter.')
        
        play_subnode = check_play_body(self.node_functions)
        self.assertIsNotNone(play_subnode, 'You should have a function named `play` in your manual_rps.py file. It doesn\'t need to accept any parameter.')
        play_body = ast.dump(play_subnode)
        self.assertIn('get_computer_choice', play_body, 'You should call the function `get_computer_choice` inside the function `play`.')
        self.assertIn('get_user_choice', play_body, 'You should call the function `get_user_choice` inside the function `play`.')
        self.assertIn('get_winner', play_body, 'You should call the function `get_winner` inside the function `play`.')

    def test_presence_readme(self):
        self.assertIn('README.md', os.listdir('.'), 'You should have a README.md file in your project folder')
        with open('README.md', 'r') as f:
            readme = f.read()
        self.assertGreater(len(readme), 1500, 'The README.md file should be at least 1500 characters long')

def check_play_body(node):
    for subnode in node.body:
        if subnode.name == 'play':
            return subnode
    return None


if __name__ == '__main__':

    unittest.main(verbosity=2)
    