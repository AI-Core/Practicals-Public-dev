import unittest
import os

class CompVisTestCase(unittest.TestCase):
    
    def test_model_presence(self):
        model_path = 'keras_model.h5'
        self.assertIn(model_path, os.listdir('.'), 'There is no keras_model.h5 file in your project folder')
    
    def test_presence_readme(self):
        self.assertIn('README.md', os.listdir('.'), 'You should have a README.md file in your project folder')
        with open('README.md', 'r') as f:
            readme = f.read()
        self.assertGreater(len(readme), 500, 'The README.md file should be at least 500 characters long')


if __name__ == '__main__':

    unittest.main(verbosity=2)
    