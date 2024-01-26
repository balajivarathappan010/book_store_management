import unittest
import json,os
from main import app, db, Book

class TestBookAPI(unittest.TestCase):
    
    def setUp(self):
        app.config['TESTING'] = True
        basedir = os.path.abspath(os.path.dirname(__file__))
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///'+os.path.join(basedir, 'db.sqlite')
        self.app = app.test_client()
        db.create_all()
    def tearDown(self):
        db.session.remove()
        db.drop_all()
    def test_valid_login(self):
        response = self.app.post('/login', json={'username': 'admin', 'password': 'balaji'})
        data = json.loads(response.data.decode('utf-8'))
        self.assertEqual(response.status_code, 200)
        self.assertIn('access_token', data)
        print(data)
    def test_invalid_login(self):
        response = self.app.post('/login', json={'username': 'invalid', 'password': 'invalid'})
        self.assertEqual(response.status_code, 401)
        data = json.loads(response.data.decode('utf-8'))
        self.assertEqual(data['message'], 'Invalid username or password')

    def test_add_books(self):
        access_token = self.get_access_token()
        response = self.app.post('/book', json={'title': 'The Great Gatsby', 'author': 'F. Scott Fitzgerald', 'isbn': '9780743273565', 'price': 9.99, 'quantity': 25}, headers={'Authorization': 'Bearer ' + access_token})
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data.decode('utf-8'))
        self.assertEqual(data['title'], 'Book1')

    def test_show_all_book(self):
        access_token = self.get_access_token()
        response = self.app.get('/book', headers={'Authorization': 'Bearer ' + access_token})
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data.decode('utf-8'))
        self.assertEqual(len(data), 0)

    def test_get_book_by_id(self):
        access_token = self.get_access_token()
        response = self.app.get('/book/2', headers={'Authorization': 'Bearer ' + access_token})
        self.assertEqual(response.status_code, 404)

    def test_update_user_by_author(self):
        access_token = self.get_access_token()
        response = self.app.put('/book/Harper_Lee', json={'title': 'Go Set a Watchman', 'price': 20.0, 'quantity': 10}, headers={'Authorization': 'Bearer ' + access_token})
        self.assertEqual(response.status_code, 404)  

    def test_delete_book(self):
        access_token = self.get_access_token()
        response = self.app.delete('/book/1', headers={'Authorization': 'Bearer ' + access_token})
        self.assertEqual(response.status_code, 404) 

    def get_access_token(self):
        response = self.app.post('/login', json={'username': 'admin', 'password': 'balaji'})
        data = json.loads(response.data.decode('utf-8'))
        return data['access_token']
if __name__ == '__main__':
    unittest.main()
