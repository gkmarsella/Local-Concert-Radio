from flask import Flask, render_template, request, redirect, url_for, jsonify, session, g
from flask_modus import Modus
from flask_sqlalchemy import SQLAlchemy
import os
import requests
from flask_oauthlib.client import OAuth, OAuthException
import random
import string
from requests.utils import quote
import json
import time
import psycopg2
import cities
from datetime import datetime

OAUTH_TOKEN_URL = 'https://accounts.spotify.com/api/token'


app = Flask(__name__)
app.debug = True
app.secret_key = 'development'
oauth = OAuth(app)
modus = Modus(app)

if os.environ.get('ENV') == 'production':
    debug = False
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')

else:
    debug = True
    app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 1
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://localhost/local-playlist'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
SPOTIFY_CLIENT_ID = app.config['SPOTIFY_CLIENT_ID'] = os.environ.get('SPOTIFY_CLIENT_ID')
SPOTIFY_CLIENT_SECRET = app.config['SPOTIFY_CLIENT_SECRET'] = os.environ.get('SPOTIFY_CLIENT_SECRET')

# ************************************************************************************************************************
#                                                       DATABASE        
# ************************************************************************************************************************

UserGenre = db.Table('user_genres',
                    db.Column('id',
                        db.Integer,
                        primary_key=True),
                    db.Column('user_id',
                        db.Integer,
                        db.ForeignKey('users.id', ondelete="cascade")),
                    db.Column('genre_id',
                        db.Integer,
                        db.ForeignKey('genres.id', ondelete="cascade")))


UserArtist = db.Table('user_artists',
                    db.Column('id',
                        db.Integer,
                        primary_key=True),
                    db.Column('user_id',
                        db.Integer,
                        db.ForeignKey('users.id', ondelete="cascade")),
                    db.Column('artist_id',
                        db.Integer,
                        db.ForeignKey('artists.id', ondelete="cascade")))


UserEvent = db.Table('user_events',
                    db.Column('id',
                        db.Integer,
                        primary_key=True),
                    db.Column('user_id',
                        db.Integer,
                        db.ForeignKey('users.id', ondelete="cascade")),
                    db.Column('event_id',
                        db.Integer,
                        db.ForeignKey('events.id', ondelete="cascade")))



class User(db.Model):


    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    user_name = db.Column(db.Text)
    user_email = db.Column(db.Text)
    genres = db.relationship("Genre",
                            secondary=UserGenre,
                            backref=db.backref('users'))

    artists = db.relationship("Artist",
                            secondary=UserArtist,
                            backref=db.backref('users'))

    events = db.relationship("Event",
                            secondary=UserEvent,
                            backref=db.backref('users'))


    def __init__(self, user_name, user_email):
        self.user_name = user_name
        self.user_email = user_email


    def __repr__(self):
        return "The user's name and email is {} {}".format(self.user_name, self.user_email)


class Genre(db.Model):

    __tablename__ = "genres"

    id = db.Column(db.Integer, primary_key=True)
    genre = db.Column(db.Text)

    def __init__(self, genre):
        self.genre = genre


class Artist(db.Model):

    __tablename__ = "artists"

    id = db.Column(db.Integer, primary_key=True)
    artist = db.Column(db.Text)

    def __init__(self, artist):
        self.artist = artist



class Event(db.Model):

    __tablename__ = "events"

    id = db.Column(db.Integer, primary_key=True)
    event = db.Column(db.Text)
    name = db.Column(db.Text)

    def __init__(self, event, name):
        self.event = event
        self.name = name


class City(db.Model):

    __tablename__ = "cities"

    id = db.Column(db.Integer, primary_key=True)
    city = db.Column(db.Text)
    state_code = db.Column(db.Text)

    def __init__(self, city, state_code):
        self.city = city
        self.state_code = state_code

    def __repr__(self):
        return "{}".format(self.city)

# ************************************************************************************************************************
#                                              SPOTIFY AUTHENTICATION        
# ************************************************************************************************************************ 



spotify = oauth.remote_app(
    'spotify',
    consumer_key=os.environ.get('SPOTIFY_CLIENT_ID'),
    consumer_secret=os.environ.get('SPOTIFY_CLIENT_SECRET'),
    # Change the scope to match whatever it us you need
    # list of scopes can be found in the url below
    # https://developer.spotify.com/web-api/using-scopes/
    request_token_params={'scope': 'user-read-private user-read-email playlist-modify playlist-modify-private'},
    base_url='https://accounts.spotify.com',
    request_token_url=None,
    access_token_url='/api/token',
    authorize_url='https://accounts.spotify.com/authorize'
)


@app.route('/')
def home():
    # use spotify_authorize
    # get_user = session['user_name']
    return render_template('home.html')

@app.route('/index')
def index():
    return redirect(url_for('login'))


