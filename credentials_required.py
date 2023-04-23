import flask
import google.oauth2.credentials
from functools import wraps


def credentials_required(f):
    @wraps(f)
    def decorator(*args, **kwargs):
        if 'credentials' not in flask.session:
            return flask.redirect('/authorize')
        credentials = google.oauth2.credentials.Credentials(**flask.session['credentials'])
        return f(credentials, *args, **kwargs)

    return decorator
