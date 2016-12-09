from flask import Flask, render_template, request, redirect, url_for, jsonify, session
from flask_modus import Modus
import os
import requests
import sys
import spotipy
import spotipy.util as util
from flask_oauthlib.client import OAuth, OAuthException
import random
import string
from requests.utils import quote


OAUTH_TOKEN_URL = 'https://accounts.spotify.com/api/token'



SPOTIFY_APP_ID = os.environ.get('SPOTIPY_CLIENT_ID')
SPOTIFY_APP_SECRET = os.environ.get('SPOTIPY_CLIENT_SECRET')


app = Flask(__name__)
app.debug = True
app.secret_key = 'development'
oauth = OAuth(app)
modus = Modus(app)

SPOTIFY_CLIENT_ID = app.config['SPOTIFY_CLIENT_ID'] = os.environ.get('SPOTIFY_CLIENT_ID')
SPOTIFY_CLIENT_SECRET = app.config['SPOTIFY_CLIENT_SECRET'] = os.environ.get('SPOTIFY_CLIENT_SECRET')

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

    # Save some info to the DB
    return render_template("search.html")



@spotify.tokengetter
def get_spotify_oauth_token():
    return session.get('oauth_token')


@app.route('/add_playlist', methods=["GET"])
def add_playlist():
    return render_template("add_playlist")

# SPOTIFY API
def create_playlist():
    def random_name(size=8):
        chars = list(string.ascii_lowercase + string.digits)
        return ''.join(random.choice(chars) for _ in range(size))

    new_playlist = spotify.post("https://api.spotify.com/v1/users/localconcertradio/playlists/", data={"name": "Your Playlist"}, headers={'Accept': 'application/json', 'Content-Type': 'application/json'}, format='json')
    return render_template("results.html", new_playlist=new_playlist)


def search_artists(artist):
    return spotify.get("https://api.spotify.com/v1/search?q=" + quote(artist, safe='') + "&type=artist", headers={"Accept": 'application/json', "Authorization": "Bearer"})
    # artist.data['artists']['items'][0]['id']

def top_tracks(id):
    return spotify.get("https://api.spotify.com/v1/artists/" +  quote(id, safe='') +"/top-tracks?country=SE", headers={"Accept": 'application/json', "Authorization":"Bearer"})
    # gettop.data['tracks'][0]['id']

def add_song(song):
    return spotify.post("https://api.spotify.com/v1/users/localconcertradio/playlists/7hHbiDnoVzUYbEThUZ5H9W/tracks?position=0&uris=spotify%3Atrack%3A{}".format(quote(song)), headers={"Accept": 'application/json', "Authorization": "Bearer"}, format='json')
# quote("foo/bar/{}".format('greg').safe='')


def user_playlists():
   return spotify.get("https://api.spotify.com/v1/users/localconcertradio/playlists", headers={"Accept": 'application/json', "Authorization": "Bearer"})
    # userplaylists.data['items'][0]['id']


@app.route('/search', methods=["GET"])
def search():
    return render_template("search.html")
            
@app.route('/results', methods=["GET"])
def results():

    # Getting list from bands in town
    search_bid = requests.get("http://api.bandsintown.com/events/search?format=json&api_version=2.0&app_id=YOUR_APP_ID&date=" + request.args.get('search-date-start') + "," + request.args.get('search-date-end') + "&location=" + request.args.get('search-city') + "," + request.args.get('search-state') + "&radius=" + request.args.get('search-radius')).json()
    
    # creating a list of all the artists
    artist_names = []
    for s in search_bid:
        for x in s['artists']:
            artist_names.append(search_artists(x['name']).data)


    # getting id's from all the names
    artist_ids = []
    for i in artist_names:
        for x in i['artists']['items']:
            artist_ids.append(x['id'])


    # searching all artists given for top tracks
    obj_tracks = []
    for i in artist_ids:
        obj_tracks.append(top_tracks(i))


    # getting a list of one song each from each artists top tracks
    track_id = []
    for i in obj_tracks:
        for x in i.data['tracks']:
            track_id.append(x['id'])




 

    


    return render_template("results.html", search_bid=search_bid, artist_get=artist_get)





if __name__ == '__main__':
    app.run(debug=True,port=3000)