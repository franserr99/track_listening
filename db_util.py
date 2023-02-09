from dotenv import load_dotenv
from sqlalchemy.orm import sessionmaker
import os, sqlalchemy, spotipy, sys, datetime, pytz
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, DateTime, FLOAT, PrimaryKeyConstraint
from sqlalchemy.ext.declarative import declarative_base

def main():
    pass


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
        class users(base): 
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
        assert( term=='short_term' or term=='medium_term' or term=='long_term' )
        #recall: the history table has the following fields: user_id, date_recorded, relative_term, track_id
        track_idx= records[0] #list of track ids
        tracks_name= records[1] #list of corresponding track names
        artist_names=records[2] #list of corresponding artist names
        now= datetime.datetime.now(pytz.timezone('US/Pacific')) #the timestamp used for all the records we are going to push right now 
        assert(len(track_idx)==len(tracks_name)==len(artist_names))
        base=declarative_base()
        Session = sessionmaker(bind=engine)
        session = Session()
        class users(base): 
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
            if (term=="long_term") :
                three_months_ago=(now-datetime.timedelta(3*30)).astimezone(pytz.timezone('US/Pacific'))
                history=session.query(listening_history).filter(id==listening_history.user_id).filter(listening_history.relative_term=="long_term").all()
                
                for record in history:
                    recorded_date_tz=datetime.datetime.replace(record.date_recorded, tzinfo=pytz.timezone('US/Pacific'))
                    if recorded_date_tz>three_months_ago:
                        print("longterm recorded within the last three months already happeend")
                        return
            if(term=="medium_term"):
                two_months_ago=(now-datetime.timedelta(2*30)).astimezone(pytz.timezone('US/Pacific'))
                history=session.query(listening_history).filter(id==listening_history.user_id).filter(listening_history.relative_term=="medium_term").all()
                for record in history:
                    recorded_date_tz=datetime.datetime.replace(record.date_recorded, tzinfo=pytz.timezone('US/Pacific'))
                    if recorded_date_tz>two_months_ago:
                        print("midterm recorded within the last two months already happeend")
                        return
            if(term=="short_term"):
                month_ago=(now-datetime.timedelta(30)).astimezone(pytz.timezone('US/Pacific'))
                day_ago=(now-datetime.timedelta(1)).astimezone(pytz.timezone('US/Pacific'))
                history=session.query(listening_history).filter(id==listening_history.user_id).filter(listening_history.relative_term=="short_term").all()
                for record in history:
                    recorded_date_tz=datetime.datetime.replace(record.date_recorded, tzinfo=pytz.timezone('US/Pacific'))
                    if recorded_date_tz>month_ago or recorded_date_tz>day_ago:
                        print("short recorded within the last month already happeend")
                        return
            for track_ID  in track_idx :
                session.add(listening_history(user_id=id, date_recorded= now, relative_term=term, track_id= track_ID))
                session.commit()
        finally:
            session.close()   
    @staticmethod
    def get_listening_history(engine: sqlalchemy.engine.Engine, music_id:str): 
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
        class users(base):
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
    @staticmethod
    def get_songs_heard(engine: sqlalchemy.engine.Engine):
        pass
