from dotenv import load_dotenv
from flask import Flask
from flask_socketio import SocketIO
from flask_pymongo import PyMongo
import os
#from redis import Redips


load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET')
app.config["MONGO_URI"] = os.getenv('MONGODB_URI')
mongo = PyMongo(app)
#redis = Redis()
socketio = SocketIO(app, cors_allowed_origins="*")

from .routes import *