# Feature types
MEADOW = 'meadow'
CITY = 'city'
ROAD = 'road'
MONASTERY = 'monastery'

# Tile definition (6 sides)
# Sides index: 0=East, 1=South-East, 2=South-West, 3=West, 4=North-West, 5=North-East
# connections: groups of indices [0-5 for sides, 6 for center] that are connected
TILES = [
    {
        'id': 'city_all',
        'sides': [CITY]*6,
        'center': CITY,
        'connections': [[0, 1, 2, 3, 4, 5, 6]],
        'count': 2
    },
    {
        'id': 'road_straight',
        'sides': [MEADOW, MEADOW, ROAD, MEADOW, MEADOW, ROAD],
        'center': ROAD,
        'connections': [[2, 5, 6]],
        'count': 8
    },
    {
        'id': 'city_one_side',
        'sides': [CITY, MEADOW, MEADOW, MEADOW, MEADOW, MEADOW],
        'center': MEADOW,
        'connections': [[0]],
        'count': 8
    },
    {
        'id': 'monastery',
        'sides': [MEADOW]*6,
        'center': MONASTERY,
        'connections': [[6]],
        'count': 4
    },
    {
        'id': 'city_road',
        'sides': [CITY, MEADOW, ROAD, MEADOW, ROAD, MEADOW],
        'center': MEADOW,
        'connections': [[0], [2, 4]], # Road connects side 2 and 4, City is separate on side 0
        'count': 5
    },
    {
        'id': 'road_curved',
        'sides': [ROAD, ROAD, MEADOW, MEADOW, MEADOW, MEADOW],
        'center': ROAD,
        'connections': [[0, 1, 6]],
        'count': 5
    }
]

def get_deck():
    deck = []
    for t in TILES:
        for _ in range(t['count']):
            # Deep copy connections
            t_copy = t.copy()
            t_copy['connections'] = [group[:] for group in t['connections']]
            deck.append(t_copy)
    import random
    random.shuffle(deck)
    return deck
