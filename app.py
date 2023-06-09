# -*- coding: utf-8 -*-
import json
import os
import flask
import requests
import datetime

import google.oauth2.credentials
import google_auth_oauthlib.flow
import googleapiclient.discovery
import pytz
import sqlite3
from helpers import credentials_to_dict, get_user_info

from credentials_required import credentials_required
from controllers.user.user import userRoutes
from controllers.club.club import clubRoutes
from controllers.event.event import eventRoutes
from models.User import User

os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
os.environ['OAUTHLIB_RELAX_TOKEN_SCOPE'] = '1'

os.environ['DB_PATH'] = "identifier.sqlite"

tz = pytz.timezone('CET')
CLIENT_SECRETS_FILE = "credentials.json"
SCOPES = ['https://www.googleapis.com/auth/calendar','https://www.googleapis.com/auth/userinfo.email']
API_SERVICE_NAME = 'calendar'
API_VERSION = 'v3'

app = flask.Flask(__name__)
app.secret_key = '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'


app.register_blueprint(userRoutes, url_prefix='/user')
app.register_blueprint(clubRoutes, url_prefix='/club')
app.register_blueprint(eventRoutes, url_prefix='/event')

@app.route('/')
def index():
    return flask.render_template("index.html")





##################




@app.route('/databasetest')
def databasetest():
    with sqlite3.connect("identifier.sqlite") as con:
        cur = con.cursor()
        cur.execute("select * from events")
        rows = cur.fetchall()
        return json.dumps(rows)



@app.route('/authorize')
def authorize():
    # Create flow instance to manage the OAuth 2.0 Authorization Grant Flow steps.
    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
        CLIENT_SECRETS_FILE, scopes=SCOPES)

    # The URI created here must exactly match one of the authorized redirect URIs
    # for the OAuth 2.0 client, which you configured in the API Console. If this
    # value doesn't match an authorized URI, you will get a 'redirect_uri_mismatch'
    # error.
    # flow.redirect_uri = flask.url_for('oauth2callback', _external=True)
    flow.redirect_uri = "http://127.0.0.1:5000/oauth2callback/"

    authorization_url, state = flow.authorization_url(
        # Enable offline access so that you can refresh an access token without
        # re-prompting the user for permission. Recommended for web server apps.
        access_type='offline',
        # Enable incremental authorization. Recommended as a best practice.
        include_granted_scopes='true')

    # Store the state so the callback can verify the auth server response.
    flask.session['state'] = state


    return flask.redirect(authorization_url)


@app.route('/oauth2callback/')
def oauth2callback():
    # Specify the state when creating the flow in the callback so that it can
    # verified in the authorization server response.
    state = flask.session['state']
    #
    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
        CLIENT_SECRETS_FILE, scopes=SCOPES, state=state)
    flow.redirect_uri = flask.url_for('oauth2callback', _external=True)
    # flow.redirect_uri = "http://127.0.0.1:5000/oauth2callback/"

    # Use the authorization server's response to fetch the OAuth 2.0 tokens.
    authorization_response = flask.request.url

    flow.fetch_token(authorization_response=authorization_response)

    # Store credentials in the session.
    # ACTION ITEM: In a production app, you likely want to save these
    #              credentials in a persistent database instead.
    credentials = flow.credentials
    flask.session['credentials'] = credentials_to_dict(credentials)
    user_info = get_user_info(credentials)
    flask.session['user_info'] = user_info
    user = User(credentials, user_info)
    user.save()

    return flask.redirect('/')


@app.route('/revoke')
def revoke():
    if 'credentials' not in flask.session:
        return ('You need to <a href="/authorize">authorize</a> before ' +
                'testing the code to revoke credentials.')

    credentials = google.oauth2.credentials.Credentials(
        **flask.session['credentials'])

    revoke = requests.post('https://oauth2.googleapis.com/revoke',
                           params={'token': credentials.token},
                           headers={'content-type': 'application/x-www-form-urlencoded'})

    status_code = getattr(revoke, 'status_code')
    if status_code == 200:
        return ('Credentials successfully revoked.' + print_index_table())
    else:
        return ('An error occurred.' + print_index_table())


@app.route('/clear')
def clear_credentials():
    if 'credentials' in flask.session:
        del flask.session['credentials']
    return ('Credentials have been cleared.<br><br>' +
            print_index_table())


def print_index_table():
    return ('<table>' +
            '<tr><td><a href="/test">Test an API request</a></td>' +
            '<td>Submit an API request and see a formatted JSON response. ' +
            '    Go through the authorization flow if there are no stored ' +
            '    credentials for the user.</td></tr>' +
            '<tr><td><a href="/authorize">Test the auth flow directly</a></td>' +
            '<td>Go directly to the authorization flow. If there are stored ' +
            '    credentials, you still might not be prompted to reauthorize ' +
            '    the application.</td></tr>' +
            '<tr><td><a href="/revoke">Revoke current credentials</a></td>' +
            '<td>Revoke the access token associated with the current user ' +
            '    session. After revoking credentials, if you go to the test ' +
            '    page, you should see an <code>invalid_grant</code> error.' +
            '</td></tr>' +
            '<tr><td><a href="/clear">Clear Flask session credentials</a></td>' +
            '<td>Clear the access token currently stored in the user session. ' +
            '    After clearing the token, if you <a href="/test">test the ' +
            '    API request</a> again, you should go back to the auth flow.' +
            '</td></tr></table>')


if __name__ == '__main__':
    # When running locally, disable OAuthlib's HTTPs verification.
    # ACTION ITEM for developers:
    #     When running in production *do not* leave this option enabled.
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

    # Specify a hostname and port that are set as a valid redirect URI
    # for your API project in the Google API Console.
    app.run('localhost', 5000, debug=True)
