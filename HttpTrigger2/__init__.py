import logging
from tempfile import TemporaryFile
from io import BytesIO

import numpy as np
import azure.functions as func
from azure.storage.blob import BlobClient


'''
def get_recs_file():
    container_name = 'data-blob'
    blob_name = 'recs_idx_5_test.npy'
    connection_string = "DefaultEndpointsProtocol=https;AccountName=oc9serverlessgroup87ea;AccountKey=e5o6Ta6bAELTG23mpWue6ssJ/RfqSLmnYtOf/lDPRPE9r2bfwAqgQYopUf6wc3drAarUz8RJZDO3+AStCuZB6A==;EndpointSuffix=core.windows.net"

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
'''


def recommend(user_id_str, n, recsFile):
    user_id = int(user_id_str)

    #TODO get last seen article form user
    article_id = user_id
    '''
    try:
       #temp
    except:
        # new user, no article read
        #TODO use cold start
    '''

    #get recommendations file from blob
    #recs = get_recs_file()
    #TRYING TO MAKE THIS WORK:
    recs = np.load(BytesIO(recsFile.read()))

    user_recs = recs[article_id,:n]
    user_recs = list(user_recs)
    '''
    try:
        #temp
    except:
        # new article: not in recs file
        #TODO need to compute cosine similarites
        pass
    '''

    return user_recs
    


def main(req: func.HttpRequest, 
         recsFile: func.InputStream, 
         embeddings: func.InputStream, 
         timeClick: func.InputStream) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    # get user_id
    key_word = 'userID'
    user_id = req.params.get(key_word)
    if not user_id:
        try:
            req_body = req.get_json()
        except ValueError:
            pass
        else:
            user_id = req_body.get(key_word)

    # get "n" recommendations and respond with a string
    n = 5
    if user_id:
        user_recs = recommend(user_id, n, recsFile)
        res = {'user_id': user_id, 'user_recs': user_recs}
        return func.HttpResponse(str(res))
    else:
        error_message = f'This HTTP triggered function executed successfully.\nPass "{key_word}" in the query string or in the request body for a personalized response.'
        return func.HttpResponse(error_message, status_code=200)