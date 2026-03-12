import random
from .tiles import get_deck, CITY, ROAD, MONASTERY, MEADOW

class GameEngine:
    COLORS = [
        {'name': 'Красный', 'hex': '#dc3545'},
        {'name': 'Синий', 'hex': '#0d6efd'},
        {'name': 'Зеленый', 'hex': '#198754'},
        {'name': 'Желтый', 'hex': '#ffc107'},
        {'name': 'Черный', 'hex': '#212529'},
        {'name': 'Белый', 'hex': '#f8f9fa'}
    ]

    def __init__(self, room_id):
        self.room_id = room_id
        self.board = {} # {(q, r): tile_data}
        self.players = [] # list of user_ids (strings)
        self.player_names = {} # {user_id: username}
        self.player_colors = {} # {user_id: color_hex}
        self.scores = {} # {user_id: score}
        self.current_player_index = 0
        self.deck = get_deck()
        self.meeples = [] # list of {'q': q, 'r': r, 'side': side, 'user_id': user_id, 'type': type}
        self.current_tile = None
        self.last_placed_pos = None # (q, r)
        self.state = 'SELECTING_COLORS' # SELECTING_COLORS, PLACING_TILE, PLACING_MEEPLE
        self.log = []
        self.last_completed_feature = None # {'feature': set, 'color': hex}

        # Initial tile at (0, 0)
        if self.deck:
            # For the initial tile, we just take the first one from deck
            # but we need to ensure it has connections meta
            start_tile = self.deck.pop(0)
            self.board[(0, 0)] = start_tile

        self.current_tile = None

    def add_player(self, user_id, username):
        user_id = str(user_id)
        if user_id not in self.players:
            self.players.append(user_id)
            self.player_names[user_id] = username
            self.scores[user_id] = 0
            return True
        return False

    def select_color(self, user_id, color_hex):
        user_id = str(user_id)
        if self.state != 'SELECTING_COLORS':
            return False, "Выбор цветов завершен"
        if self.players[self.current_player_index] != user_id:
            return False, "Не ваша очередь выбирать цвет"
        if color_hex in self.player_colors.values():
            return False, "Этот цвет уже занята"

        self.player_colors[user_id] = color_hex
        self.current_player_index += 1

        if self.current_player_index >= len(self.players):
            self.current_player_index = 0
            self.state = 'PLACING_TILE'
            self.next_turn()
        return True, "Успех"

    def next_turn(self):
        self.last_completed_feature = None
        while self.deck:
            tile = self.deck.pop(0)
            if self.can_tile_be_placed(tile):
                self.current_tile = tile
                self.state = 'PLACING_TILE'
                return True
            else:
                self.log.append(f"Плитка {tile['id']} сброшена (некуда поставить)")

        self.current_tile = None
        if self.state != 'GAME_OVER':
            self.score_unfinished_features_at_end()
            self.state = 'GAME_OVER'
        return False

    def score_unfinished_features_at_end(self):
        self.log.append("Игра окончена. Подсчет очков за незавершенные объекты...")
        processed_features = set()

        # We need to copy meeples because award_points removes them
        meeples_to_process = self.meeples[:]

        for m in meeples_to_process:
            q, r, side = m['q'], m['r'], m['side']
            feature = self.get_feature(q, r, side)
            feature_tuple = tuple(sorted(list(feature)))

            if feature_tuple in processed_features:
                continue
            processed_features.add(feature_tuple)

            tile = self.board.get((q, r))
            if not tile: continue
            feature_type = tile['sides'][side] if side < 6 else tile['center']

            # Award points for unfinished feature
            self.award_points(feature, feature_type, m['user_id'], is_final=True)

    def can_tile_be_placed(self, tile):
        candidates = set()
        for (q, r) in self.board:
            for nq, nr, _, _ in self.get_neighbors(q, r):
                if (nq, nr) not in self.board:
                    candidates.add((nq, nr))

        temp_tile = tile.copy()
        temp_tile['sides'] = tile['sides'][:]
        temp_tile['connections'] = [g[:] for g in tile['connections']]

        for _ in range(6):
            for q, r in candidates:
                if self.is_valid_placement(q, r, temp_tile):
                    return True

            sides = temp_tile['sides']
            temp_tile['sides'] = [sides[5]] + sides[0:5]
            new_conns = []
            for group in temp_tile['connections']:
                new_group = []
                for idx in group:
                    new_group.append((idx + 1) % 6 if idx < 6 else 6)
                new_conns.append(new_group)
            temp_tile['connections'] = new_conns
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
                    new_group.append((idx + 1) % 6 if idx < 6 else 6)
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
            uname = self.player_names.get(user_id, user_id)
            self.log.append(f"Пользователь {uname} разместил плитку {self.current_tile['id']} на ({q}, {r})")
            return True, "Успех"
        return False, "Недопустимое размещение"

    def skip_meeple(self, user_id):
        user_id = str(user_id)
        if self.state != 'PLACING_MEEPLE':
            return False, "Сейчас нельзя пропустить мипла"
        if self.players[self.current_player_index] != user_id:
            return False, "Не ваш ход"
        self.score_completed_features(user_id)
        self.current_player_index = (self.current_player_index + 1) % len(self.players)
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
        self.score_completed_features(user_id)
        self.current_player_index = (self.current_player_index + 1) % len(self.players)
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
                    else: return True # Monastery is complete if 6 neighbors
                continue
            neighbors = self.get_neighbors(q, r)
            nq, nr, _, _ = neighbors[s]
            if (nq, nr) not in self.board:
                return False
        return True

    def score_completed_features(self, user_id):
        if not self.last_placed_pos: return
        q, r = self.last_placed_pos
        tile = self.board[(q, r)]
        processed_features = []

        # Check all features in the room (not just on the tile) to find completed monasteries
        features_to_check = []
        for side in range(7):
            features_to_check.append((q, r, side))

        # Also check neighbors for monasteries that might have been completed
        for nq, nr, _, _ in self.get_neighbors(q, r):
            if (nq, nr) in self.board:
                features_to_check.append((nq, nr, 6))

        for cq, cr, cs in features_to_check:
            curr_tile = self.board.get((cq, cr))
            if not curr_tile: continue
            feature_type = curr_tile['sides'][cs] if cs < 6 else curr_tile['center']
            if feature_type not in [CITY, ROAD, MONASTERY]: continue

            feature = self.get_feature(cq, cr, cs)
            feature_tuple = tuple(sorted(list(feature)))
            if feature_tuple in processed_features: continue
            processed_features.append(feature_tuple)

            if self.is_feature_complete(feature):
                self.award_points(feature, feature_type, user_id)

    def award_points(self, feature, feature_type, finisher_id, is_final=False):
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

        if is_final:
            if feature_type == MONASTERY:
                # 1 point for monastery tile + 1 per neighbor
                q_m, r_m, _ = list(feature)[0] # Monastery feature has only 1 tile-side group
                neighbors_count = 0
                for nq, nr, _, _ in self.get_neighbors(q_m, r_m):
                    if (nq, nr) in self.board:
                        neighbors_count += 1
                points = 1 + neighbors_count
            else:
                # 1 point per tile for roads and cities
                points = len(unique_tiles)
        else:
            points = len(unique_tiles) * (2 if feature_type == CITY else 1)
            if feature_type == MONASTERY: points = 7

        for uid in winners:
            self.scores[uid] = self.scores.get(uid, 0) + points
            username = self.player_names.get(uid, f"Игрок {uid}")
            status = "незавершенный" if is_final else "завершенный"
            self.log.append(f"Пользователь {username} получил {points} очков за {status} объект!")

        if not is_final:
            self.last_completed_feature = {
                'feature': list(unique_tiles),
                'color': self.player_colors.get(finisher_id, '#ffffff')
            }

        for m in feature_meeples:
            if m in self.meeples:
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
            'player_names': self.player_names,
            'player_colors': self.player_colors,
            'available_colors': self.COLORS,
            'scores': self.scores,
            'current_tile': self.current_tile,
            'valid_placements': self.get_valid_placements(),
            'deck_size': len(self.deck),
            'meeples': self.meeples,
            'state': self.state,
            'last_placed_pos': self.last_placed_pos,
            'last_completed_feature': self.last_completed_feature
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
        engine.player_names = data.get('player_names', {})
        engine.player_colors = data.get('player_colors', {})
        engine.scores = data.get('scores', {})
        engine.current_player_index = data.get('current_player_index', 0)
        engine.current_tile = data.get('current_tile')
        engine.deck = data.get('deck', [])
        engine.meeples = data.get('meeples', [])
        engine.state = data.get('state', 'SELECTING_COLORS')
        engine.last_placed_pos = data.get('last_placed_pos')
        engine.last_completed_feature = data.get('last_completed_feature')
        return engine
