from app import create_app, db
from app.models import User, Room

app = create_app()

def test_db():
    with app.app_context():
        # Clean up
        db.drop_all()
        db.create_all()

        # Test User
        u = User(username='testuser')
        u.set_password('password')
        db.session.add(u)
        db.session.commit()

        user = User.query.filter_by(username='testuser').first()
        assert user is not None
        assert user.check_password('password')

        # Test Room
        r = Room(name='testroom', created_by=user.id)
        db.session.add(r)
        db.session.commit()

        room = Room.query.filter_by(name='testroom').first()
        assert room is not None
        print("Models test passed!")

if __name__ == "__main__":
    test_db()
