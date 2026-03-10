# Feature types
MEADOW = 'meadow'
CITY = 'city'
ROAD = 'road'
MONASTERY = 'monastery'

# Tile definition (6 sides)
# Sides index: 0=top, 1=top-right, 2=bottom-right, 3=bottom, 4=bottom-left, 5=top-left
TILES = [
    {
        'id': 'city_all',
        'sides': [CITY, CITY, CITY, CITY, CITY, CITY],
        'center': CITY,
        'count': 1
    },
    {
        'id': 'road_straight',
        'sides': [MEADOW, MEADOW, ROAD, MEADOW, MEADOW, ROAD],
        'center': ROAD,
        'count': 5
    },
    {
        'id': 'city_one_side',
        'sides': [CITY, MEADOW, MEADOW, MEADOW, MEADOW, MEADOW],
        'center': MEADOW,
        'count': 5
    },
    {
        'id': 'monastery',
        'sides': [MEADOW, MEADOW, MEADOW, MEADOW, MEADOW, MEADOW],
        'center': MONASTERY,
        'count': 2
    },
    {
        'id': 'city_road',
        'sides': [CITY, MEADOW, ROAD, MEADOW, ROAD, MEADOW],
        'center': MEADOW,
        'count': 3
    }
]

def get_deck():
    deck = []
    for t in TILES:
        for _ in range(t['count']):
            deck.append(t.copy())
    import random
    random.shuffle(deck)
    return deck
