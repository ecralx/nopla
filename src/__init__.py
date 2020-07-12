from decouple import config
from flask import Flask
from flask_socketio import SocketIO
from flask_pymongo import PyMongo
#from redis import Redips


app = Flask(__name__)
app.config['SECRET_KEY'] = config('SECRET')
app.config["MONGO_URI"] = config('MONGODB_URI')

mongo = PyMongo(app)
#redis = Redis()
socketio = SocketIO(app, cors_allowed_origins="*")

from .routes import *