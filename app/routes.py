from flask import render_template, redirect, url_for, request, flash
from flask_login import login_user, logout_user, login_required, current_user
from . import db
from .models import User, Room

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
        return render_template('game.html', room=room)
