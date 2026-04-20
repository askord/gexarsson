import os
from flask import render_template, redirect, url_for, request, flash, current_app, abort
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.utils import secure_filename
from . import db
from .models import User, Room, TileImage
from .game.tiles import TILES

def init_routes(app):
    @app.route('/')
    def index():
        if current_user.is_authenticated:
            return redirect(url_for('dashboard'))
        return render_template('index.html')

    @app.route('/register', methods=['GET', 'POST'])
    def register():
        if request.method == 'POST':
            username = request.form.get('username')
            password = request.form.get('password')
            if User.query.filter_by(username=username).first():
                flash('Username already exists')
                return redirect(url_for('register'))
            user = User(username=username)
            user.set_password(password)
            db.session.add(user)
            db.session.commit()
            return redirect(url_for('login'))
        return render_template('register.html')

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if request.method == 'POST':
            username = request.form.get('username')
            password = request.form.get('password')
            user = User.query.filter_by(username=username).first()
            if user and user.check_password(password):
                login_user(user)
                return redirect(url_for('dashboard'))
            flash('Invalid username or password')
        return render_template('login.html')

    @app.route('/logout')
    @login_required
    def logout():
        logout_user()
        return redirect(url_for('index'))

    @app.route('/dashboard')
    @login_required
    def dashboard():
        rooms = Room.query.filter_by(is_active=True).all()
        return render_template('dashboard.html', rooms=rooms)

    @app.route('/create_room', methods=['POST'])
    @login_required
    def create_room():
        room_name = request.form.get('room_name')
        if Room.query.filter_by(name=room_name).first():
            flash('Room name already exists')
            return redirect(url_for('dashboard'))
        room = Room(name=room_name, created_by=current_user.id)
        db.session.add(room)
        db.session.commit()
        return redirect(url_for('game', room_id=room.id))

    @app.route('/game/<int:room_id>')
    @login_required
    def game(room_id):
        room = Room.query.get_or_404(room_id)
        # Get custom images
        custom_images = {ti.tile_id: ti.image_filename for ti in TileImage.query.all()}
        return render_template('game.html', room=room, custom_images=custom_images)

    @app.route('/admin/tiles', methods=['GET', 'POST'])
    @login_required
    def admin_tiles():
        if not current_user.is_admin:
            abort(403)

        if request.method == 'POST':
            tile_id = request.form.get('tile_id')
            file = request.files.get('file')
            if file and tile_id:
                filename = secure_filename(file.filename)
                upload_folder = os.path.join(current_app.static_folder, 'custom_tiles')
                os.makedirs(upload_folder, exist_ok=True)
                file.save(os.path.join(upload_folder, filename))

                ti = TileImage.query.filter_by(tile_id=tile_id).first()
                if ti:
                    ti.image_filename = filename
                else:
                    ti = TileImage(tile_id=tile_id, image_filename=filename)
                    db.session.add(ti)
                db.session.commit()
                flash(f'Изображение для {tile_id} успешно обновлено')
            return redirect(url_for('admin_tiles'))

        custom_images = {ti.tile_id: ti.image_filename for ti in TileImage.query.all()}
        return render_template('admin_tiles.html', tiles=TILES, custom_images=custom_images)
