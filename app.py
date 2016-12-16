from flask import Flask, render_template, request, redirect, url_for, jsonify, session
from flask_modus import Modus
from flask_sqlalchemy import SQLAlchemy
import os
import requests
from flask_oauthlib.client import OAuth, OAuthException
import random
import string
from requests.utils import quote
import json



OAUTH_TOKEN_URL = 'https://accounts.spotify.com/api/token'



app = Flask(__name__)
app.debug = True
app.secret_key = 'development'
oauth = OAuth(app)
modus = Modus(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://localhost/local-playlist'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'secret'
db = SQLAlchemy(app)
SPOTIFY_CLIENT_ID = app.config['SPOTIFY_CLIENT_ID'] = os.environ.get('SPOTIFY_CLIENT_ID')
SPOTIFY_CLIENT_SECRET = app.config['SPOTIFY_CLIENT_SECRET'] = os.environ.get('SPOTIFY_CLIENT_SECRET')

# ************************************************************************************************************************
#                                                       DATABASE        
# ************************************************************************************************************************


class User(db.Model):


    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    user_name = db.Column(db.Text)
    user_email = db.Column(db.Text)


    def __init__(self, user_name, user_email):
        self.user_name = user_name
        self.user_email = user_email


    def __repr__(self):
        return "The user's name and email is {} {}".format(self.user_name, self.user_email)


class Genres(db.Model):

    __tablename__ = "genres"

    id = db.Column(db.Integer, primary_key=True)
    genre = db.Column(db.Text)

    def __init__(self, genre):
        self.genre = genre


class Artists(db.Model):

    __tablename__ = "artists"

    id = db.Column(db.Integer, primary_key=True)
    artist = db.Column(db.Text)

    def __init__(self, artist):
        self.artist = artist



class Events(db.Model):

    __tablename__ = "events"

    id = db.Column(db.Integer, primary_key=True)
    event = db.Column(db.Text)

    def __init__(self, event):
        self.event = event


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


UserEvents = db.Table('user_events',
                    db.Column('id',
                        db.Integer,
                        primary_key=True),
                    db.Column('user_id',
                        db.Integer,
                        db.ForeignKey('users.id', ondelete="cascade")),
                    db.Column('event_id',
                        db.Integer,
                        db.ForeignKey('events.id', ondelete="cascade")))




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
    request_token_params={'scope': 'user-read-private user-read-email'},
    base_url='https://accounts.spotify.com',
    request_token_url=None,
    access_token_url='/api/token',
    authorize_url='https://accounts.spotify.com/authorize'
)


@app.route('/')
def index():
    return redirect(url_for('login'))


