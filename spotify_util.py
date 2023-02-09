import os, sys, spotipy, requests, datetime, pytz, sqlalchemy, email_util
import pandas as pd
from  dotenv import load_dotenv
from spotipy.oauth2 import SpotifyOAuth
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker
import db_util, cache_util
#this assumes that the db is already up and running, prior to this a script has been run to seed the database and create the structure for it 
def main(): 
    
    oauth, client=init_client()
    this_month_tracks=get_top_tracks(client=client)
    
    tracks_id=this_month_tracks[0]
    tracks_name=this_month_tracks[1]
    tracks_artists=this_month_tracks[2]
    #filter the songs by artists
    artist_dict={}
    for k ,track_artists in enumerate(tracks_artists):
        artists=track_artists.split(",")
        for creator in artists:
            cre=str(creator.strip())
            if cre not in artist_dict: #the list as a value for the key:value pairing does not exist yet
                artist_dict[cre]=[]
            artist_dict[cre].append(k)
    #by the end of this, every artist should have a list associated with the songs they are in 

    all_artists=artist_dict.keys()
    if len(artist_dict)<=6:
        #all artists are already your top artists 
        top_artists=all_artists
    else :
        top_artists=[]
        for creator in artist_dict.keys():
            top_artists.append(creator)
            if len (top_artists)==6:
                break
    #top artist by how many of their songs are in the api results 
    for artist in all_artists:
        appearances=len(artist_dict[artist])
        #if it appears more times than any of the four artists already in there, 
        #then replace the first time bigger fish found but check all of them if necessary
        for k ,top_artist in enumerate(top_artists):
            if appearances>len(artist_dict[top_artist]): 
                top_artists[k]=artist
                break
    

    
    print(top_artists)
    message_body=''
    message_body+='Hello,\nHere is the breakdown of your listening history for around the last month: \n'
    message_body+='\n Your favorite artists were:\n '
    for artist in top_artists:
        message_body+='\t'+ artist+ '\n'

    message_body+='\n\n'
    message_body+='Your top tracks for the last month have been:\n'

    for k,track in enumerate(tracks_name): 
        message_body+=' \t'+ track+ ', by  ' + tracks_artists[k] +'\n'
    print(message_body)

    email_util.email_util.send(message_body=message_body)


def init_client(): 
    load_dotenv("/Users/franserr/Documents/portfolio/spotify_usage/env_files/client.env")     #load env vars
    load_dotenv("/Users/franserr/Documents/portfolio/spotify_usage/env_files/db.env")
    scope= "user-library-read user-read-playback-position user-top-read user-read-recently-played playlist-read-private"
    #now= datetime.datetime.now(tz=pytz.timezone('US/Pacific'))
    #now=now.strftime('%Y-%m-%d %H:%M:%S')
    try: 
        #load_dotenv should load env var, now just check they exist in the enviorment
        os.environ["SPOTIPY_CLIENT_SECRET"] 
        os.environ['SPOTIPY_CLIENT_ID']
        os.environ["SPOTIPY_REDIRECT_URI"]
        os.environ['user']
        os.environ['password']
        os.environ['port']
    except:
        print("one of these were not set as an enviormental variable, needed for successful execution")
        sys.exit(1) #use this instead of exit() bc it speaks to interpreter, not safe in prod env
    oauth=SpotifyOAuth(scope=scope)
    sp=spotipy.Spotify(auth_manager=oauth)
    return oauth, sp

'''
flow: 
    check to see if user is present in database 
        if not, add the user
    get the top songs across the three different near-terms 
    push the historical listening data of the three sets
    get unique songs across all three 
    find the songs not already in the database library and push those 
'''
def welcome_user(engine: sqlalchemy.engine.Engine, client:spotipy.Spotify): 
    spotipy_id=client.me()['id']
    db_sp_id=db_util.user_util.user_id_list(engine=engine)
    if spotipy_id not in db_sp_id: 
        db_util.user_util.create_user(spotipy_id, engine)
def get_top_tracks(client:spotipy.Spotify):
    engine = db_util.connection_util.connect_db()
    Session =sessionmaker(bind=engine)
    spotipy_id=client.me()['id']
    welcome_user(engine=engine,client=client)
    track_dict=client.current_user_top_tracks(20,offset=0,time_range= "short_term" )
    shortterm=get_tracks_info(track_dict)
    if(track_dict['next']): 
        paginate_results(track_dict, shortterm[0], shortterm[1], shortterm[2])
    track_dict=client.current_user_top_tracks(20,offset=0,time_range= "medium_term" )
    midterm=get_tracks_info(track_dict)
    if(track_dict['next']): 
        paginate_results(track_dict, midterm[0], midterm[1], midterm[2])
    track_dict=client.current_user_top_tracks(20,offset=0,time_range= "long_term")
    longterm=get_tracks_info(track_dict)
    if(track_dict['next']): 
        paginate_results(track_dict, longterm[0], longterm[1], longterm[2])
    #id, name, artist: structure of the tuple returned 
    #init the iterables w/ short-term
    unique_track_idx=shortterm[0][:]
    unique_track_names=shortterm[1][:]
    unique_track_artists=shortterm[2][:]
    #middle-term, then longterm
    for i, track in enumerate(midterm[0]):
        if track not in unique_track_idx:
            unique_track_idx.append(track)
            unique_track_artists.append(midterm[2][i])
            unique_track_names.append(midterm[1][i])
    for i, track in enumerate(longterm[0]):
        if track not in unique_track_idx:
            unique_track_idx.append(track)
            unique_track_artists.append(longterm[2][i])
            unique_track_names.append(longterm[1][i])
    assert(len(unique_track_idx)==len(unique_track_artists)==len(unique_track_names))
    db_util.song_util.add_songs(engine=engine,track_uris= unique_track_idx,track_names=unique_track_names, track_artists=unique_track_artists , client=client)
    db_util.history_util.push_history_data(records=shortterm,term='short_term', id=spotipy_id,engine=engine)
    db_util.history_util.push_history_data(records=midterm,term='medium_term', id=spotipy_id,engine=engine)
    db_util.history_util.push_history_data(records=longterm,term='long_term', id=spotipy_id,engine=engine)
    return shortterm

