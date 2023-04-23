from flask import Blueprint, render_template
import flask
import json

import google.oauth2.credentials
import google_auth_oauthlib.flow
import googleapiclient.discovery
import pytz
import datetime
import sqlite3

from credentials_required import credentials_required


API_SERVICE_NAME = 'calendar'
API_VERSION = 'v3'

userRoutes = Blueprint('user', __name__)


@userRoutes.get('/events')
def events():
    return render_template("list.html")


@userRoutes.get('/clubs')
def clubs():
    return "CLUBS"


