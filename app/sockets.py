from flask_socketio import join_room, leave_room, emit
from flask_login import current_user
from . import socketio, db
from .models import Room
from .game.engine import GameEngine
import json

game_engines = {}

def get_engine(room_id):
    room_id = int(room_id)
    if room_id not in game_engines:
        room = Room.query.get(room_id)
        if room and room.game_state:
            state = json.loads(room.game_state)
            game_engines[room_id] = GameEngine.from_dict(state)
        elif room:
            game_engines[room_id] = GameEngine(room_id)
            save_engine(room_id)
    return game_engines.get(room_id)

def save_engine(room_id):
    engine = game_engines.get(room_id)
    if engine:
        room = Room.query.get(room_id)
        room.game_state = json.dumps(engine.to_dict())
        db.session.commit()

@socketio.on('join')
def on_join(data):
    room_id = int(data['room'])
    join_room(str(room_id))

    engine = get_engine(room_id)
    if engine and current_user.is_authenticated:
        engine.add_player(current_user.id)
        save_engine(room_id)

    if engine:
        emit('game_update', engine.to_dict(), room=str(room_id))
    emit('message', {'msg': f'User {current_user.username} joined room {room_id}'}, room=str(room_id))

@socketio.on('rotate_tile')
def on_rotate_tile(data):
    room_id = int(data['room'])
    engine = get_engine(room_id)
    if engine and engine.players and engine.players[engine.current_player_index] == current_user.id:
        engine.rotate_current_tile()
        emit('game_update', engine.to_dict(), room=str(room_id))

@socketio.on('place_tile')
def on_place_tile(data):
    room_id = int(data['room'])
    q, r = int(data['q']), int(data['r'])
    engine = get_engine(room_id)
    if engine:
        success, msg = engine.place_tile(current_user.id, q, r)
        if success:
            save_engine(room_id)
            emit('game_update', engine.to_dict(), room=str(room_id))
        else:
            emit('error', {'msg': msg})
