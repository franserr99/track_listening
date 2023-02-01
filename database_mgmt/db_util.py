from dotenv import load_dotenv
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
import os, sqlalchemy, spotipy, sys, datetime, pytz
def connect_db():
    load_dotenv("/Users/franserr/Documents/portfolio/spotify_usage/env_files/db.env")
    user=os.environ['user']
    pw=os.environ['password']
    port=os.environ['port']
    connector_str='mysql+mysqlconnector://'+user+':'+ pw+ '@localhost:'+ port+'/testing_DB'
    engine=create_engine(connector_str)







    return engine
def create_user():

    pass
def push_history_data(records:tuple): 
    now= datetime.datetime.now(pytz.timezone('US/Pacific')).strftime('%Y-%m-%d %H:%M:%S') 
    assert(len(records)==3), "expected number of features for record is three"



    #part two: connect to the my database and store it
    user=os.environ['user']
    pw=os.environ['password']
    port=os.environ['port']
    connector_str='mysql+mysqlconnector://'+user+':'+ pw+ '@localhost:'+ port+'/test_DB'
    engine=create_engine(connector_str)

    #check to see if the database contains the spotify id of the client 
    with engine.connect() as connection: 
        pass

def library_table(engine: sqlalchemy.engine.Engine, as_list:bool): 
    #will return different tuples depending on the paramters


    pass 
def history_table(engine: sqlalchemy.engine.Engine): 

    pass
def audio_feeature_table(engine: sqlalchemy.engine.Engine): 

    pass 
def users_table(engine: sqlalchemy.engine.Engine, as_list:bool):



    pass

def add_song(engine: sqlalchemy.engine.Engine, track_uri:str):
   
    pass
'''
flow:
    get the audio features for all the tracks 
        when finished processing all of them, there should be atleast ( think the code puts in 2 columns because i wanted to match it )
        one column where there is the URI (i also need to match this to what i am comparing to, because i might only have the spotify id )
    since the audiofeatures have their own uri part i should be able to push them completely independently from the tracks themselves 



'''
def add_songs(engine: sqlalchemy.engine.Engine, track_uris: list(str), client:spotipy.Spotify):



    for i in range (0, len(track_uris), 100): #break into 100 item chunks
        track_uris.append(track_uris[i:i+100])
    
    all_features=dict(client.audio_features(track_uris[0])[0])
    feature_column_names=list(all_features.keys())[:-7] #get numerical data
    feature_column_names.append('id') #keep a copy to make sure data lines up later

    songs_audio_features=[]
    #account for songs that dont have audio features
    all_bad_indices=[]

    for k, chunk in enumerate(track_uris):
        features=list(client.audio_features(chunk)) 
        print(features)
        print(len(chunk))
        sys.exit(1)
        assert(len(features)==len(chunk))
        if None in features: #clean up data 
            print(features)
            bad_indices=[]
            for i, v in enumerate(features): #get indicies of null values
                if(v is None):
                    print(i)
                    all_bad_indices.append(int(i+((k)*100))) #account for the partioning 
                    bad_indices.append(i) 
            for j in range (len(bad_indices)): #get rid of items in feature list that are null
                features.pop(bad_indices[j])    
        for song_features in features: #removed all nulls by now, dealing with only a list of dictionaries
            feats=[]
            for column_name in feature_column_names:
                feats.append(song_features[column_name])
            songs_audio_features.append(feats)

def get_song_uris(engine: sqlalchemy.engine.Engine):
    pass
#there might be different kind of information that we want to extract from it, will create functions for that when the time comes 

