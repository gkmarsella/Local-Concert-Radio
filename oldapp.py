@app.route('/results', methods=["GET"])
def results():

    # Getting list from bands in town
    search_bid = requests.get("http://api.bandsintown.com/events/search?format=json&api_version=2.0&app_id=YOUR_APP_ID&date=" + request.args.get('search-date-start') + "," + request.args.get('search-date-end') + "&location=" + request.args.get('search-city') + "," + request.args.get('search-state') + "&radius=" + request.args.get('search-radius')).json()

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


#-----------------------------------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------------------------------
    # Removing artist duplicates

    names_no_duplicates = []
    for i in artist_names:   
        if 'artists' in i and 'items' in i['artists']:
            for y in i['artists']['items']:
                if y not in names_no_duplicates:
                    names_no_duplicates.append(y)


    # removing all artists with 'featuring/presents' (which creates multiple duplicates if not filtered out)
    names_no_feat = []
    for i in names_no_duplicates:
        if 'feat.' not in i and 'presents' not in i and 'Presents' not in i and 'featuring' not in i:
            names_no_feat.append(i)


#-----------------------------------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------------------------------


    # getting id's from all the names
    artist_ids = {}
    for i in artist_names:
        if 'artists' in i and 'items' in i['artists']:
            for y in i['artists']['items']:
                artist_ids.append(y['id'])



    # searching all artists given for top tracks
    obj_tracks = []
    for i in artist_ids:
        obj_tracks.append(top_tracks(i))


    # getting a list of one song each from each artists top tracks
    track_id = []
    for i in obj_tracks:
        if 'tracks' in i.data and (len(i.data['tracks'])) > 0:
            track_id.append(i.data['tracks'][0]['id'])

    from IPython import embed; embed()

    # adding songs to playlist
    for i in track_id:
        add_song(playlist_id, i)

# feat., featuring, feat, 





    spotify_player_source = "https://embed.spotify.com/?uri=spotify%3Auser%3Alocalconcertradio%3Aplaylist%3A{}".format(quote(playlist_id))


    return render_template("results.html", search_bid=search_bid, spotify_player_source=spotify_player_source)