from flask import Blueprint, render_template
import flask
import json

import google.oauth2.credentials
import google_auth_oauthlib.flow
import googleapiclient.discovery
import pytz
import datetime

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

@userRoutes.get('/edit')
def edit():
    eventId = flask.request.args.get("eventId")
    return render_template("edit.html", eventId=eventId)

@userRoutes.post('/edited')
@credentials_required
def edited(credentials):
    service = googleapiclient.discovery.build(
        API_SERVICE_NAME, API_VERSION, credentials=credentials)

    eventId = flask.request.form["eventId"]
    if not eventId:
        return "No event ID provided"

    event = service.events().get(calendarId='primary', eventId=eventId).execute()


    if flask.request.form["title"]:
        event["summary"] = flask.request.form["title"]

    duration = None

    # update start time
    if flask.request.form["time"]:
        old_start = datetime.datetime.fromisoformat(event["start"]['dateTime'])
        old_end = datetime.datetime.fromisoformat(event["end"]['dateTime'])
        duration = old_end - old_start
        print('writing: ', flask.request.form['time'])
        event["start"]['dateTime'] = flask.request.form['time'] + ':00'


    # update duration if changed
    if flask.request.form['duration']:
        duration = datetime.timedelta(minutes=int(flask.request.form["duration"]))

    # update end time based on start time and duration
    if flask.request.form['time'] or flask.request.form['duration']:
        start = datetime.datetime.fromisoformat(event["start"]['dateTime'])
        event["end"]['dateTime'] = (start + duration).isoformat()


    updated_event = service.events().update(calendarId='primary', eventId=event['id'], body=event).execute()

    return render_template("edit.html")
