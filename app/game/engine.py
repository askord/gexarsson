import random
from .tiles import get_deck, CITY, ROAD, MONASTERY, MEADOW

class GameEngine:
    def __init__(self, room_id):
        self.room_id = room_id
        self.board = {} # {(q, r): tile_data}
        self.players = [] # list of user_ids
        self.scores = {} # {user_id: score}
        self.current_player_index = 0
        self.deck = get_deck()
        self.meeples = [] # list of {'q': q, 'r': r, 'side': side, 'user_id': user_id, 'type': type}
        self.current_tile = None
        self.last_placed_pos = None # (q, r)
        self.state = 'PLACING_TILE' # 'PLACING_TILE', 'PLACING_MEEPLE'

        # Initial tile at (0, 0)
        if self.deck:
            self.board[(0, 0)] = self.deck.pop(0)

        self.next_turn()

    def add_player(self, user_id):
        if user_id not in self.players:
            self.players.append(user_id)
            self.scores[user_id] = 0
            return True
        return False

    def next_turn(self):
        if self.deck:
            self.current_tile = self.deck.pop(0)
            if self.players:
                self.current_player_index = (self.current_player_index + 1) % len(self.players)
            self.state = 'PLACING_TILE'
            self.last_placed_pos = None
            return True
        self.current_tile = None
        return False

    def rotate_current_tile(self):
        if self.state == 'PLACING_TILE' and self.current_tile:
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
        if self.state != 'PLACING_TILE':
            return False, "Сейчас нельзя ставить плитку"
        if not self.players or self.players[self.current_player_index] != user_id:
            return False, "Не ваш ход"

        if self.is_valid_placement(q, r, self.current_tile):
            self.board[(q, r)] = self.current_tile
            self.last_placed_pos = (q, r)
            self.state = 'PLACING_MEEPLE'
            return True, "Успех"
        return False, "Недопустимое размещение"

    def skip_meeple(self, user_id):
        if self.state != 'PLACING_MEEPLE':
            return False, "Сейчас нельзя пропустить мипла"
        if self.players[self.current_player_index] != user_id:
            return False, "Не ваш ход"

        self.score_completed_features()
        self.next_turn()
        return True, "Успех"

    def place_meeple(self, user_id, side):
        if self.state != 'PLACING_MEEPLE':
            return False, "Сейчас нельзя ставить мипла"
        if self.players[self.current_player_index] != user_id:
            return False, "Не ваш ход"

        q, r = self.last_placed_pos
        tile = self.board[(q, r)]

        # Basic check: side must have a feature
        feature_type = tile['sides'][side] if side < 6 else tile['center']
        if feature_type == MEADOW:
            return False, "Нельзя ставить мипла на луг в этой версии"

        # Check if feature is already occupied
        feature = self.get_feature(q, r, side)
        for m in self.meeples:
            if (m['q'], m['r'], m['side']) in feature:
                return False, "Эта область уже занята"

        self.meeples.append({
            'q': q, 'r': r, 'side': side,
            'user_id': user_id,
            'type': feature_type
        })

        self.score_completed_features()
        self.next_turn()
        return True, "Успех"

    def get_feature(self, q, r, side):
        # side: 0-5 for sides, 6 for center
        tile = self.board.get((q, r))
        if not tile: return set()

        feature_type = tile['sides'][side] if side < 6 else tile['center']
        visited = set()
        stack = [(q, r, side)]

        while stack:
            curr_q, curr_r, curr_s = stack.pop()
            if (curr_q, curr_r, curr_s) in visited: continue
            visited.add((curr_q, curr_r, curr_s))

            curr_tile = self.board.get((curr_q, curr_r))
            if not curr_tile: continue

            # Internal connections
            if curr_s < 6:
                # If center matches, it connects to all same-type sides and center
                if curr_tile['center'] == feature_type:
                    stack.append((curr_q, curr_r, 6))
                    for i in range(6):
                        if curr_tile['sides'][i] == feature_type:
                            stack.append((curr_q, curr_r, i))
                # Even if center doesn't match, we might connect to adjacent sides?
                # (Simplification: only through center)
            else: # center
                for i in range(6):
                    if curr_tile['sides'][i] == feature_type:
                        stack.append((curr_q, curr_r, i))

            # External connections (only for sides)
            if curr_s < 6:
                neighbors = self.get_neighbors(curr_q, curr_r)
                nq, nr, my_s, target_s = neighbors[curr_s]
                if (nq, nr) in self.board:
                    neighbor_tile = self.board[(nq, nr)]
                    if neighbor_tile['sides'][target_s] == feature_type:
                        stack.append((nq, nr, target_s))

        return visited

    def is_feature_complete(self, feature):
        for q, r, s in feature:
            if s == 6: continue
            neighbors = self.get_neighbors(q, r)
            nq, nr, my_s, target_s = neighbors[s]
            if (nq, nr) not in self.board:
                return False
        return True

    def score_completed_features(self):
        # We only check features connected to the last placed tile
        if not self.last_placed_pos: return

        q, r = self.last_placed_pos
        tile = self.board[(q, r)]

        processed_features = []

        for side in range(7):
            feature_type = tile['sides'][side] if side < 6 else tile['center']
            if feature_type not in [CITY, ROAD]: continue

            feature = self.get_feature(q, r, side)
            if feature in processed_features: continue
            processed_features.append(feature)

            if self.is_feature_complete(feature):
                self.award_points(feature, feature_type)

    def award_points(self, feature, feature_type):
        # Find meeples on this feature
        meeple_counts = {} # {user_id: count}
        feature_meeples = []

        for m in self.meeples:
            if (m['q'], m['r'], m['side']) in feature:
                meeple_counts[m['user_id']] = meeple_counts.get(m['user_id'], 0) + 1
                feature_meeples.append(m)

        if not meeple_counts: return # No one to award

        max_meeples = max(meeple_counts.values())
        winners = [uid for uid, count in meeple_counts.items() if count == max_meeples]

        # Calculate points
        # City: 2 points per tile. Road: 1 point per tile.
        unique_tiles = set((q, r) for q, r, s in feature)
        points = len(unique_tiles) * (2 if feature_type == CITY else 1)

        for uid in winners:
            self.scores[uid] = self.scores.get(uid, 0) + points

        # Return meeples
        for m in feature_meeples:
            self.meeples.remove(m)

    def to_dict(self):
        return {
            'room_id': self.room_id,
            'board': {f"{q},{r}": v for (q, r), v in self.board.items()},
            'current_player_index': self.current_player_index,
            'players': self.players,
            'scores': self.scores,
            'current_tile': self.current_tile,
            'deck': self.deck,
            'meeples': self.meeples,
            'state': self.state,
            'last_placed_pos': self.last_placed_pos
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
        engine.scores = data.get('scores', {})
        engine.current_player_index = data.get('current_player_index', 0)
        engine.current_tile = data.get('current_tile')
        engine.deck = data.get('deck', [])
        engine.meeples = data.get('meeples', [])
        engine.state = data.get('state', 'PLACING_TILE')
        engine.last_placed_pos = data.get('last_placed_pos')
        return engine
