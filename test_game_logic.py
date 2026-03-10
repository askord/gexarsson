import unittest
from app.game.engine import GameEngine
from app.game.tiles import CITY, MEADOW, ROAD

class TestGameEngine(unittest.TestCase):
    def setUp(self):
        self.engine = GameEngine(1)
        self.engine.players = [1, 2] # user_ids
        self.engine.current_player_index = 0

        # Clear board for test
        self.engine.board = {}
        # Manually set board (0,0)
        self.engine.board[(0, 0)] = {
            'id': 'city_all',
            'sides': [CITY, CITY, CITY, CITY, CITY, CITY],
            'center': CITY
        }
        # Force current tile to be predictable
        self.engine.current_tile = {
            'id': 'city_all',
            'sides': [CITY, CITY, CITY, CITY, CITY, CITY],
            'center': CITY
        }

    def test_valid_placement(self):
        success, msg = self.engine.place_tile(1, 0, 1)
        self.assertTrue(success)
        self.assertIn((0, 1), self.engine.board)

    def test_turn_authority(self):
        # User 2 tries to place but it's user 1's turn
        success, msg = self.engine.place_tile(2, 0, 1)
        self.assertFalse(success)
        self.assertEqual(msg, "Not your turn")

    def test_tile_rotation(self):
        self.engine.current_tile = {
            'id': 'city_one_side',
            'sides': [CITY, MEADOW, MEADOW, MEADOW, MEADOW, MEADOW],
            'center': MEADOW
        }
        self.engine.rotate_current_tile()
        self.assertEqual(self.engine.current_tile['sides'], [MEADOW, CITY, MEADOW, MEADOW, MEADOW, MEADOW])

if __name__ == '__main__':
    unittest.main()
