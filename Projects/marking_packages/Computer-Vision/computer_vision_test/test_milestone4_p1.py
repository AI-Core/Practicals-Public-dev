import unittest
import os


class CompVisTestCase(unittest.TestCase):
    
    def test_manual_rps_presence(self):
        manual_game_script = 'manual_rps.py'
        self.assertIn(manual_game_script, os.listdir('.'), 'There is no manual_rps.py file in your project folder. If it is there, make sure it is named correctly, and that it is in the main folder')


if __name__ == '__main__':

    unittest.main(verbosity=2)
    