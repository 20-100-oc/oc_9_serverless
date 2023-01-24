import logging
from tempfile import TemporaryFile
from io import BytesIO

import numpy as np
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
import azure.functions as func
from azure.storage.blob import BlobClient



def get_user_read_list(user_id, time_click_df):
    group_user = time_click_df[time_click_df['user_id'] == user_id]
    sorted_group = group_user.sort_values('click_timestamp', ascending=False)
    read_list = list(sorted_group['click_article_id'])
    return read_list



def extract_with_indices(x, idx):
    return x[np.arange(x.shape[0])[:, None], idx]



def compute_top_n(idx, n, embeddingsFile):
    embeddings = np.load(BytesIO(embeddingsFile.read()))
    #embeddings = np.load(BytesIO(embeddingsFile.read()), allow_pickle=True)

    # compute cosine similarities
    embedding_rows = embeddings[idx,:].reshape(1, -1)
    embeddings_without_i = np.delete(embeddings, idx, axis=0)
    res = cosine_similarity(embedding_rows, embeddings_without_i)

    # get top "n" similarities
    top_n_indices = np.argpartition(res,-n)[:,-n:]
    top_n_values = extract_with_indices(res, top_n_indices)
    top_n_indices = extract_with_indices(top_n_indices, np.flip(np.argsort(top_n_values), axis=1))

    return res



def recommend(user_id_str, n, timeClick, recsFile, embeddingsFile):
    user_id = int(user_id_str)
    
    try:
        # get last seen article form user
        time_click = time_click = pd.read_pickle(BytesIO(timeClick.read()))
        read_list = get_user_read_list(user_id, time_click)
        article_id = read_list[0]
    except IndexError:
        # new user, no article read:
        #TODO use cold start
        pass
    
    '''
    try:
        # get recommendations file from blob
        recs = np.load(BytesIO(recsFile.read()))
        user_recs = recs[article_id,:n]
        user_recs = list(user_recs)
    except IndexError:
        # new article, not in recs file:
        # compute cosine similarites
        user_recs = compute_top_n(article_id, n, embeddingsFile)
    '''
    #temp
    user_recs = compute_top_n(article_id, n, embeddingsFile)

    return user_recs



def main(req: func.HttpRequest, 
         recsFile: func.InputStream, 
         embeddingsFile: func.InputStream, 
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
        user_recs = recommend(user_id, n, timeClick, recsFile, embeddingsFile)

        res = {'user_id': user_id, 'user_recs': user_recs}
        return func.HttpResponse(str(res))
    else:
        error_message = f'This HTTP triggered function executed successfully.\nPass "{key_word}" in the query string or in the request body for a personalized response.'
        return func.HttpResponse(error_message, status_code=200)
