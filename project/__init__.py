from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_modus import Modus

app = Flask(__name__)
modus = Modus(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://localhost/local-playlist'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

@app.route('/')
def root():
    return "HELLO BLUEPRINTS!"