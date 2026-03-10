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
            self.board[(0, 0)] = self.deck.pop(0)

        self.next_turn()

    def add_player(self, user_id):
        if user_id not in self.players:
            self.players.append(user_id)
            return True
        return False

    def next_turn(self):
        if self.deck:
            self.current_tile = self.deck.pop(0)
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
        # Pointy-topped hex axial neighbor offsets
        # Sides: 0=East (+1, 0), 1=South-East (0, +1), 2=South-West (-1, +1),
        #        3=West (-1, 0), 4=North-West (0, -1), 5=North-East (+1, -1)
        # my_side matches neighbor's target_side (target = (my_side + 3) % 6)
        return [
            (q+1, r, 0, 3),   # Side 0 (East)
            (q, r+1, 1, 4),   # Side 1 (South-East)
            (q-1, r+1, 2, 5), # Side 2 (South-West)
            (q-1, r, 3, 0),   # Side 3 (West)
            (q, r-1, 4, 1),   # Side 4 (North-West)
            (q+1, r-1, 5, 2)  # Side 5 (North-East)
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
            return False, "Не ваш ход"

        if self.is_valid_placement(q, r, self.current_tile):
            self.board[(q, r)] = self.current_tile
            self.next_turn()
            return True, "Успех"
        return False, "Недопустимое размещение"

    def to_dict(self):
        return {
            'room_id': self.room_id,
            'board': {f"{q},{r}": v for (q, r), v in self.board.items()},
            'current_player_index': self.current_player_index,
            'players': self.players,
            'current_tile': self.current_tile,
            'deck': self.deck
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
        engine.deck = data.get('deck', [])
        return engine
