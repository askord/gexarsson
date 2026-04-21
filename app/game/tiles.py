# Feature types
MEADOW = 'meadow'
CITY = 'city'
ROAD = 'road'
MONASTERY = 'monastery'

# Tile definition (6 sides)
# Sides index: 0=East, 1=South-East, 2=South-West, 3=West, 4=North-West, 5=North-East
# connections: groups of indices [0-5 for sides, 6 for center] that are connected

TILES = [

    # ===== ГОРОДА =====
    {
        'id': 'city_all',
        'sides': [CITY]*6,
        'center': CITY,
        'connections': [[0,1,2,3,4,5,6]],
        'count': 2
    },
    {
        'id': 'city_one',
        'sides': [CITY, MEADOW, MEADOW, MEADOW, MEADOW, MEADOW],
        'center': MEADOW,
        'connections': [[0]],
        'count': 8
    },
    {
        'id': 'city_two_adjacent',
        'sides': [CITY, CITY, MEADOW, MEADOW, MEADOW, MEADOW],
        'center': MEADOW,
        'connections': [[0,1]],
        'count': 6
    },
    {
        'id': 'city_two_opposite',
        'sides': [CITY, MEADOW, MEADOW, CITY, MEADOW, MEADOW],
        'center': MEADOW,
        'connections': [[0],[3]],
        'count': 5
    },
    {
        'id': 'city_three',
        'sides': [CITY, CITY, CITY, MEADOW, MEADOW, MEADOW],
        'center': MEADOW,
        'connections': [[0,1,2]],
        'count': 4
    },

    # ===== ДОРОГИ =====
    {
        'id': 'road_straight',
        'sides': [MEADOW, MEADOW, ROAD, MEADOW, MEADOW, ROAD],
        'center': ROAD,
        'connections': [[2,5,6]],
        'count': 8
    },
    {
        'id': 'road_curve',
        'sides': [ROAD, ROAD, MEADOW, MEADOW, MEADOW, MEADOW],
        'center': ROAD,
        'connections': [[0,1,6]],
        'count': 8
    },
    {
        'id': 'road_t',
        'sides': [ROAD, ROAD, ROAD, MEADOW, MEADOW, MEADOW],
        'center': ROAD,
        'connections': [[0,1,2,6]],
        'count': 6
    },
    {
        'id': 'road_cross',
        'sides': [ROAD]*6,
        'center': ROAD,
        'connections': [[0,1,2,3,4,5,6]],
        'count': 2
    },
    {
        'id': 'road_dead_end',
        'sides': [ROAD, MEADOW, MEADOW, MEADOW, MEADOW, MEADOW],
        'center': ROAD,
        'connections': [[0,6]],
        'count': 4
    },

    # ===== ГОРОД + ДОРОГА =====
    {
        'id': 'city_road',
        'sides': [CITY, MEADOW, ROAD, MEADOW, ROAD, MEADOW],
        'center': MEADOW,
        'connections': [[0], [2,4]],
        'count': 6
    },
    {
        'id': 'city_road_curve',
        'sides': [CITY, ROAD, ROAD, MEADOW, MEADOW, MEADOW],
        'center': ROAD,
        'connections': [[0], [1,2,6]],
        'count': 5
    },
    {
        'id': 'city_split',
        'sides': [CITY, ROAD, CITY, ROAD, MEADOW, MEADOW],
        'center': MEADOW,
        'connections': [[0], [2], [1,3]],
        'count': 4
    },

    # ===== МОНАСТЫРИ =====
    {
        'id': 'monastery',
        'sides': [MEADOW]*6,
        'center': MONASTERY,
        'connections': [[6]],
        'count': 6
    },
    {
        'id': 'monastery_road',
        'sides': [ROAD, MEADOW, MEADOW, MEADOW, MEADOW, MEADOW],
        'center': MONASTERY,
        'connections': [[6], [0]],
        'count': 4
    },

    # ===== ПОЛЯ =====
    {
        'id': 'meadow',
        'sides': [MEADOW]*6,
        'center': MEADOW,
        'connections': [[0,1,2,3,4,5]],
        'count': 4
    },

    # ===== МИКС =====
    {
        'id': 'mixed',
        'sides': [CITY, ROAD, MEADOW, CITY, ROAD, MEADOW],
        'center': MEADOW,
        'connections': [[0],[3],[1,4]],
        'count': 4
    }
]

def get_deck():
    deck = []
    for t in TILES:
        for _ in range(t['count']):
            t_copy = t.copy()
            t_copy['connections'] = [group[:] for group in t['connections']]
            deck.append(t_copy)

    import random
    random.shuffle(deck)
    return deck
