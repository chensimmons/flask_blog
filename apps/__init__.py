
import os

from flask_sqlalchemy import SQLAlchemy
from flask import Flask
from apps.utils import create_folder

app = Flask(__name__)

app.config["SECRET_KEY"] = "And though you might be gone, And the world may not know"
app.debug = True
app.config['MAX_CONTENT_LENGTH'] = 8*1024*1024



# app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///flasker.db"
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://root:chen@localhost/flasker"

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True

db = SQLAlchemy(app)

APPS_DIR = os.path.dirname(__file__)
STATIC_DIR = os.path.join(APPS_DIR,'static')

app.config['UPLOADS_RELATIVE'] = 'uploads'
app.config['UPLOADS_FOLDER'] = os.path.join(STATIC_DIR, app.config['UPLOADS_RELATIVE'])

app.config["UPLOADED_PHOTOS_DEST"] = app.config['UPLOADS_FOLDER']
create_folder(app.config['UPLOADS_FOLDER'])


# print('init_db:', app.config["DATABASE"])



from apps import views