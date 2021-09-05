from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from redis import Redis
from flask_wtf.csrf import CSRFProtect
import os
from flask_login import LoginManager

redis = Redis()
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = os.path.realpath('.') +'/my_app/static/uploads'
app.config['WTF_CSRF_SECRET_KEY']  = 'random key for form'
app.config["FACEBOOK_OAUTH_CLIENT_ID"] = 'key from developer account'
app.config["FACEBOOK_OAUTH_CLIENT_SECRET"] = 'key from developer account'


CSRFProtect(app)
db = SQLAlchemy(app)

migrate = Migrate(app, db)

app.secret_key = 'some_random_key'

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.login'

from my_app.catalog.views import catalog
from my_app.auth.views import auth
from my_app.auth.views import facebook_blueprint

app.register_blueprint(catalog)
app.register_blueprint(auth)
app.register_blueprint(facebook_blueprint)

db.create_all()