@app.route('/login')
def login():
    callback = url_for(
        'spotify_authorized',
        next=None,
        _external=True
    )
    return spotify.authorize(callback=callback)


@app.route('/callback')
def spotify_authorized():
    resp = spotify.authorized_response()
    if resp is None:
        return 'Access denied: reason={0} error={1}'.format(
            request.args['error_reason'],
            request.args['error_description']
        )
    if isinstance(resp, OAuthException):
        return 'Access denied: {0}'.format(resp.message)

    # store the token in the session
    session['oauth_token'] = (resp['access_token'], '')
    # me = spotify.get('/me')

    user_id = spotify.get("https://api.spotify.com/v1/me").data

    # get_user = session['user_name']



    if User.query.filter_by(user_name=user_id['id']).first() is None:
        new_user = User(user_id['id'], user_id['email'])
        db.session.add(new_user)
        db.session.commit()

    session['user_name'] = user_id['id']

    # Save some info to the DB
    db_to_favorites()
    return render_template("search.html",all_cities=cities.all_cities)



@spotify.tokengetter
def get_spotify_oauth_token():
    return session.get('oauth_token')



# ************************************************************************************************************************
#                                                       SPOTIFY        
# ************************************************************************************************************************





def create_playlist():

    def random_name(size=8):
        chars = list(string.ascii_lowercase + string.digits)
        return ''.join(random.choice(chars) for _ in range(size))


    user_id = spotify.get("https://api.spotify.com/v1/me").data['id']

    new_playlist = spotify.post("https://api.spotify.com/v1/users/"+  quote(user_id, safe='')  +"/playlists/", data={"name": "GeoConcert"}, headers={'Accept': 'application/json', 'Content-Type': 'application/json'}, format='json')
    return new_playlist


def search_artists(artist):
    return spotify.get("https://api.spotify.com/v1/search?q=" + quote(artist, safe='') + "&type=artist", headers={"Accept": 'application/json', "Authorization": "Bearer"})
    # artist.data['artists']['items'][0]['id']

def top_tracks(id):
    return spotify.get("https://api.spotify.com/v1/artists/" +  quote(id, safe='') +"/top-tracks?country=SE", headers={"Accept": 'application/json', "Authorization":"Bearer"})
    # gettop.data['tracks'][0]['id']

def wild_card(name):
    return spotify.get("https://api.spotify.com/v1/search?q=" +  quote(name, safe='')  + "&type=track&limit=1", headers={"Accept": 'application/json', "Authorization":"Bearer"})

def add_song(playlist, song):
    user_id = session['user_name']
    return spotify.post("https://api.spotify.com/v1/users/" +  quote(user_id, safe='')  + "/playlists/" +  quote(playlist, safe='') + "/tracks?position=0&uris=spotify%3Atrack%3A{}".format(quote(song)), headers={"Accept": 'application/json', "Authorization": "Bearer"}, format='json')


def user_playlists():

    user_id = session['user_name']
    return spotify.get("https://api.spotify.com/v1/users/" +  quote(user_id, safe='')  + "/playlists", headers={"Accept": 'application/json', "Authorization": "Bearer"})


def add_multiple(ids, playlist_id):
    # add up to 100 tracks in an array
    user_id = session['user_name']
    id_str = ",".join(ids)

    return spotify.post("https://api.spotify.com/v1/users/" +  quote(user_id, safe='')  + "/playlists/" +  quote(playlist_id, safe='') + "/tracks?uris=" + quote(ids, safe=''), headers={"Accept": 'application/json', "Authorization": "Bearer"}, format='json')

# ************************************************************************************************************************
#                                               REQUESTS
# ************************************************************************************************************************
@app.route('/event', methods=["POST"])
def event():

    name = request.json['name']
    event = request.json['event']

    get_user = User.query.filter_by(user_name=session['user_name']).first()

    if get_user is None:
        return jsonify({}), 401


    artist_event = Event.query.filter_by(name=name).first()


    if artist_event is None:
        artist_event = Event(event, name)
        db.session.add(artist_event)
        db.session.commit()


    get_user.events.append(artist_event)
    db.session.add(get_user)
    db.session.commit()


    return jsonify({'id': artist_event.id, 'name': artist_event.name, 'event': artist_event.event})

@app.route('/event/<id>', methods=["DELETE"])
def delete_event(id):
    event = Event.query.get(id)
    db.session.delete(event)
    db.session.commit()
    return jsonify({'event':event.id})


def db_to_favorites():
    get_user = User.query.filter_by(user_name=session['user_name']).first()
    g.events = get_user.events

def find_user():
    user_id = session['user_name']
    return user_id



@app.route('/search', methods=["GET", "POST"])
def search():
    db_to_favorites()
    return render_template("search.html", all_cities=cities.all_cities, get_user=get_user)


