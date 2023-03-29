import flask
import google.oauth2.credentials
import google_auth_oauthlib.flow
import googleapiclient.discovery
from functools import wraps


def credentials_required(f):
    @wraps(f)
    def decorator(*args, **kwargs):
        if 'credentials' not in flask.session:
            return flask.redirect('authorize')

            # Load credentials from the session.
        credentials = google.oauth2.credentials.Credentials(**flask.session['credentials'])
        return f(credentials, *args, **kwargs)

    return decorator
