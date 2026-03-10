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
        # Pointy-topped neighbors for (0, 0):
        # (1, 0), (0, 1), (-1, 1), (-1, 0), (0, -1), (1, -1)
        success, msg = self.engine.place_tile(1, 1, 0) # East
        self.assertTrue(success)
        self.assertIn((1, 0), self.engine.board)

    def test_invalid_placement_non_matching(self):
        # Neighbor's side 0 is East.
        # (1, 0) is East of (0, 0).
        # My side 3 (West) must match neighbor's side 0 (East).
        self.engine.current_tile = {
            'id': 'road_straight',
            'sides': [MEADOW, MEADOW, ROAD, MEADOW, MEADOW, ROAD], # Side 3 is MEADOW
            'center': ROAD
        }
        # neighbor (0,0) Side 0 is CITY. My Side 3 is MEADOW. Fails.
        success, msg = self.engine.place_tile(1, 1, 0)
        self.assertFalse(success)
        self.assertEqual(msg, "Недопустимое размещение")

    def test_turn_authority(self):
        # User 2 tries to place but it's user 1's turn
        success, msg = self.engine.place_tile(2, 1, 0)
        self.assertFalse(success)
        self.assertEqual(msg, "Не ваш ход")

if __name__ == '__main__':
    unittest.main()
