import unittest
from app.game.engine import GameEngine
from app.game.tiles import CITY, MEADOW, ROAD

class TestScoring(unittest.TestCase):
    def setUp(self):
        self.engine = GameEngine(1)
        self.engine.add_player(1)
        self.engine.board = {}
        # Start with a single-sided city tile at (0,0) facing East (Side 0)
        self.engine.board[(0, 0)] = {
            'id': 'city_one_side',
            'sides': [CITY, MEADOW, MEADOW, MEADOW, MEADOW, MEADOW],
            'center': MEADOW
        }
        self.engine.state = 'PLACING_TILE'

    def test_city_completion_scoring(self):
        # 1. Player 1's turn to place a tile.
        # Place another city_one_side at (1,0) facing West (Side 3) to close the city.
        # First, set current tile
        self.engine.current_tile = {
            'id': 'city_one_side',
            'sides': [MEADOW, MEADOW, MEADOW, CITY, MEADOW, MEADOW], # Side 3 is CITY
            'center': MEADOW
        }
        success, msg = self.engine.place_tile(1, 1, 0)
        self.assertTrue(success)

        # 2. Place a meeple on the city side (Side 3 of new tile)
        success, msg = self.engine.place_meeple(1, 3)
        self.assertTrue(success)

        # 3. Check if points were awarded.
        # Feature consists of (0,0,0) and (1,0,3).
        # Feature is complete. Points: 2 tiles * 2 = 4 points.
        self.assertEqual(self.engine.scores[1], 4)
        # Meeple should be returned
        self.assertEqual(len(self.engine.meeples), 0)

if __name__ == '__main__':
    unittest.main()
