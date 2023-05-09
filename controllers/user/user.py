from flask import Blueprint, render_template, request, session
import flask
import json

import google.oauth2.credentials
import google_auth_oauthlib.flow
import googleapiclient.discovery
import pytz
import datetime
import sqlite3
from models.Club import Club


from credentials_required import credentials_required


API_SERVICE_NAME = 'calendar'
API_VERSION = 'v3'

userRoutes = Blueprint('user', __name__)


@userRoutes.get('/events')
def events():
    return render_template("list.html")


@userRoutes.get('/clubs')
@credentials_required
def show(_):
    club_id = request.args.get("clubID")
    club = Club(club_id)

    data = club.getIncomingTrainingsStats(3)

    your = []
    managed = []
    other = []

    user_id = session['user_info']['id']
    your, managed, other = Club.userClubs(user_id)

    for m in managed:
        c = Club(m[1])
        m = (*m, c.count_admins() > 1)

    
    print(managed)

    clubs = {
        "your" : your,
        "managed" : managed,
        "other" : other 
    }

    return flask.render_template("clubs.html", clubs=clubs)
