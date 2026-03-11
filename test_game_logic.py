import unittest
from app.game.engine import GameEngine
from app.game.tiles import CITY, MEADOW, ROAD

class TestGameEngine(unittest.TestCase):
    def setUp(self):
        self.engine = GameEngine(1)
        self.engine.add_player(1)
        self.engine.add_player(2)
        self.engine.current_player_index = 0

        # Clear board for test
        self.engine.board = {}
        # Manually set board (0,0) - a city tile
        self.engine.board[(0, 0)] = {
            'id': 'city_all',
            'sides': [CITY, CITY, CITY, CITY, CITY, CITY],
            'center': CITY,
            'connections': [[0, 1, 2, 3, 4, 5, 6]]
        }
        self.engine.state = 'PLACING_TILE'
        # Force current tile to be predictable
        self.engine.current_tile = {
            'id': 'city_all',
            'sides': [CITY, CITY, CITY, CITY, CITY, CITY],
            'center': CITY,
            'connections': [[0, 1, 2, 3, 4, 5, 6]]
        }

    def test_scoring_city(self):
        # 1. Place tile (1, 0)
        success, msg = self.engine.place_tile(1, 1, 0)
        self.assertTrue(success)
        self.assertEqual(self.engine.state, 'PLACING_MEEPLE')

        # 2. Place meeple
        success, msg = self.engine.place_meeple(1, 0)
        self.assertTrue(success)
        self.assertEqual(len(self.engine.meeples), 1)

        feature = self.engine.get_feature(0, 0, 0)
        self.assertIn((0, 0, 0), feature)
        self.assertIn((1, 0, 3), feature)

    def test_turn_authority(self):
        success, msg = self.engine.place_tile(2, 1, 0)
        self.assertFalse(success)
        self.assertEqual(msg, "Не ваш ход")

if __name__ == '__main__':
    unittest.main()
