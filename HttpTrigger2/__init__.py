import os
import logging
from tempfile import TemporaryFile

import numpy as np
import azure.functions as func
from azure.storage.blob import BlobClient


def recommend_old(user_id_str, n):
    user_id = int(user_id_str)

    recs = {
        0: [657, 325, 482, 45, 5], 
        1: [357, 387, 855, 487, 54], 
    }

    article_id = user_id   # temp
    user_recs = recs[article_id][:n]
    return user_recs


#def get_recs_file(connection_string):
def get_recs_file():
    container_name = 'data-blob'
    blob_name = 'recs_idx_20.npy'
    connection_string = "DefaultEndpointsProtocol=https;AccountName=oc9serverlessgroup87ea;AccountKey=GGR/fUyGsTQb3m2wC6qnTQuc/BGok7FkGVP7gVe9CsVyGzlFMQyhI9WLMwUenCne3FbERfBa1C5M+AStdowY0g==;EndpointSuffix=core.windows.net"

    blob = BlobClient.from_connection_string(
        conn_str=connection_string, 
        container_name=container_name, 
        blob_name=blob_name)

    with TemporaryFile() as my_blob:
        blob_data = blob.download_blob()
        blob_data.readinto(my_blob)
        my_blob.seek(0)   # don't forget this
        recs = np.load(my_blob)
    
    return recs



def compute_recs(connection_string):
    res = [0, 1, 2]
    return res   #temp



#def recommend(user_id_str, n, connection_string):
def recommend(user_id_str, n):
    user_id = int(user_id_str)

    #TODO get last seen article from user
    try:
        article_id = user_id   #temp
    except:
        # new user, no article read
        #TODO use cold start
        article_id = 4   #temp

    #get recommendations file from blob
    recs_from_file = get_recs_file()
    #recs_from_file = get_recs_file(connection_string)

    try:
        user_recs = recs_from_file[article_id,:n]
        user_recs = list(user_recs)
    except:
        # new article: not in recs file
        #TODO compute cosine similarites
        user_recs = compute_recs()

    return user_recs
    


def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    # get user_id
    key_word = 'userID'
    #dict_key = 'key'
    #connection_string_param = 'connection_string'
    #connection_string = "DefaultEndpointsProtocol=https;AccountName=oc9serverlessgroup87ea;AccountKey=GGR/fUyGsTQb3m2wC6qnTQuc/BGok7FkGVP7gVe9CsVyGzlFMQyhI9WLMwUenCne3FbERfBa1C5M+AStdowY0g==;EndpointSuffix=core.windows.net"
    
    #works but connection string is on API
    user_id = req.params.get(key_word)
    if not user_id:
        try:
            req_body = req.get_json()
        except ValueError:
            pass
        else:
            user_id = req_body.get(key_word)

    '''    
    user_id = req.params.get(key_word)
    connection_string = req.params.get(connection_string_param)
    if not user_id:
        try:
            req_body = req.get_json()
        except ValueError:
            pass
        else:
            user_id, connection_string = req_body.get(key_word)
            connection_string = req.params.get(connection_string_param)
    '''
    '''
    req = req.params.get(dict_key)
    user_id, connection_string = ' '.split(req)
    if not user_id:
        try:
            req_body = req.get_json()
        except ValueError:
            pass
    '''

    # get "n" recommendations and respond with a string
    n = 5
    if user_id:
        user_recs = recommend(user_id, n)
        #user_recs = recommend(user_id, n, connection_string)
        res = {'user_id': user_id, 'user_recs': user_recs}
        return func.HttpResponse(str(res))
    else:
        error_message = f'This HTTP triggered function executed successfully.\nPass "{key_word}" in the query string or in the request body for a personalized response.'
        return func.HttpResponse(error_message, status_code=200)