@app.route('/results', methods=["GET", "POST"])
def results():

    db_to_favorites()
    # Getting user ID to create a playlist
    user_id = session['user_name']
    datereplace = request.args.get('daterange').replace(' - ', ',')
    date = datereplace.replace('/', '')
    date_start = date[4:8] + '-' + date[:2] + '-' + date[2:4]
    date_end = date[13:17] + '-' + date[9:11] + '-' + date[11:13]
    dates = date_start + ',' + date_end

    city_arg = request.args.get('search-city')
    city = city_arg[:-4]

    state_arg = request.args.get('search-city')
    state = state_arg[-2:]



    create_playlist()

    search_bid = requests.get("http://api.bandsintown.com/events/search?format=json&api_version=2.0&app_id=YOUR_APP_ID&date=" + dates + "&location=" + city + "," + state + "&radius=" + request.args.get('search-radius'))
    search_bid = search_bid.json()


    #Getting new playlist id
    playlist_id = user_playlists().data['items'][0]['id']

    
    # creating a list of all the artists
    artist_names = []
    for s in search_bid:
        if 'artists' in s: 
            for x in s['artists']:
                artist_names.append(search_artists(x['name']).data)



    # matching all ids with their names
    artist_dict = {}
    for i in artist_names:
        if 'artists' in i and 'items' in i['artists']:
            for y in i['artists']['items']:
                artist_dict.update({y['name']:y['id']})
 

    just_names = []
    for i in artist_names:
        if 'artists' in i and 'items' in i['artists'] and len(i['artists']['items']) > 0:
            just_names.append(i['artists']['items'][0]['name'])  

    just_ids = []
    for i in artist_names:
        if 'artists' in i and 'items' in i['artists'] and len(i['artists']['items']) > 0:
            just_ids.append(i['artists']['items'][0]['id']) 


    artist_tracks = []
    for i in just_ids:
        name = top_tracks(i).data
        if 'tracks' in name and (len(name['tracks'])) > 0:
                if name['tracks'][0]['id'] is not None and name['tracks'][0]['id'] is not None:
                    artist_tracks.append('spotify:track:' + name['tracks'][0]['id'])   


    # removing all artists with 'featuring/presents' (which creates multiple duplicates if not filtered out)
    names_no_feat = {k:v for k,v in artist_dict.items() if 'feat' not in k.lower() or 'presents' not in k.lower() or 'feat.' not in k.lower or 'featuring' not in k.lower()}

##################################################################################
################################## FOR ARTIST IMAGES #############################
    def images(name):
        try:
            get_image = requests.get("http://api.bandsintown.com/artists/" +  quote(name, safe='') + ".json?api_version=2.0&app_id=YOUR_APP_ID")
            get_image = get_image.json()['image_url']
        except (json.decoder.JSONDecodeError, KeyError) as e:
            return "https://s3.amazonaws.com/bit-photos/artistLarge.jpg"
        return get_image

    first_artist = {}
    for s in search_bid:
        if 'artists' in s:
            for x in s['artists']:
                first_artist.update({s['id']:images(s['artists'][0]['name'])})
##################################################################################
##################################################################################

    song_string = ",".join(artist_tracks)

    add_multiple(song_string, playlist_id)

    iframe_data = user_playlists().data['items'][0]['external_urls']['spotify']

    iframe_embed = iframe_data.replace('.com', '.com/embed')

    https_iframe = iframe_embed.replace('http', 'https')

    spotify_player_source = https_iframe


    return render_template("results.html", search_bid=search_bid, spotify_player_source=spotify_player_source, names_no_feat=names_no_feat, user_id=user_id, playlist_id=playlist_id, first_artist=first_artist, just_names=just_names)




@app.route('/get_tracks', methods=["GET", "POST"])
def get_tracks():

    user_id = session['user_name']
    playlist_id = user_playlists().data['items'][0]['id']

    print(request.json)
    name = wild_card(request.json['artist']).data

    if 'tracks' in name and (len(name['tracks'])) > 0:
        if name['tracks'].get('items') is not None and len(name['tracks']['items']) > 0 and name['tracks']['items'][0].get('id') is not None:
            add_song(playlist_id, name['tracks']['items'][0]['id'])
            time.sleep(1.00)


    iframe_data = user_playlists().data['items'][0]['external_urls']['spotify']

    iframe_embed = iframe_data.replace('.com', '.com/embed')

    spotify_player_source = iframe_embed


    return jsonify({'url':spotify_player_source})



@app.route('/logout', methods=["GET", "POST"])
def logout():
    return AuthenticationClient.clearCookies(getApplication());

##################################################################################
######################### ERROR PAGES ############################################
##################################################################################

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500



if __name__ == '__main__':
    app.run(debug=debug,port=3000)