import unittest
import os

class CompVisTestCase(unittest.TestCase):
    
    def test_camera_rps_presence(self):
        camera_game_script = 'camera_rps.py'
        self.assertIn(camera_game_script, os.listdir('.'), 'There is no camera_rps.py file in your project folder. If it is there, make sure it is named correctly, and that it is in the main folder')

if __name__ == '__main__':

    unittest.main(verbosity=2)
    