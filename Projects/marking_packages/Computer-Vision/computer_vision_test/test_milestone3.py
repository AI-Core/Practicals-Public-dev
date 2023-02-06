import unittest
import os


class CompVisTestCase(unittest.TestCase):
    
    def test_requirements_presence(self):
        model_path = 'requirements.txt'
        self.assertIn(model_path, os.listdir('.'), 'There is no requirements.txt file in your project folder')
        with open('requirements.txt') as f:
            requirements = f.read().splitlines()
        with open('requirements.txt') as f:
            requirements_str = f.read()
        second_line = requirements[1]
        self.assertIn('---', second_line, 'The second line of the requirements.txt file should be a line of dashes. If it is not, that means that you did not generate it using "pip list > requirements.txt"')
        libraries = [r.split()[0] for r in requirements[2:]]
        self.assertIn('ipykernel', libraries, 'You should have ipykernel in your requirements.txt file. This will allow you to run python notebooks')
        self.assertIn('ipython', libraries, 'You should have ipython in your requirements.txt file. If not, you will not be able to run python notebooks. To install it run: pip install ipykernel')
        self.assertIn('tensorflow', requirements_str, 'You should have tensorflow in your requirements.txt file. If not, you will not be able to run python notebooks. To install it run: pip install tensorflow')
        self.assertGreater(len(requirements), 10, 'You should have at least 10 lines in your requirements.txt file. If you don\'t, make sure that you have tensorflow, opencv, and ipykernel installed. Once installed, you have to run "pip list > requirements.txt" to update the requirements.txt file')

if __name__ == '__main__':

    unittest.main(verbosity=2)
    