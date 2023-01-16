import logging

import azure.functions as func



def recommend(user_id):
    recs = {
        0: [657, 325, 482, 45, 5], 
        1: [357, 387, 855, 487, 54], 
    }

    user_recs = recs[int(user_id)]
    return ' '.join(str(x) for x in user_recs)



def main(req: func.HttpRequest) -> func.HttpResponse:
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

    # process and respond
    if user_id:
        user_recs = recommend(user_id)

        #success_message = f'User ID: {user_id}\nRecommended articles: {user_recs}'
        #return func.HttpResponse(success_message)
        res = {'user_id': user_id, 'user_recs': user_recs}
        return func.HttpResponse(res)
    else:
        error_message = f'This HTTP triggered function executed successfully.\nPass "{key_word}" in the query string or in the request body for a personalized response.'
        return func.HttpResponse(error_message, status_code=200)