def paginate_results(tracks:dict, idx:list, track_names:list, artist_names:list):
    type, access_token = cache_util.get_auth_info()
    while(tracks['next']):
        tracks= requests.get(tracks['next'], headers={ 'Authorization': type+" "+access_token }).json()
        more_idx, more_track_names,more_artist_names= get_tracks_info(tracks)
        idx.extend(more_idx)
        track_names.extend(more_track_names)
        artist_names.extend(more_artist_names)
def get_tracks_info(tracks:dict):
    tracks_URI=[]
    tracks_name=[]
    artists_name=[]
    for item in tracks['items']:
        tracks_URI.append(item['uri'])
        tracks_name.append(item['name'])
        artists=''
        n=len(item['artists'])
        for i in range (n):
            artists+=item['artists'][i]['name']
            if(i<=n-2):
                artists+=', '
        artists_name.append(artists) 
    

    assert(len(tracks_URI)==len(tracks_name)==len(artists_name))
    return tracks_URI, tracks_name, artists_name
def extract_info(client:spotipy.Spotify, playlistIDs:list):  
    all_tracks_IDX=[]
    all_track_names=[]
    all_track_artists=[]

    for id in playlistIDs:
        count_IDX= len(all_tracks_IDX)
        count_names=len(all_track_names)
        count_artists=(len(all_track_artists))
        
        tracks=client.playlist_tracks(id)
        tracks_IDX, tracks_name, artist_names=get_tracks_info_playlist_route(tracks)
        all_tracks_IDX.extend(tracks_IDX)
        all_track_names.extend(tracks_name)
        all_track_artists.extend(artist_names)

        while(tracks['next']): #go through remaining pages if any exist
            token=dict(cache_util.get_cached_token())
            tracks=requests.get(tracks['next'], headers={"Authorization":  token['token_type']+" "+token['access_token']}).json()
            tracks_IDX, tracks_name, artist_names=get_tracks_info_playlist_route(tracks)
            all_tracks_IDX.extend(tracks_IDX)
            all_track_names.extend(tracks_name)
            all_track_artists.extend(artist_names)
        
        count_IDX_after_playlist= len(all_tracks_IDX)
        count_names_after_playlist=len(all_track_names)
        count_artist_after_playlist= (len(all_track_artists))
        assert (tracks['total']==(count_IDX_after_playlist-count_IDX)== (count_names_after_playlist-count_names )== (count_artist_after_playlist-count_artists))
    return all_tracks_IDX,all_track_names,all_track_artists
def get_tracks_info_playlist_route(tracks:dict):
    tracks_URI=[]
    tracks_name=[]
    artists_name=[]
    for item in tracks['items']:
        print(item)
        tracks_URI.append(item['track']['uri'])
        tracks_name.append(item['track']['name'])
        artists_name.append(item['track']['artists'][0]['name']) #get first artist associated with the song in the json obj
    assert(len(tracks_URI)==len(tracks_name)==len(artists_name))
    return tracks_URI, tracks_name, artists_name
def begin_rec_flow(client:spotipy.Spotify, oauth:SpotifyOAuth):  
    potential_seed_playlists_IDX=[]
    user_created_playlists_IDX=[]
    playlists=client.current_user_playlists()
    for playlist in playlists['items']:
        if playlist['owner']['id'] !=client.me()['id']:
            print("playlist with ID"+ playlist['owner']['id']+" is going into the potential seed tracks")
            potential_seed_playlists_IDX.append(playlist['id'])            
        else: 
            user_created_playlists_IDX.append(playlist['id'])
    
    potential_tracks_IDX,potential_track_names,potential_track_artists= extract_info(client=client, playlistIDs= potential_seed_playlists_IDX)
    user_playlist_tracks_IDX,user_playlist_track_names,user_playlist_track_artists= extract_info(client=client, playlistIDs= potential_seed_playlists_IDX)
    
    engine=db_util.connection_util.connect_db()
    #add the songs and push the data we got to corresponding tables
    db_util.song_util.add_songs(engine=engine, track_uris=potential_tracks_IDX,track_names=potential_track_names, track_artists=potential_track_artists, client=client)
    db_util.song_util.add_songs(engine=engine, track_uris=user_playlist_tracks_IDX,track_names=user_playlist_track_names, track_artists=user_playlist_track_artists, client=client)
    db_util.rec_util.push_pontential_recs(engine=engine, track_IDs=potential_tracks_IDX,user=client.me()['id'])
    db_util.seed_util.push_seeds(engine=engine, track_IDs=user_playlist_tracks_IDX,user=client.me()['id'])
    #come back to this later when you learned more about reccomender systems
if __name__=='__main__':
    main()