class song_util:
    @staticmethod
    def get_fav_songs_uri(user:str, engine: sqlalchemy.engine.Engine):
        all_users= user_util.user_id_list()
        if user not in all_users:
            user_util.create_user(id=user, engine=engine)
            print("user not in databse, tracks from history to get ")
            return
        base=declarative_base()
        Session = sessionmaker(bind=engine)
        class users(base):
            __tablename__='users'
            id = Column(String(50), primary_key=True, unique=True)
        class listening_history(base):
            __tablename__='history'
            user_id = Column(String(50),ForeignKey('users.id'), primary_key=True)
            date_recorded=Column(DateTime)
            relative_term=Column(String(30), primary_key=True)
            track_id= Column (String(26) , ForeignKey('library.uri'), primary_key=True)
            __table_args__ = (PrimaryKeyConstraint('user_id', 'relative_term', 'track_id'),)
        class track_library(base):
            __tablename__='library'
            uri= Column(String(26),primary_key=True, unique=True)
            track_name=Column(String(100))
            track_artists=Column(String(100))
        session = Session()
        try:
            user_listening_hist=session.query(listening_history).filter(listening_history.user_id==user).all()
            unique_track_uri=[]
            for track_listenened in user_listening_hist:
                if track_listenened.uri not in unique_track_uri:
                    unique_track_uri.append(track_listenened.uri)
            return unique_track_uri
        finally:
            session.close()
    @staticmethod
    def fav_songs_info(engine: sqlalchemy.engine.Engine, user_id:str):
        song_uri=song_util.get_fav_songs_uri(user=user_id, engine=engine)
        track_names, track_artist=song_util.get_song_info(engine=engine, song_uris=song_uri)
        return song_uri, track_names, track_artist
    @staticmethod
    def get_song_info(engine: sqlalchemy.engine.Engine, song_uris:list):
        base=declarative_base()
        Session = sessionmaker(bind=engine)
        session=Session()
        class track_library(base):
            __tablename__='library'
            uri= Column(String(26),primary_key=True, unique=True)
            track_name=Column(String(100))
            track_artists=Column(String(100))
        track_names=[]
        track_artists=[]
        try:
            library=session.query(track_library).all()
            for track in song_uris:
                for lib_track in library:
                    if track== lib_track.uri:
                        track_names.append(lib_track.track_name)
                        track_artists.append(lib_track.track_artists)
            return track_names, track_artists
        finally:
            session.close()

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
        if not track_uris or len(track_uris)==0:
            return 
        base=declarative_base()
        Session = sessionmaker(bind=engine)
        session = Session()
        db_lib=song_util.get_song_uris(engine=engine)
        class track_library(base):
            __tablename__='library'
            uri= Column(String(26),primary_key=True, unique=True)
            track_name=Column(String(100))
            track_artists=Column(String(100))
        need_features=[]
        try:    
            for i, track in enumerate(track_uris):
                if track not in db_lib:
                    need_features.append(track)
                    session.add(track_library(uri=track, track_name=track_names[i], track_artists=track_artists[i]))
                    session.commit()
        finally:
            session.close()
        #PART TWO: add the features to the library
        partitioned_list=[] 
        trackIDX=need_features
        if not trackIDX or len(trackIDX)==0:
            return 
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
            print(song_URIs)
            print(session.query(track_library).all())
            #sys.exit(1)
            return song_URIs
        finally:
            session.close()
    'returns a list of list, where each element is a list of all the features and the identifying id (id comes last)'
    @staticmethod
    def get_audio_features(engine: sqlalchemy.engine.Engine, tracks_uri:list):        
        #returns a 3 -tuple 
        # one of the three elements may be null (need to check that this is possible in pythoon )
        if len(tracks_uri)==0:
            return
        #get the audiofeatures for a specific song if we have it 
        base=declarative_base()
        Session = sessionmaker(bind=engine)
        session = Session()

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
        songs_features=[]
        try:
            for track in tracks_uri:
                feat=[]
                features=session.query(audio_features).filter(audio_features.track_id==track).first()
                feat.append(features.danceability)
                feat.append(features.energy)
                feat.append(features.key)
                feat.append(features.loudness)
                feat.append(features.mode)
                feat.append(features.speechiness)
                feat.append(features.acousticness)
                feat.append(features.instrumentalness)
                feat.append(features.liveness)
                feat.append(features.valence)
                feat.append(features.tempo)
                feat.append(track)
                songs_features.append(feat)
            return songs_features
        finally:
            session.close() 
    @staticmethod
    def song_in_db(engine: sqlalchemy.engine.Engine, track_uri:str): 
        db_songs= song_util.get_song_uris()
        if track_uri not in db_songs:
            return False
        else:
            return True

