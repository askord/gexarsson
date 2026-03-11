import random
from .tiles import get_deck, CITY, ROAD, MONASTERY, MEADOW

class GameEngine:
    def __init__(self, room_id):
        self.room_id = room_id
        self.board = {} # {(q, r): tile_data}
        self.players = [] # list of user_ids (strings)
        self.scores = {} # {user_id: score}
        self.current_player_index = 0
        self.deck = get_deck()
        self.meeples = [] # list of {'q': q, 'r': r, 'side': side, 'user_id': user_id, 'type': type}
        self.current_tile = None
        self.last_placed_pos = None # (q, r)
        self.state = 'PLACING_TILE'
        self.log = []

        if self.deck:
            self.board[(0, 0)] = self.deck.pop(0)

        self.next_turn()

    def add_player(self, user_id):
        user_id = str(user_id)
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

            new_conns = []
            for group in self.current_tile['connections']:
                new_group = []
                for idx in group:
                    if idx < 6:
                        new_group.append((idx + 1) % 6)
                    else:
                        new_group.append(6)
                new_conns.append(new_group)
            self.current_tile['connections'] = new_conns

            if 'rotation' not in self.current_tile:
                self.current_tile['rotation'] = 0
            self.current_tile['rotation'] = (self.current_tile['rotation'] + 1) % 6
            return True
        return False

    def get_neighbors(self, q, r):
        return [
            (q+1, r, 0, 3), (q, r+1, 1, 4), (q-1, r+1, 2, 5),
            (q-1, r, 3, 0), (q, r-1, 4, 1), (q+1, r-1, 5, 2)
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

    def get_valid_placements(self):
        if not self.current_tile: return []
        valid = []
        candidates = set()
        for (q, r) in self.board:
            for nq, nr, _, _ in self.get_neighbors(q, r):
                if (nq, nr) not in self.board:
                    candidates.add((nq, nr))
        for q, r in candidates:
            if self.is_valid_placement(q, r, self.current_tile):
                valid.append({'q': q, 'r': r})
        return valid

    def place_tile(self, user_id, q, r):
        user_id = str(user_id)
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
        user_id = str(user_id)
        if self.state != 'PLACING_MEEPLE':
            return False, "Сейчас нельзя пропустить мипла"
        if self.players[self.current_player_index] != user_id:
            return False, "Не ваш ход"
        self.score_completed_features()
        self.next_turn()
        return True, "Успех"

    def place_meeple(self, user_id, side):
        user_id = str(user_id)
        if self.state != 'PLACING_MEEPLE':
            return False, "Сейчас нельзя ставить мипла"
        if self.players[self.current_player_index] != user_id:
            return False, "Не ваш ход"

        q, r = self.last_placed_pos
        tile = self.board[(q, r)]
        feature_type = tile['sides'][side] if side < 6 else tile['center']
        if feature_type == MEADOW:
            return False, "Нельзя ставить мипла на луг"

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
        visited = set()
        stack = [(q, r, side)]
        while stack:
            curr_q, curr_r, curr_s = stack.pop()
            if (curr_q, curr_r, curr_s) in visited: continue
            visited.add((curr_q, curr_r, curr_s))
            curr_tile = self.board.get((curr_q, curr_r))
            if not curr_tile: continue
            feature_type = curr_tile['sides'][curr_s] if curr_s < 6 else curr_tile['center']
            for group in curr_tile['connections']:
                if curr_s in group:
                    for other_idx in group:
                        if other_idx != curr_s:
                            stack.append((curr_q, curr_r, other_idx))
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
            if s == 6:
                tile = self.board.get((q, r))
                if tile and tile['center'] == MONASTERY:
                    neighbors_count = 0
                    for nq, nr, _, _ in self.get_neighbors(q, r):
                        if (nq, nr) in self.board:
                            neighbors_count += 1
                    if neighbors_count < 6: return False
                continue
            neighbors = self.get_neighbors(q, r)
            nq, nr, _, _ = neighbors[s]
            if (nq, nr) not in self.board:
                return False
        return True

    def score_completed_features(self):
        if not self.last_placed_pos: return
        q, r = self.last_placed_pos
        tile = self.board[(q, r)]
        processed_features = []
        for side in range(7):
            feature_type = tile['sides'][side] if side < 6 else tile['center']
            if feature_type not in [CITY, ROAD, MONASTERY]: continue
            feature = self.get_feature(q, r, side)
            feature_tuple = tuple(sorted(list(feature)))
            if feature_tuple in processed_features: continue
            processed_features.append(feature_tuple)
            if self.is_feature_complete(feature):
                self.award_points(feature, feature_type)

    def award_points(self, feature, feature_type):
        meeple_counts = {}
        feature_meeples = []
        for m in self.meeples:
            if (m['q'], m['r'], m['side']) in feature:
                meeple_counts[m['user_id']] = meeple_counts.get(m['user_id'], 0) + 1
                feature_meeples.append(m)
        if not meeple_counts: return
        max_meeples = max(meeple_counts.values())
        winners = [uid for uid, count in meeple_counts.items() if count == max_meeples]
        unique_tiles = set((q, r) for q, r, s in feature)
        points = len(unique_tiles) * (2 if feature_type == CITY else 1)
        if feature_type == MONASTERY: points = 7
        for uid in winners:
            self.scores[uid] = self.scores.get(uid, 0) + points
            self.log.append(f"Игрок {uid} получил {points} очков!")
        for m in feature_meeples:
            self.meeples.remove(m)

    def get_and_clear_log(self):
        log = self.log
        self.log = []
        return log

    def to_dict(self):
        return {
            'room_id': self.room_id,
            'board': {f"{q},{r}": v for (q, r), v in self.board.items()},
            'current_player_index': self.current_player_index,
            'players': self.players,
            'scores': self.scores,
            'current_tile': self.current_tile,
            'valid_placements': self.get_valid_placements(),
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
