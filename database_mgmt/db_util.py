from dotenv import load_dotenv
from sqlalchemy.orm import sessionmaker
import os, sqlalchemy, spotipy, sys, datetime, pytz
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, DateTime, FLOAT, PrimaryKeyConstraint
from sqlalchemy.ext.declarative import declarative_base




class connection_util:
    def connect_db():
        load_dotenv("/Users/franserr/Documents/portfolio/spotify_usage/env_files/db.env")
        user=os.environ['user']
        pw=os.environ['password']
        port=os.environ['port']
        connector_str='mysql+mysqlconnector://'+user+':'+ pw+ '@localhost:'+ port+'/testing_DB'
        engine=create_engine(connector_str)
        return engine
class user_util:
    def create_user(id: str, engine: sqlalchemy.engine.Engine  ):
        print("user being created")
        base=declarative_base()
        Session = sessionmaker(bind=engine)
        session = Session()
        class users(base): #keep a high level users table in order to expand this another way if you want to later
            __tablename__='users'
            id = Column(String(50), primary_key=True, unique=True)
        try:
            new_user=users(id=id)
            session.add(new_user)
            session.commit() 
        finally:
            session.close()
    def users_list(engine: sqlalchemy.engine.Engine):
        base=declarative_base()
        Session = sessionmaker(bind=engine)
        session = Session()
        
        class users(base): #keep a high level users table in order to expand this another way if you want to later
            __tablename__='users'
            id = Column(String(50), primary_key=True, unique=True)
        try:
            user_list= session.query(users).all()  
            #returns a list of user objects, access the field of each one and check for the id     
            return user_list
        finally:
            session.close()
    def user_id_list(engine: sqlalchemy.engine.Engine):
        users=user_util.users_list(engine=engine)
        IDs=[]
        for user in users:
            IDs.append(user.id)
        return IDs

class history_util:
    @staticmethod
    def push_history_data(records:tuple, term:str, id:str,engine: sqlalchemy.engine.Engine): #an example of expected tuple:near_term= (track_idx,tracks_name,artist_names)
        assert(term==('short_term' or 'medium_term' or 'long_term' )) 
        #recall: the history table has the following fields: user_id, date_recorded, relative_term, track_id
        track_idx= records[0] #list of track ids
        tracks_name= records[1] #list of corresponding track names
        artist_names=records[2] #list of corresponding artist names
        now= datetime.datetime.now(pytz.timezone('US/Pacific')).strftime('%Y-%m-%d %H:%M:%S') #the timestamp used for all the records we are going to push right now 
        assert(len(track_idx)==len(tracks_name)==len(artist_names))
        base=declarative_base()
        Session = sessionmaker(bind=engine)
        session = Session()
        class users(base): #keep a high level users table in order to expand this another way if you want to later
            __tablename__='users'
            id = Column(String(50), primary_key=True, unique=True)
        class track_library(base):
            __tablename__='library'
            uri= Column(String(26),primary_key=True, unique=True)
            track_name=Column(String(100))
            track_artists=Column(String(100))
        class listening_history(base):
            __tablename__='history'
            user_id = Column(String(50),ForeignKey('users.id'), primary_key=True)
            date_recorded=Column(DateTime)
            relative_term=Column(String(30), primary_key=True)
            track_id= Column (String(26) , ForeignKey('library.uri'), primary_key=True, unique=False)
            __table_args__ = (PrimaryKeyConstraint('user_id', 'relative_term', 'track_id'),)
        try:
            for track_ID  in track_idx :
                #create an instance of the obj
                session.add(listening_history(user_id=id, date_recorded= now, relative_term=term, track_id= track_ID))
                session.commit()
        finally:
            session.close()   
    @staticmethod
    def get_listening_history(engine: sqlalchemy.engine.Engine, music_id:str): 
        #check to see if the database contains the spotify id of the client 
        base=declarative_base()
        Session = sessionmaker(bind=engine)
        session = Session()
        #make model that represents the table
        class users(base): #keep a high level users table in order to expand this another way if you want to later
            __tablename__='users'
            id = Column(String(50), primary_key=True, unique=True)
        class track_library(base):
            __tablename__='library'
            uri= Column(String(26),primary_key=True, unique=True)
            track_name=Column(String(100))
            track_artists=Column(String(100))
        class listening_history(base):
            __tablename__='history'
            user_id = Column(String(50),ForeignKey('users.id'), primary_key=True)
            date_recorded=Column(DateTime)
            relative_term=Column(String(30), primary_key=True)
            track_id= Column (String(26) , ForeignKey('library.uri'), primary_key=True)
            __table_args__ = (PrimaryKeyConstraint('user_id', 'relative_term', 'track_id'),)
        #i want to reference 
        try:
            history=session.query(listening_history).filter(listening_history.user_id==music_id).all()
            return history
        finally:
            session.close()
    @staticmethod
    def get_listening_history_by_term(engine: sqlalchemy.engine.Engine, music_id:str, term:str): 
        assert(term==('short_term' or 'middle_term' or 'long_term' ))
        base=declarative_base()
        Session = sessionmaker(bind=engine)
        session = Session()
        #make model that represents the table
        class users(base): #keep a high level users table in order to expand this another way if you want to later
            __tablename__='users'
            id = Column(String(50), primary_key=True, unique=True)
        class track_library(base):
            __tablename__='library'
            uri= Column(String(26),primary_key=True, unique=True)
            track_name=Column(String(100))
            track_artists=Column(String(100))
        class listening_history(base):
            __tablename__='history'
            user_id = Column(String(50),ForeignKey('users.id'), primary_key=True)
            date_recorded=Column(DateTime)
            relative_term=Column(String(30), primary_key=True)
            track_id= Column (String(26) , ForeignKey('library.uri'), primary_key=True)
            __table_args__ = (PrimaryKeyConstraint('user_id', 'relative_term', 'track_id'),)
        try:
            history=session.query(listening_history).filter(listening_history.user_id==music_id).filter(listening_history.relative_term).all()
            return history
        finally:
            session.close()
    @staticmethod
    def get_most_recent_history(): 
        pass
