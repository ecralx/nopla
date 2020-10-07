import sys
from flask import Flask
from flask_socketio import SocketIO
from flask_pymongo import PyMongo
import os
from redis import from_url as redis_from_url

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET')
app.config['MONGO_URI'] = os.getenv('MONGODB_URI')
app.config['REDIS_URL'] = os.getenv('REDIS_URL')
mongo = PyMongo(app)
redis = redis_from_url(app.config['REDIS_URL'])
socketio = SocketIO(app, cors_allowed_origins="*")

from .routes import *