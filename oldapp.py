@app.route('/results', methods=["GET", "POST"])
def results():
    db_to_favorites()

    # Getting user ID to create a playlist
    user_id = session['user_name']
    create_playlist()

    search_bid = json.loads(request.form.get('ids'))


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
    count = 0
    for i in track_id:
        while (count < 10):
            add_song(playlist_id, i)
            count = count + 1



    spotify_player_source = "https://embed.spotify.com/?uri=spotify%3Auser%3A" + user_id + "%3Aplaylist%3A{}".format(quote(playlist_id))


    def images(name):
        try:
            get_image = requests.get("http://api.bandsintown.com/artists/" +  quote(name, safe='') + ".json?api_version=2.0&app_id=YOUR_APP_ID")
            get_image = get_image.json()['image_url']
        except (json.decoder.JSONDecodeError, KeyError) as e:
            return "https://s3.amazonaws.com/bit-photos/artistLarge.jpg"
        return get_image

    first_artist = {}
    for s in search_bid:
        first_artist.update({s['id']:images(s['artists'][0]['name'])})