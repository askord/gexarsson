import unittest
from app.game.engine import GameEngine
from app.game.tiles import CITY, MEADOW, ROAD

class TestMeepleBugs(unittest.TestCase):
    def setUp(self):
        self.engine = GameEngine(1)
        self.engine.add_player("1")
        self.engine.board = {}
        self.engine.board[(0, 0)] = {
            'id': 'city_one_side',
            'sides': [CITY, MEADOW, MEADOW, MEADOW, MEADOW, MEADOW],
            'center': MEADOW,
            'connections': [[0]]
        }
        self.engine.state = 'PLACING_TILE'

    def test_no_double_meeple_on_connected_feature(self):
        self.engine.meeples.append({'q': 0, 'r': 0, 'side': 0, 'user_id': "1", 'type': CITY})
        self.engine.current_tile = {
            'id': 'city_one_side',
            'sides': [MEADOW, MEADOW, MEADOW, CITY, MEADOW, MEADOW],
            'center': MEADOW,
            'connections': [[3]]
        }
        self.engine.place_tile("1", 1, 0)
        success, msg = self.engine.place_meeple("1", 3)
        self.assertFalse(success)
        self.assertEqual(msg, "Эта область уже занята")

    def test_skip_meeple_preserves_existing(self):
        self.engine.meeples.append({'q': 0, 'r': 0, 'side': 0, 'user_id': "1", 'type': CITY})
        self.engine.current_tile = {
            'id': 'road_straight',
            'sides': [MEADOW, MEADOW, ROAD, MEADOW, MEADOW, ROAD],
            'center': ROAD,
            'connections': [[2, 5, 6]]
        }
        self.engine.place_tile("1", 0, 1)
        self.engine.skip_meeple("1")
        self.assertEqual(len(self.engine.meeples), 1)
        self.assertEqual(self.engine.meeples[0]['q'], 0)

if __name__ == '__main__':
    unittest.main()
