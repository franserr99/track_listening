from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, DateTime, FLOAT, PrimaryKeyConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

def main():
    load_dotenv("/Users/franserr/Documents/portfolio/spotify_usage/env_files/db.env")
    user=os.environ['user']
    pw=os.environ['password']
    port=os.environ['port']
    connector_str='mysql+mysqlconnector://'+user+':'+ pw+ '@localhost:'+ port+'/testing_DB'
    engine=create_engine(connector_str)

    base=declarative_base()
    #the column names are inferred from the variable names 

    #once a track is listened to by one user, we can refer to the same record here
    #less redundant entries
    class track_library(base):
        __tablename__='library'
        uri= Column(String(100),primary_key=True, unique=True)
        track_name=Column(String(100))
        track_artists=Column(String(100))
    class audio_features(base):
        __tablename__='audio_features'
        #example audiofeature (numerical portions of what gets returned)
        #danceability': 0.232, 'energy': 0.441, 'key': 10, 'loudness': -14.604, 'mode': 1, 'speechiness': 0.0452, 'acousticness': 0.135, 'instrumentalness': 0.0441, 'liveness': 0.668, 'valence': 0.237, 'tempo': 147.655
        track_id = Column(String(100), ForeignKey('library.uri'), unique=True,primary_key=True )
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
    class listening_history(base):
        __tablename__='history'
        user_id = Column(String(50),ForeignKey('users.id'), primary_key=True)
        date_recorded=Column(DateTime, primary_key=True)
        relative_term=Column(String(30), primary_key=True)
        track_id= Column (String(100) , ForeignKey('library.uri'), primary_key=True)
        __table_args__ = (PrimaryKeyConstraint('user_id', 'relative_term', 'track_id', 'date_recorded'),)
        #extra comma to indicate the object is a tuple even though it only has one element
    class users(base): #keep a high level users table in order to expand this another way if you want to later
        __tablename__='users'
        id = Column(String(50), primary_key=True, unique=True)

    #create tables
    base.metadata.create_all(bind=engine)
    #create session
    Session = sessionmaker(bind=engine)
    session = Session()


main()

