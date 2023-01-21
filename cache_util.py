import json,sys

def get_cached_token():
    #check if there is a cached token, if there is then let this process happen, else hit for a new token
    #might also be where you check for scopes and the like 

    with open('.cache', 'r') as cache_file:
        # Read the contents of the file: is stored as a dictionary

        #check if a refresh is needed here
        cache_data = cache_file.read()
        dict=json.loads(cache_data)
        return dict
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
def get_auth_info(cached_token:dict=None, refresh_token:bool=False):
    #token_info=[]
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
        
#creating an object out of the client is better, the way spotipy is set up they have it built into the function calls for checking 
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
