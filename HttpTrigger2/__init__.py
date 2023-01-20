import logging
from tempfile import TemporaryFile
from io import BytesIO

import numpy as np
import pandas as pd
import azure.functions as func
from azure.storage.blob import BlobClient



def get_user_read_list(user_id, time_click_df):
    group_user = time_click_df[time_click_df['user_id'] == user_id]
    sorted_group = group_user.sort_values('click_timestamp', ascending=False)
    read_list = list(sorted_group['click_article_id'])
    return read_list



def recommend(user_id_str, n, timeClick, recsFile):
    user_id = int(user_id_str)

    #TODO get last seen article form user
    #article_id = user_id  # temp
    time_click = time_click = pd.read_pickle(BytesIO(timeClick.read()))
    read_list = get_user_read_list(user_id, time_click)
    article_id = read_list[0]
    '''
    try:
       #temp
    except:
        # new user, no article read
        #TODO use cold start
    '''

    #get recommendations file from blob
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
        user_recs = recommend(user_id, n, timeClick, recsFile)

        res = {'user_id': user_id, 'user_recs': user_recs}
        return func.HttpResponse(str(res))
    else:
        error_message = f'This HTTP triggered function executed successfully.\nPass "{key_word}" in the query string or in the request body for a personalized response.'
        return func.HttpResponse(error_message, status_code=200)
