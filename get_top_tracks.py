import os, sys, time, spotipy, requests, cache_util
from cache_util import get_cached_token
from  dotenv import load_dotenv
from spotipy.oauth2 import SpotifyOAuth

def main(): 

    #the concepts of 

    load_dotenv("/Users/franserr/Documents/portfolio/spotify_usage/env_files/client.env")     #load env vars
    scope= "user-library-read user-read-playback-position user-top-read user-read-recently-played playlist-read-private"
    try: 
        #load_dotenv should load env var, now just check they exist in the enviorment
        os.environ["SPOTIPY_CLIENT_SECRET"] 
        os.environ['SPOTIPY_CLIENT_ID']
        os.environ["SPOTIPY_REDIRECT_URI"]
    except:
        print("one of these were not set as an enviormental variable, needed for successful execution")
        sys.exit(1) #use this instead of exit() bc it speaks to interpreter, not safe in prod env
    
    #print(os.environ) debugging purposes 
    oauth=SpotifyOAuth(scope=scope)
    sp=spotipy.Spotify(auth_manager=oauth)
    get_top_tracks(sp)




    
def get_top_tracks(client:spotipy.Spotify ): 

    tracks= []
    short_term_tracks=client.current_user_top_tracks(20,offset=0,time_range= "short_term" )
    st_track_idx,st_tracks_name, st_artist_names=get_tracks_info(short_term_tracks)
    if(short_term_tracks['next']): 
        paginate_results(short_term_tracks, st_track_idx, st_tracks_name, st_artist_names)
    print(short_term_tracks)
    print(st_track_idx)
    print(st_tracks_name)
    print(st_artist_names)
    sys.exit(1)

    middle_term_tracks=client.current_user_top_tracks(20,offset=0,time_range= "middle_term" )
    mt_track_idx,mt_tracks_name, mt_artist_names=get_tracks_info(middle_term_tracks)
    if(middle_term_tracks['next']): 
        paginate_results(middle_term_tracks, mt_track_idx, mt_tracks_name, mt_artist_names)
    long_term_tracks=client.current_user_top_tracks(20,offset=0,time_range="long_term" )

    lt_track_idx,lt_tracks_name, lt_artist_names=get_tracks_info(long_term_tracks)
    if(long_term_tracks['next']): 
        paginate_results(long_term_tracks, lt_track_idx, lt_tracks_name, lt_artist_names)


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
    
    
main()

