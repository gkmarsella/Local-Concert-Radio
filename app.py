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

    spotify.post("https://api.spotify.com/v1/users/localconcertradio/playlists/", data={"name": random_name()}, headers={'Accept': 'application/json', 'Content-Type': 'application/json'}, format='json')

def search_artists():
    artist = request.args.get("something")
    spotify.get("https://api.spotify.com/v1/search?q=Radiohead&type=artist", headers={"Accept": 'application/json', "Authorization": "Bearer"})
    # artist.data['artists']['items'][0]['id']

def top_tracks():
    spotify.get("https://api.spotify.com/v1/artists/4Z8W4fKeB5YxbusRsdQVPb/top-tracks?country=SE", headers={"Accept": 'application/json', "Authorization":"Bearer"})
    # gettop.data['tracks'][0]['id']

def add_song():
    spotify.post("https://api.spotify.com/v1/users/localconcertradio/playlists/7hHbiDnoVzUYbEThUZ5H9W/tracks?position=0&uris=spotify%3Atrack%3A2pXpURmn6zC5ZYDMms6fwa", headers={"Accept": 'application/json', "Authorization": "Bearer"}, format='json')

def user_playlists():
    spotify.get("https://api.spotify.com/v1/users/localconcertradio/playlists", headers={"Accept": 'application/json', "Authorization": "Bearer"})
    # userplaylists.data['items'][0]['id']


@app.route('/search', methods=["GET"])
def search():
    return render_template("search.html")
            
@app.route('/results', methods=["GET"])
def results():
    # search_artist = requests.get("http://api.bandsintown.com/artists/" + request.args.get('search-artist')  + "/events.json?api_version=2.0&app_id=local_radio").json()

    # search_dict = {"date": request.args.get('search-start-date') + "," + request.args.get('search-date-end'), "location": request.args.get('search-city') + "," + request.args.get('search-state'), "radius": request.args.get('search-radius')}
    search_test = requests.get("http://api.bandsintown.com/events/search?format=json&api_version=2.0&app_id=YOUR_APP_ID&date=" + request.args.get('search-date-start') + "," + request.args.get('search-date-end') + "&location=" + request.args.get('search-city') + "," + request.args.get('search-state') + "&radius=" + request.args.get('search-radius')).json()
    # search_location = requests.get("http://api.bandsintown.com/events/search?format=json&api_version=2.0&app_id=YOUR_APP_ID", params=search_dict).json()
    return render_template("results.html", search_test=search_test)





if __name__ == '__main__':
    app.run(debug=True,port=3000)