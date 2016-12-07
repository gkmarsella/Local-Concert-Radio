from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_modus import Modus
import os
import requests

app = Flask(__name__)
api = Modus(app)

key = app.config['KEY'] = os.environ.get('KEY')
secret = app.config['SECRET'] = os.environ.get('SECRET')

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