import os, sys, time, spotipy, requests
from  dotenv import load_dotenv
from spotipy.oauth2 import SpotifyOAuth
#okay i want to set it up so that i create it using the tools with spotipy 
# then i want to work backwards by creating my own services and strip away what i use in spotipy 

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
    short_term_tracks=client.current_user_top_tracks(20,offset=0,time_range= "short-term" )
    print(short_term_tracks)
    sys.exit(1)
    #check if you need to paginate for the short term
    middle_term_tracks=client.current_user_top_tracks(20,offset=0,time_range= "middle-term" )
    #check if you need to paginate for the middle term
    long_term_tracks=client.current_user_top_tracks(20,offset=0,time_range="long-term" )
    #check if you need to paginate for the long term
def paginate_results(tracks:dict, offset:int=0):
    


