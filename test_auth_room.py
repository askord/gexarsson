import unittest
from app import create_app, db
from app.models import User, Room

class TestAuthRoom(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.client = self.app.test_client()
        with self.app.app_context():
            db.create_all()

    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    def test_register_login(self):
        # Register
        response = self.client.post('/register', data=dict(username='test', password='password'), follow_redirects=True)
        self.assertIn('Войти'.encode('utf-8'), response.data)

        # Login
        response = self.client.post('/login', data=dict(username='test', password='password'), follow_redirects=True)
        # Check if username is in the navbar
        self.assertIn('test'.encode('utf-8'), response.data)

        # Logout
        response = self.client.get('/logout', follow_redirects=True)
        self.assertIn('Добро пожаловать'.encode('utf-8'), response.data)

    def test_create_room(self):
        # Login first
        self.client.post('/register', data=dict(username='test', password='password'), follow_redirects=True)
        self.client.post('/login', data=dict(username='test', password='password'), follow_redirects=True)

        # Create Room
        response = self.client.post('/create_room', data=dict(room_name='myroom'), follow_redirects=True)
        self.assertIn('Комната: myroom'.encode('utf-8'), response.data)

        with self.app.app_context():
            room = Room.query.filter_by(name='myroom').first()
            self.assertIsNotNone(room)

if __name__ == '__main__':
    unittest.main()