class rec_util:
    @staticmethod
    def get_potential_recs(user_ID:str, engine: sqlalchemy.engine.Engine):
        base=declarative_base()
        Session = sessionmaker(bind=engine)
        class potential_recs(base):
            __tablename__='potential_recs'
            user_id = Column(String(50),ForeignKey('users.id'), primary_key=True)
            date_recorded=Column(DateTime, primary_key=True)
            track_id= Column (String(100) , ForeignKey('library.uri'), primary_key=True)
            __table_args__ = (PrimaryKeyConstraint('user_id', 'track_id', 'date_recorded'),)
        session=Session()
        try:
            recs=session.query(potential_recs).filter(potential_recs.user_id==user_ID).all()
            rec_IDs=[]
            for rec in recs:
                if(rec.track_id not in rec_IDs):
                    rec_IDs.append(rec.track_id)
            return rec_IDs
        finally:
            session.close()
    @staticmethod
    def latest_record_date(engine: sqlalchemy.engine.Engine, user_ID:str):
        base=declarative_base()
        Session = sessionmaker(bind=engine)
        #returns the last time a record was pushed for this user 
        class potential_recs(base):
            __tablename__='potential_recs'
            user_id = Column(String(50),ForeignKey('users.id'), primary_key=True)
            date_recorded=Column(DateTime, primary_key=True)
            track_id= Column (String(100) , ForeignKey('library.uri'), primary_key=True)
            __table_args__ = (PrimaryKeyConstraint('user_id', 'track_id', 'date_recorded'),)
        session=Session()

        try: 
            recs= session.query(potential_recs).filter(potential_recs.track_id==user_ID)
            earliest=recs[0].date_recorded
            for rec in recs:
                if rec.date_recorded> earliest:
                    earliest= rec.date_recorded
            return earliest
        finally:
            session.close()



    @staticmethod
    def push_pontential_recs(engine: sqlalchemy.engine.Engine, track_IDs:list, user:str):
        base=declarative_base()
        Session = sessionmaker(bind=engine)
        
        class potential_recs(base):
            __tablename__='potential_recs'
            user_id = Column(String(50),ForeignKey('users.id'), primary_key=True)
            date_recorded=Column(DateTime, primary_key=True)
            track_id= Column (String(100) , ForeignKey('library.uri'), primary_key=True)
            __table_args__ = (PrimaryKeyConstraint('user_id', 'track_id', 'date_recorded'),)
        session=Session()
        now= datetime.datetime.now(pytz.timezone('US/Pacific')).strftime('%Y-%m-%d %H:%M:%S') #the timestamp used for all the records we are going to push right now 
        try:
            db_recs_for_user=rec_util.get_potential_recs(user_ID=user,engine=engine)
            for track in track_IDs:
                if track not in db_recs_for_user:
                    session.add(potential_recs(user_id=user, date_recorded=now, track_id=track))
                    session.commit()
        finally:
            session.close()
        
class seed_util:
    @staticmethod
    def get_stored_seeds(user_ID:str, engine: sqlalchemy.engine.Engine):
        base=declarative_base()
        Session = sessionmaker(bind=engine)
        class seed_tracks(base):
            __tablename__='seed_tracks'
            user_id = Column(String(50),ForeignKey('users.id'), primary_key=True)
            date_recorded=Column(DateTime, primary_key=True)
            track_id= Column (String(100) , ForeignKey('library.uri'), primary_key=True)
            __table_args__ = (PrimaryKeyConstraint('user_id', 'track_id', 'date_recorded'),)
        session=Session()
        try:
            recs=session.query(seed_tracks).filter(seed_tracks.user_id==user_ID).all()
            seed_IDs=[]
            for rec in recs:
                if(rec.track_id not in seed_IDs):
                    seed_IDs.append(rec.track_id)
            return seed_IDs
        finally:
            session.close()
    @staticmethod
    def latest_record_date(engine: sqlalchemy.engine.Engine,user_ID:str):
        #returns the last time a record was pushed for this user 
        base=declarative_base()
        Session = sessionmaker(bind=engine)
        class seed_tracks(base):
            __tablename__='seed_tracks'
            user_id = Column(String(50),ForeignKey('users.id'), primary_key=True)
            date_recorded=Column(DateTime, primary_key=True)
            track_id= Column (String(100) , ForeignKey('library.uri'), primary_key=True)
            __table_args__ = (PrimaryKeyConstraint('user_id', 'track_id', 'date_recorded'),)
        session=Session()
        try: 
            recs= session.query(seed_tracks).filter(seed_tracks.track_id==user_ID)
            earliest=recs[0].date_recorded
            for rec in recs:
                if rec.date_recorded> earliest:
                    earliest= rec.date_recorded
            return earliest
        finally:
            session.close()
    @staticmethod
    def push_seeds(engine: sqlalchemy.engine.Engine,  track_IDs:list, user:str):
        base=declarative_base()
        Session = sessionmaker(bind=engine)
        class seed_tracks(base):
            __tablename__='seed_tracks'
            user_id = Column(String(50),ForeignKey('users.id'), primary_key=True)
            date_recorded=Column(DateTime, primary_key=True)
            track_id= Column (String(100) , ForeignKey('library.uri'), primary_key=True)
            __table_args__ = (PrimaryKeyConstraint('user_id', 'track_id', 'date_recorded'),)
        session=Session()
        now= datetime.datetime.now(pytz.timezone('US/Pacific')).strftime('%Y-%m-%d %H:%M:%S')
        #the timestamp used for all the records we are going to push right now 
        try:
            db_recs_for_user=seed_util.get_stored_seeds(user_ID=user,engine=engine)
            for track in track_IDs:
                if track not in db_recs_for_user:
                    session.add(seed_tracks(user_id=user, date_recorded=now, track_id=track))
                    session.commit()
        finally:
            session.close()
