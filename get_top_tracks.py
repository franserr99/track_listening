import os, sys, spotipy,cache_util, requests, datetime, pytz
from  dotenv import load_dotenv
from spotipy.oauth2 import SpotifyOAuth
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

#this assumes that the db is already up and running, prior to this a script has been run to seed the database and create the structure for it 
def main(): 
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
    
    #print(os.environ) debugging purposes 
    oauth=SpotifyOAuth(scope=scope)
    sp=spotipy.Spotify(auth_manager=oauth)
    get_top_tracks(sp)
    
def get_top_tracks(client:spotipy.Spotify ): 
    #get the idx w corresponding track name & artist for each near-term
    short_term_tracks=client.current_user_top_tracks(20,offset=0,time_range= "short_term" )
    #init near-term meta data, process data for each term
    st_track_idx,st_tracks_name, st_artist_names=get_tracks_info(short_term_tracks)
    if(short_term_tracks['next']): 
        paginate_results(short_term_tracks, st_track_idx, st_tracks_name, st_artist_names)
    middle_term_tracks=client.current_user_top_tracks(20,offset=0,time_range= "middle_term" )
    mt_track_idx,mt_tracks_name, mt_artist_names=get_tracks_info(middle_term_tracks)
    if(middle_term_tracks['next']): 
        paginate_results(middle_term_tracks, mt_track_idx, mt_tracks_name, mt_artist_names)
    long_term_tracks=client.current_user_top_tracks(20,offset=0,time_range="long_term" )
    lt_track_idx,lt_tracks_name, lt_artist_names=get_tracks_info(long_term_tracks)
    if(long_term_tracks['next']): 
        paginate_results(long_term_tracks, lt_track_idx, lt_tracks_name, lt_artist_names)
    #get unique track
    unique_track_idx=[]
    #unique in context of for each unique id
    unique_track_artists=[] 
    unique_track_names=[]
    #init the iterables w/ short-term
    unique_track_idx.extend(st_track_idx)
    unique_track_artists.extend(st_artist_names)
    unique_track_names.extend(st_tracks_name)
    #middle-term, then longterm
    for track, i in enumerate(mt_track_idx):
        if track not in unique_track_idx:
            unique_track_idx.append(track)
            unique_track_artists.append(mt_artist_names[i])
            unique_track_names.append(mt_tracks_name[i])
    for track, i in enumerate(lt_track_idx):
        if track not in unique_track_idx:
            unique_track_idx.append(track)
            unique_track_artists.append(lt_artist_names[i])
            unique_track_names.append(lt_tracks_name[i])
    assert(len(unique_track_idx)==len(unique_track_artists)==len(unique_track_names))

    now= datetime.datetime.now(pytz.timezone('US/Pacific')).strftime('%Y-%m-%d %H:%M:%S')
    #part one: done
    #part two: connect to the my database and store it
    user=os.environ['user']
    pw=os.environ['password']
    port=os.environ['port']
    connector_str='mysql+mysqlconnector://'+user+':'+ pw+ '@localhost:'+ port+'/test_DB'
    engine=create_engine(connector_str)

    #check to see if the database contains the spotify id of the client 


    








    

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

