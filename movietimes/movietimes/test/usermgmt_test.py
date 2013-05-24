from __future__ import with_statement
import sys, os
import code
from flask import request
parentdir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0,parentdir) 
print sys.path
import movietimes
from movietimes import app
#app = Flask(__name__)
import unittest
import json


class SkeletonTestCase(unittest.TestCase):
    def setUp(self):
        app.config['DB_NAME'] = "movietimes_test"
        app.debug = True
        self.app = app.test_client()
        movietimes.init_db()

    def tearDown(self):
        movietimes.drop_db()

    def login(self, email, password):
        return self.app.post('/login',
                    data=dict(email=email,
                              password=password),
                    follow_redirects=True)

    def logout(self):
        return self.app.get('/logout',
                    follow_redirects=True)

    def verify_login(self):
        rv = self.app.get('/me.json')
        self.assertEqual(json.loads(rv.data)['user']['email'], 'mikeo@10gen.com')

class RegisterTest(SkeletonTestCase):
    data=dict(email='mikeo@10gen.com',
              password='12345',
              confirm='12345')


    def test_register_success(self):

        rv = self.app.post('/register', data=RegisterTest.data, follow_redirects=True)
        print rv.data
        self.verify_login()
        self.logout()
        rv = self.app.get('/me.json')
        self.assertEqual(json.loads(rv.data)['user'], None)
        self.login('mikeo@10gen.com', '12345')
        self.verify_login()
                      
    def test_reset_password(self):
        rv = self.app.post('/register', data=RegisterTest.data, follow_redirects=True)
        self.logout()
        self.app.post('/forgot', data=dict(email='mikeo@10gen.com'))
        from movietimes import database
        token = database.db.tokens.find_one({"email":"mikeo@10gen.com"})
        assert token is not None
        self.app.get('/reset/' + token['_id'])
        self.verify_login()
        self.app.post('/changepw', data=dict(password='54321', confirm='54321'))
        self.logout()
        self.login('mikeo@10gen.com', '54321')
        self.verify_login()

