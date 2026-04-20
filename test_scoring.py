import unittest
from app.game.engine import GameEngine
from app.game.tiles import CITY, MEADOW, ROAD

class TestScoring(unittest.TestCase):
    def setUp(self):
        self.engine = GameEngine(1)
        self.engine.add_player("1", "player1")
        self.engine.board = {}
        # Start with a single-sided city tile at (0,0) facing East (Side 0)
        self.engine.board[(0, 0)] = {
            'id': 'city_one_side',
            'sides': [CITY, MEADOW, MEADOW, MEADOW, MEADOW, MEADOW],
            'center': MEADOW,
            'connections': [[0]]
        }
        self.engine.state = 'PLACING_TILE'

    def test_city_completion_scoring(self):
        self.engine.current_tile = {
            'id': 'city_one_side',
            'sides': [MEADOW, MEADOW, MEADOW, CITY, MEADOW, MEADOW], # Side 3 is CITY
            'center': MEADOW,
            'connections': [[3]]
        }
        success, msg = self.engine.place_tile("1", 1, 0)
        self.assertTrue(success)

        success, msg = self.engine.place_meeple("1", 3)
        self.assertTrue(success)

        self.assertEqual(self.engine.scores["1"], 4)
        self.assertEqual(len(self.engine.meeples), 0)

if __name__ == '__main__':
    unittest.main()
