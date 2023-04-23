import googleapiclient.discovery
from googleapiclient import errors


def credentials_to_dict(credentials):
    return {'token': credentials.token,
            'refresh_token': credentials.refresh_token,
            'token_uri': credentials.token_uri,
            'client_id': credentials.client_id,
            'client_secret': credentials.client_secret,
            'scopes': credentials.scopes}


API_SERVICE_NAME = 'calendar'
API_VERSION = 'v3'


def getGoogleService(credentials):
    return googleapiclient.discovery.build(
        API_SERVICE_NAME, API_VERSION, credentials=credentials)

def get_user_info(credentials):
    user_info_service = googleapiclient.discovery.build(
      serviceName='oauth2', version='v2',
      credentials=credentials)
    user_info = None
    try:
        user_info = user_info_service.userinfo().get().execute()
    except errors.HttpError as e:
        print('An error occurred: %s', e)
    return user_info