@app.route('/login')
def login():
    callback = url_for(
        'spotify_authorized',
        next=request.args.get('next') or request.referrer or None,
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
    me = spotify.get('/me')

    user_id = spotify.get("https://api.spotify.com/v1/me").data

    if User.query.filter_by(user_name=user_id['id']).first() is None:
        user_id['id'] = User(user_id['id'], user_id['email'])
        db.session.add(user_id['id'])
        db.session.commit()

    # Save some info to the DB
    return render_template("search.html")



@spotify.tokengetter
def get_spotify_oauth_token():
    return session.get('oauth_token')



# user_id = spotify.get("https://api.spotify.com/v1/me").data 

# if user_id['id'] not in User.user_name:
#     user_id['id'] = User(user_id['id'], user_id['email'])


# ************************************************************************************************************************
#                                                       SPOTIFY        
# ************************************************************************************************************************





def create_playlist():

    def random_name(size=8):
        chars = list(string.ascii_lowercase + string.digits)
        return ''.join(random.choice(chars) for _ in range(size))

    user_id = spotify.get("https://api.spotify.com/v1/me").data['id']

    new_playlist = spotify.post("https://api.spotify.com/v1/users/"+  quote(user_id, safe='')  +"/playlists/", data={"name": "Your Playlist"}, headers={'Accept': 'application/json', 'Content-Type': 'application/json'}, format='json')
    return render_template("results.html", new_playlist=new_playlist)


def search_artists(artist):
    return spotify.get("https://api.spotify.com/v1/search?q=" + quote(artist, safe='') + "&type=artist", headers={"Accept": 'application/json', "Authorization": "Bearer"})
    # artist.data['artists']['items'][0]['id']

def top_tracks(id):
    return spotify.get("https://api.spotify.com/v1/artists/" +  quote(id, safe='') +"/top-tracks?country=SE", headers={"Accept": 'application/json', "Authorization":"Bearer"})
    # gettop.data['tracks'][0]['id']

def add_song(playlist, song):

    user_id = spotify.get("https://api.spotify.com/v1/me").data['id']

    return spotify.post("https://api.spotify.com/v1/users/" +  quote(user_id, safe='')  + "/playlists/" +  quote(playlist, safe='') + "/tracks?position=0&uris=spotify%3Atrack%3A{}".format(quote(song)), headers={"Accept": 'application/json', "Authorization": "Bearer"}, format='json')
# quote("foo/bar/{}".format('greg').safe='')


def user_playlists():
    user_id = spotify.get("https://api.spotify.com/v1/me").data['id']

    return spotify.get("https://api.spotify.com/v1/users/" +  quote(user_id, safe='')  + "/playlists", headers={"Accept": 'application/json', "Authorization": "Bearer"})
    # userplaylists.data['items'][0]['id']


# ************************************************************************************************************************
#                                               REQUESTS
# ************************************************************************************************************************

@app.route('/search', methods=["GET"])
def search():
    return render_template("search.html")

@app.route('/sort', methods=["GET"])
def sort():
    search_bands = requests.get("http://api.bandsintown.com/events/search?format=json&api_version=2.0&app_id=YOUR_APP_ID&date=" + request.args.get('search-date-start') + "," + request.args.get('search-date-end') + "&location=" + request.args.get('search-city') + "," + request.args.get('search-state') + "&radius=" + request.args.get('search-radius')).json()

    def images(name):
        get_image =  requests.get("http://api.bandsintown.com/artists/" +  quote(name, safe='') + ".json?api_version=2.0&app_id=YOUR_APP_ID").json()['image_url']
        return get_image

    first_artist = {}
    for s in search_bands:
        first_artist.update({s['id']:images(s['artists'][0]['name'])})


    return render_template("sort.html", search_bands=search_bands, first_artist=first_artist, search_data=json.dumps(search_bands))


@app.route('/results', methods=["GET", "POST"])
def results():
    user_id = spotify.get("https://api.spotify.com/v1/me").data['id']
    # Getting list from bands in town
    # BEFORE SORT
    # search_bid = requests.get("http://api.bandsintown.com/events/search?format=json&api_version=2.0&app_id=YOUR_APP_ID&date=" + request.args.get('search-date-start') + "," + request.args.get('search-date-end') + "&location=" + request.args.get('search-city') + "," + request.args.get('search-state') + "&radius=" + request.args.get('search-radius')).json()
    # AFTER SORT
    search_bid = json.loads(request.form.get('ids'))

    # Creating a new playlist
    create_playlist()


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




    # removing all artists with 'featuring/presents' (which creates multiple duplicates if not filtered out)
    names_no_feat = {k:v for k,v in artist_dict.items() if 'feat' not in k.lower() or 'presents' not in k.lower() or 'feat.' not in k.lower or 'featuring' not in k.lower()}


    # removing duplicate names


# {k:v for k,v in artist_dict2.items() if k in sorted([k for k,v in artist_dict2.items()])}

    # searching all artists given for top tracks
    obj_tracks = []
    for i in names_no_feat.values():
        obj_tracks.append(top_tracks(i))


    # getting a list of one song each from each artists top tracks
    track_id = []
    for i in obj_tracks:
        if 'tracks' in i.data and (len(i.data['tracks'])) > 0:
            track_id.append(i.data['tracks'][0]['id'])

    # adding songs to playlist
    for i in track_id:
        add_song(playlist_id, i)



    spotify_player_source = "https://embed.spotify.com/?uri=spotify%3Auser%3A" + user_id + "%3Aplaylist%3A{}".format(quote(playlist_id))


    return render_template("results.html", search_bid=search_bid, spotify_player_source=spotify_player_source)


if os.environ.get('ENV') == 'production':
    debug = False

else:
    debug = True




if __name__ == '__main__':
    app.run(debug=debug,port=3000)