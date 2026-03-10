import random
from .tiles import get_deck

class GameEngine:
    def __init__(self, room_id):
        self.room_id = room_id
        self.board = {} # {(q, r): tile_data}
        self.players = [] # list of user_ids
        self.current_player_index = 0
        self.deck = get_deck()
        self.meeple_placement = [] # list of (q, r, side, user_id)
        self.current_tile = None

        # Initial tile at (0, 0)
        if self.deck:
            self.board[(0, 0)] = self.deck.pop()

        self.next_turn()

    def add_player(self, user_id):
        if user_id not in self.players:
            self.players.append(user_id)
            return True
        return False

    def next_turn(self):
        if self.deck:
            self.current_tile = self.deck.pop()
            if self.players:
                self.current_player_index = (self.current_player_index + 1) % len(self.players)
            return True
        self.current_tile = None
        return False

    def rotate_current_tile(self):
        if self.current_tile:
            sides = self.current_tile['sides']
            new_sides = [sides[5]] + sides[0:5]
            self.current_tile['sides'] = new_sides
            if 'rotation' not in self.current_tile:
                self.current_tile['rotation'] = 0
            self.current_tile['rotation'] = (self.current_tile['rotation'] + 1) % 6
            return True
        return False

    def get_neighbors(self, q, r):
        return [
            (q, r-1, 0, 3), (q+1, r-1, 1, 4), (q+1, r, 2, 5),
            (q, r+1, 3, 0), (q-1, r+1, 4, 1), (q-1, r, 5, 2)
        ]

    def is_valid_placement(self, q, r, tile):
        if (q, r) in self.board: return False
        has_neighbor = False
        for nq, nr, my_side, target_side in self.get_neighbors(q, r):
            if (nq, nr) in self.board:
                has_neighbor = True
                if tile['sides'][my_side] != self.board[(nq, nr)]['sides'][target_side]:
                    return False
        return has_neighbor

    def place_tile(self, user_id, q, r):
        if not self.players or self.players[self.current_player_index] != user_id:
            return False, "Not your turn"

        if self.is_valid_placement(q, r, self.current_tile):
            self.board[(q, r)] = self.current_tile
            self.next_turn()
            return True, "Success"
        return False, "Invalid placement"

    def to_dict(self):
        return {
            'board': {f"{q},{r}": v for (q, r), v in self.board.items()},
            'current_player_index': self.current_player_index,
            'players': self.players,
            'current_tile': self.current_tile,
            'deck_size': len(self.deck)
        }

    @classmethod
    def from_dict(cls, data):
        engine = cls(data.get('room_id', 0))
        board_data = data.get('board', {})
        engine.board = {}
        for k, v in board_data.items():
            q, r = map(int, k.split(','))
            engine.board[(q, r)] = v
        engine.players = data.get('players', [])
        engine.current_player_index = data.get('current_player_index', 0)
        engine.current_tile = data.get('current_tile')
        engine.deck_size_saved = data.get('deck_size', 0)
        return engine
