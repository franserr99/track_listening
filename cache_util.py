import json,sys, requests, base64, os, datetime
from datetime import datetime
from dotenv import load_dotenv

def get_cached_token():
    cache_data=None
    with open('.cache', 'r') as cache_file:
        # read the contents of the file: is stored as a dictionary
        cache_data = json.loads(cache_file.read())
    now=datetime.now()
    if cache_data:
        expiration_date=datetime.fromtimestamp(cache_data['expires_at'])
        if(expiration_date<now):
            refresh_token() #make it return something, then reassign cache_date reference 
        return cache_data
    else:
        #no cached token
        pass
def refresh_token():
    if ('SPOTIPY_CLIENT_ID' or 'SPOTIPY_CLIENT_SECRET') not in os.environ :
        load_dotenv("/Users/franserr/Documents/portfolio/spotify_usage/env_files/client.env")    
    try: 
        client_secret=os.environ["SPOTIPY_CLIENT_SECRET"] 
        client_ID=os.environ['SPOTIPY_CLIENT_ID']
    except:
        print("one of these were not set as an enviormental variable, needed for successful execution")
        sys.exit(1) 
    client_ID=base64.b64encode(client_ID.encode())
    client_secret=base64.b64encode(client_secret.encode())
    auth_info= get_cached_token()
    refresh_token=auth_info['refresh_token']
    headers = {'Authorization':'Basic '+ client_ID+':'+ client_secret , 'Content-Type': 'application/x-www-form-urlencoded'}
    data = 'grant_type='+refresh_token+'&'+refresh_token+'='+refresh_token+''
    url= 'https://accounts.spotify.com/api/token'
    response= requests.post(url=url,headers=headers, data=data ).json()
    if'expires_at' not in response:
        expires_in=response['expires_in']
        #n seconds from now
        expiration_date=datetime.now()+ datetime.timedelta(seconds=expires_in)
        #now create a timestamp 
        response['expires_at']=int(expiration_date.timestamp())
    update_cache(response)
def get_auth_info(cached_token:dict=None, refresh_token:bool=False):
    if cached_token==None:
        token =get_cached_token()
        if(refresh_token):
            return token['token_type'], token['access_token'], token['refresh_token']
        else:
            return token['token_type'], token['access_token']
    else: 
        if(refresh_token):
            return cached_token['token_type'], cached_token['access_token'], cached_token['refresh_token']
        else:
            return cached_token['token_type'], cached_token['access_token']
def get(key):
    cache = get_cached_token()
    if key in cache:
        return cache[key]
    else:
        return None
def set(key, value):
    cache = get_cached_token()
    cache[key] = value
    update_cache(cache)
def delete(key):
    cache = get_cached_token()
    if key in cache:
        del cache[key]
    update_cache(cache)
def update_cache(data:dict=None):
    if not data: #no dict passed
        data = get_cached_token()
        # Open the .cache file for writing
        with open('.cache', 'w') as cache_file:
            # Write the data to the file
            cache_file.write(json.dumps(data))
    else: 
        with open('.cache', 'w') as cache_file:
            # Write the data to the file
            cache_file.write(json.dumps(data))
#now test the refresh method 