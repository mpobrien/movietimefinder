from flask import Flask, session, g, render_template
from flask.ext.pymongo import PyMongo

from flask.ext.login import (LoginManager, current_user, login_required,
                            login_user, logout_user, UserMixin, AnonymousUser,
                            confirm_login, fresh_login_required)
app = Flask(__name__)
app.secret_key = '\xff\x19\xf4\xde\xc4T\n\x8a\xb7\x02h}\xadD\xe2\xa1\x86\x9b\xe3\xbf-\x95.\xa8'
app.debug = True

app.config['MONGO_URL'] = 'mongodb://localhost:27017/'
app.config['CSS_FRAMEWORK'] = 'bootstrap'; # foundation
app.config['MONGO_DBNAME'] = 'movies';
mongo = PyMongo(app)
app.mongo = mongo

login_manager = LoginManager()

login_manager.anonymous_user = AnonymousUser
login_manager.login_view = "login"
login_manager.login_message = u"Please log in to access this page."
login_manager.refresh_view = "reauth"

login_manager.setup_app(app)

@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404

from usermgmt import usermgmt 
from movietimes.views import general
app.register_blueprint(usermgmt.mod)
app.register_blueprint(general.mod)



def init_db(index=False):
    with app.test_request_context():
        from movietimes.database import *
        #database.c = mongo.cx
        #database.db = database.c[app.config['DB_NAME']]
        database.ensure_indexes()

def drop_db():
    database.c.drop_database('movietimes_test')

init_db(True)