class song_util:
    @staticmethod
    def add_song(engine: sqlalchemy.engine.Engine, track_uri:str, track_name:str, track_artist:str):
        base=declarative_base()
        Session = sessionmaker(bind=engine)
        session = Session()
        #you could use the context manager (ie with Session() as session) but if a database error occurs it wont close the session
        class track_library(base):
            __tablename__='library'
            uri= Column(String(26),primary_key=True, unique=True)
            track_name=Column(String(100))
            track_artists=Column(String(100))
        #later switch to a with Session.begin() as session: because it will commit and close transaction and rollback and changes 
        #right now i still need control over the commit method 

        try: 
            session.add(track_library(uri=track_uri, track_name=track_name, track_artists=track_artist) )
            session.commit()
        finally:
            session.close()
            print('an error occured within the add_song method')
    '''
    flow:
        get the audio features for all the tracks 
            when finished processing all of them, there should be atleast ( think the code puts in 2 columns because i wanted to match it )
            one column where there is the URI (i also need to match this to what i am comparing to, because i might only have the spotify id )
        since the audiofeatures have their own uri part i should be able to push them completely independently from the tracks themselves 

    '''
    @staticmethod
    def add_songs(engine: sqlalchemy.engine.Engine, track_uris: list, track_names:list, track_artists:list, client:spotipy.Spotify):
        #PART ONE: add to the track library 
        base=declarative_base()
        Session = sessionmaker(bind=engine)
        session = Session()
        class track_library(base):
            __tablename__='library'
            uri= Column(String(26),primary_key=True, unique=True)
            track_name=Column(String(100))
            track_artists=Column(String(100))
        try:    
            for i, track in enumerate(track_uris):
                session.add(track_library(uri=track, track_name=track_names[i], track_artists=track_artists[i]))
                session.commit()
        finally:
            session.close()
        #PART TWO: add the features to the library
        partitioned_list=[] 
        trackIDX=track_uris
        #prep data: break into 100 item chunks,assuming that we are dealing w alot of tracks off bat
        for i in range (0, len(trackIDX), 100): 
            partitioned_list.append(trackIDX[i:i+100])
        all_features=dict(client.audio_features(partitioned_list[0])[0])
        #get numerical data
        feature_column_names=list(all_features.keys())[:-7] 
        #this line might need to get taken out? 
        feature_column_names.append('uri') #keep a copy to make sure data lines up later
        songs_audio_features=[]
        #account for songs that dont have audio features
        all_bad_indices=[]
        for k, chunk in enumerate(partitioned_list):
            features=list(client.audio_features(chunk)) 
            assert(len(features)==len(chunk))
            #clean up data 
            if None in features: 
                print(features)
                bad_indices=[]
                #get indicies of null values
                for i, v in enumerate(features): 
                    if(v is None):
                        #account for the partioning 
                        all_bad_indices.append(int(i+((k)*100))) 
                        bad_indices.append(i) 
                #get rid of items in feature list that are null
                for j in range (len(bad_indices)): 
                    features.pop(bad_indices[j])    
            #removed all nulls by now, dealing with only a list of dictionaries
            for song_features in features:
                feats=[]
                for column_name in feature_column_names:
                    feats.append(song_features[column_name])
                print(feats)
                songs_audio_features.append(feats)
        #element in song_audio_features is a list containing all the features and info for a given track: a list of lists 
        #create the model to represent the table
        class audio_features(base):
            __tablename__='audio_features'
            #example audiofeature (numerical portions of what gets returned)
            #danceability': 0.232, 'energy': 0.441, 'key': 10, 'loudness': -14.604, 'mode': 1,
            #'speechiness': 0.0452, 'acousticness': 0.135, 'instrumentalness': 0.0441, 'liveness': 0.668, 
            #'valence': 0.237, 'tempo': 147.655
            track_id = Column(String(26), ForeignKey('library.uri'), unique=True,primary_key=True )
            danceability= Column(FLOAT)
            energy=Column(FLOAT)
            key=Column(FLOAT)
            loudness=Column(FLOAT)
            mode=Column(FLOAT)
            speechiness=Column(FLOAT)
            acousticness=Column(FLOAT)
            instrumentalness=Column(FLOAT)
            liveness=Column(FLOAT)
            valence=Column(FLOAT)
            tempo=Column(FLOAT)


        session = Session()
        try:
            #add each song's audiofeatures to it 
            for song_feat in songs_audio_features:
                session.add(audio_features(track_id= song_feat[-1],danceability=song_feat[0], energy=song_feat[1],
                                            key=song_feat[2] ,loudness=song_feat[3],  mode=song_feat[4],
                                            speechiness=song_feat[5],acousticness=song_feat[6],instrumentalness= song_feat[7],
                                            liveness=song_feat[8], valence=song_feat[9],tempo=song_feat[10]))
                session.commit()
        finally:
            session.close()
    @staticmethod
    def get_song_uris(engine: sqlalchemy.engine.Engine):
        base=declarative_base()
        Session = sessionmaker(bind=engine)
        session = Session()

        class track_library(base):
            __tablename__='library'
            uri= Column(String(26),primary_key=True, unique=True)
            track_name=Column(String(100))
            track_artists=Column(String(100))
        try:
            song_URIs=[track_library.uri for track_library in session.query(track_library).all() ]
            return song_URIs
        finally:
            session.close()
    @staticmethod
    def get_audio_features(engine: sqlalchemy.engine.Engine, track_uri:str):
        #accept a single element list or multiple elements in the list 
        
        #returns a 3 -tuple 
        # one of the three elements may be null (need to check that this is possible in pythoon )

    #get the audiofeatures for a specific song if we have it 
        pass
    #first make sure that the song is in the database! 
    #if not then add it to DB and add the 
    @staticmethod
    def song_in_db(): 
        pass

