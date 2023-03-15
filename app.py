import oauthlib.oauth2
from flask import Flask, render_template, url_for, redirect
from authlib.integrations.flask_client import OAuth
import os
import google.oauth2.credentials
from googleapiclient.discovery import build as google_build

app = Flask(__name__)
app.secret_key = os.urandom(12)

oauth:OAuth = OAuth(app)

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/google/')
def google():

    GOOGLE_CLIENT_ID = '619268607661-01ao98qf4q10l6n9dd8mtuccbm9qjp02.apps.googleusercontent.com'
    GOOGLE_CLIENT_SECRET = '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'

    CONF_URL = 'https://accounts.google.com/.well-known/openid-configuration'
    oauth.register(
        name='google',
        client_id=GOOGLE_CLIENT_ID,
        client_secret=GOOGLE_CLIENT_SECRET,
        server_metadata_url=CONF_URL,
        client_kwargs={
            'scope': 'openid email profile https://www.googleapis.com/auth/calendar'
        }
    )

    # Redirect to google_auth function
    redirect_uri = url_for('google_auth', _external=True)
    print(redirect_uri)
    return oauth.google.authorize_redirect(redirect_uri)

@app.route('/google/auth/')
def google_auth():
    print("START")
    token = oauth.google.authorize_access_token()


    # user = oauth.google.parse_id_token(token, nonce=)
    print(" Google User ", token)
    credentials = token.to_json()
    service = google_build('calendar', 'v3', credentials=credentials)
    event = {
        'summary': 'Google I/O 2015',
        'location': '800 Howard St., San Francisco, CA 94103',
        'description': 'A chance to hear more about Google\'s developer products.',
        'start': {
            'dateTime': '2023-05-28T09:00:00-07:00',
            'timeZone': 'America/Los_Angeles',
        },
        'end': {
            'dateTime': '2023-05-28T17:00:00-07:00',
            'timeZone': 'America/Los_Angeles',
        },
        'recurrence': [
            'RRULE:FREQ=DAILY;COUNT=2'
        ],
        'attendees': [
            {'email': 'lpage@example.com'},
            {'email': 'sbrin@example.com'},
        ],
        'reminders': {
            'useDefault': False,
            'overrides': [
                {'method': 'email', 'minutes': 24 * 60},
                {'method': 'popup', 'minutes': 10},
            ],
        },
    }

    event = service.events().insert(calendarId='primary', body=event).execute()
    print('Event created: %s' % (event.get('htmlLink')))

    return redirect('/')