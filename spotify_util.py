import os, sys, spotipy,cache_util, requests, datetime, pytz, sqlalchemy
import pandas as pd
from  dotenv import load_dotenv
from spotipy.oauth2 import SpotifyOAuth
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker
from database_mgmt import db_util

#this assumes that the db is already up and running, prior to this a script has been run to seed the database and create the structure for it 
def main(): 
    
    oauth, client=init_client()
    get_top_tracks(client=client)
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
    after=db_util.user_util.users_list(engine=engine)
    #did testing stage by stage of the flow
    #print(after)
    #sys.exit(0)
def get_top_tracks(client:spotipy.Spotify):
    
    #how would i do this if they gave me access before? 
    
    engine = db_util.connection_util.connect_db()
    Session =sessionmaker(bind=engine)
    spotipy_id=client.me()['id']
    #check if the user is in the database already, if not, then create it 
    welcome_user(engine=engine,client=client)
    #get listening history for each near term 
    short_term_tracks=client.current_user_top_tracks(20,offset=0,time_range= "short_term" )
    st_track_idx,st_tracks_name, st_artist_names=get_tracks_info(short_term_tracks)
    if(short_term_tracks['next']): 
        paginate_results(short_term_tracks, st_track_idx, st_tracks_name, st_artist_names)
    middle_term_tracks=client.current_user_top_tracks(20,offset=0,time_range= "medium_term" )
    mt_track_idx,mt_tracks_name, mt_artist_names=get_tracks_info(middle_term_tracks)
    if(middle_term_tracks['next']): 
        paginate_results(middle_term_tracks, mt_track_idx, mt_tracks_name, mt_artist_names)
    long_term_tracks=client.current_user_top_tracks(20,offset=0,time_range="long_term" )
    lt_track_idx,lt_tracks_name, lt_artist_names=get_tracks_info(long_term_tracks)
    if(long_term_tracks['next']): 
        paginate_results(long_term_tracks, lt_track_idx, lt_tracks_name, lt_artist_names)

    shortterm= (st_track_idx,st_tracks_name, st_artist_names)
    midterm=(mt_track_idx,mt_tracks_name, mt_artist_names)
    longterm=(lt_track_idx,lt_tracks_name, lt_artist_names)

    #get unique tracks across all three terms 
    unique_track_idx=[]
    unique_track_artists=[] 
    unique_track_names=[]
    #init the iterables w/ short-term
    unique_track_idx.extend(st_track_idx)
    unique_track_artists.extend(st_artist_names)
    unique_track_names.extend(st_tracks_name)
    #middle-term, then longterm
    for i, track in enumerate(mt_track_idx):
        if track not in unique_track_idx:
            unique_track_idx.append(track)
            unique_track_artists.append(mt_artist_names[i])
            unique_track_names.append(mt_tracks_name[i])
    for i, track in enumerate(lt_track_idx):
        if track not in unique_track_idx:
            unique_track_idx.append(track)
            unique_track_artists.append(lt_artist_names[i])
            unique_track_names.append(lt_tracks_name[i])
    assert(len(unique_track_idx)==len(unique_track_artists)==len(unique_track_names))
    
    #add the songs not already present
    print(unique_track_idx)
    db_track_library_URIs=db_util.song_util.get_song_uris(engine=engine)
    
    new_db_tracks=[]
    new_db_track_names=[]
    new_db_artists_name=[]

    for i, track in enumerate(unique_track_idx):
        if track not in db_track_library_URIs:
            new_db_tracks.append(track)
            new_db_track_names.append(unique_track_names[i])
            new_db_artists_name.append(unique_track_artists[i])
    #the function takes care of doing audiofeatures as well 
    if (len (new_db_tracks)>0):
        db_util.song_util.add_songs(engine=engine,track_uris= new_db_tracks,track_names=new_db_track_names, track_artists=new_db_artists_name , client=client)
    #all the database relate stuff is done, i would like to add something more visual at the end, like something on the front end for the user 
    #come back to this later, need to do more brainstorming, lets fill in the rest for the database stuff 
    #what if the lists are empty? figure out more edge cases and handle them by making this conditional call
    #send listening data of each term to database
    db_util.history_util.push_history_data(records=shortterm,term='short_term', id=spotipy_id,engine=engine)
    db_util.history_util.push_history_data(records=midterm,term='medium_term', id=spotipy_id,engine=engine)
    db_util.history_util.push_history_data(records=longterm,term='long_term', id=spotipy_id,engine=engine)


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
        artists_name.append(artists) #get first artist associated with the song in the json obj
    assert(len(tracks_URI)==len(tracks_name)==len(artists_name))
    return tracks_URI, tracks_name, artists_name
        

if __name__=='__main__':
    main()

