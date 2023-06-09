import datetime
import sqlite3
import pprint
import flask
import googleapiclient.discovery
import pytz
from flask import Blueprint, render_template
from helpers import credentials_to_dict, getGoogleService, get_user_info
import json

from credentials_required import credentials_required
from models.Club import Club
from models.Event import Event

tz = pytz.timezone('CET')
eventRoutes = Blueprint('event', __name__)

@eventRoutes.get("/confirm")
@credentials_required
def confirm(credentials):
    service = getGoogleService(credentials)
    eventId = flask.request.args["eventId"]
    if not eventId:
        return "No event ID provided"

    event = service.events().get(calendarId='primary', eventId=eventId).execute()
    user_info = get_user_info(credentials)

    if 'attendees' in event:
        for attendee in event['attendees']:
            if attendee['email'] == user_info['email']:
                attendee['responseStatus'] = 'accepted'
                break

    updated_event = service.events().update(calendarId='primary', eventId=event['id'], body=event).execute()
    Event().attendance(eventId, user_info['id'], True)
    return flask.redirect('/event/list')

@eventRoutes.get("/reject")
@credentials_required
def reject(credentials):
    service = getGoogleService(credentials)
    eventId = flask.request.args["eventId"]
    if not eventId:
        return "No event ID provided"

    event = service.events().get(calendarId='primary', eventId=eventId).execute()
    user_info = get_user_info(credentials)

    if 'attendees' in event:
        for attendee in event['attendees']:
            if attendee['email'] == user_info['email']:
                attendee['responseStatus'] = 'declined'
                break

    updated_event = service.events().update(calendarId='primary', eventId=event['id'], body=event).execute()
    Event().attendance(eventId, user_info['id'], False)
    return flask.redirect('/event/list')


@eventRoutes.post("/add")
@credentials_required
def add(credentials):
    service = getGoogleService(credentials)
    calendar = service.calendars().get(calendarId='primary').execute()

    flask.session['credentials'] = credentials_to_dict(credentials)

    start_datetime = datetime.datetime(2023, 3, 28, 8)
    stop_datetime = datetime.datetime(2023, 3, 28, 8, 30)

    name = flask.request.form["name"]
    time = flask.request.form["time"] + ':00'
    is_weekly_recurring = False
    until = None
    if "weekly" in flask.request.form:
        is_weekly_recurring = flask.request.form.get("weekly") == "true"
        until = flask.request.form["until"]
    if until:
        until += ':00'
        until = until.replace("-", "")
        until = until.replace(":", "")

    club_id = flask.request.form["club"]
    club = Club(club_id)

    emails, at_ids = club.getMembers()
    attendees = []

    for email in emails:
        attendees.append({'email': email.strip()})

    event = {
        'summary': name,
        'description': '',
        'start': {
            'dateTime': time,
            'timeZone': 'CET',
        },
        'end': {
            'dateTime': (datetime.datetime.fromisoformat(time) + datetime.timedelta(
                minutes=int(flask.request.form["duration"]))).isoformat(),
            'timeZone': 'CET',
        },
        'attendees': attendees,
        'etag': "app"
    }
    if is_weekly_recurring:
        event["recurrence"] = [f"RRULE:FREQ=WEEKLY;UNTIL={until}Z"]
    event = service.events().insert(calendarId='primary', body=event).execute()
    Event().add(event, at_ids, club_id)
    if is_weekly_recurring:
        instances = service.events().instances(calendarId='primary', eventId=event['id']).execute()
        print(instances)
    return flask.redirect('/event/list')

@eventRoutes.get("/remove")
@credentials_required
def remove(credentials):
    service = getGoogleService(credentials)
    eventId = flask.request.args["eventId"]
    service.events().delete(calendarId='primary', eventId=eventId).execute()
    eventModel = Event()
    eventModel.remove(eventId)

    return flask.redirect('/event/list')

@eventRoutes.get("/edit")
def edit():
    eventId = flask.request.args.get("eventId")
    if not eventId:
        return "No event ID provided"

    return render_template("edit.html", eventId=eventId)

@eventRoutes.post("/edited")
@credentials_required
def edited(credentials):
    service = getGoogleService(credentials)
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

    eventModel = Event()
    eventModel.edit(event['id'], updated_event)
    return flask.redirect('/event/list')


@eventRoutes.get("/list")
@credentials_required
def list_events(credentials):
    service = getGoogleService(credentials)
    calendar = service.calendars().get(calendarId='primary').execute()
    print(calendar['summary'])

    flask.session['credentials'] = credentials_to_dict(credentials)
    user_id = flask.session['user_info']['id']


    timeMin = tz.localize(datetime.datetime.now()).isoformat()
    maybe_events = service.events().list(calendarId='primary', timeMin=timeMin,
                                         maxResults=10, singleEvents=True,
                                         orderBy='startTime').execute()['items']

    pprint.pprint(maybe_events)

    for e in maybe_events:
        e['stats'] = {}
        if 'dateTime' in e['start']:
            e['start']['pretty'] = datetime.datetime.fromisoformat(e['start']['dateTime']).strftime("%Y.%m.%d at %H:%M")

        all_count, yes_count, maybe_count, no_response, no_count = 0, 0, 0, 0, 0

        # The attendee's response status. Possible values are:

        #     "needsAction" - The attendee has not responded to the invitation (recommended for new events).
        #     "declined" - The attendee has declined the invitation.
        #     "tentative" - The attendee has tentatively accepted the invitation.
        #     "accepted" - The attendee has accepted the invitation.

        if 'attendees' in e:
            for a in e['attendees']:
                all_count += 1
                match a['responseStatus']:
                    case 'needsAction':
                        no_response += 1
                    case 'declined':
                        no_count += 1
                    case 'tentative':
                        maybe_count += 1
                    case 'accepted':
                        yes_count += 1

        e['stats'] = {
            'all': all_count,
            'yes': yes_count,
            'maybe': maybe_count,
            'no_response': no_response,
            'no': no_count,
        }

        e['admin'] = Event.is_admin(e['id'], user_id)

    maybe_events = filter(lambda ev: 'dateTime' in ev['start'], maybe_events)

    managed = Club.userClubs(user_id)[1]
    print(managed)

    # return json.dumps(maybe_events)
    return flask.render_template("list.html", events=maybe_events, clubs=managed)

@eventRoutes.get("/attendance")
@credentials_required
def attendance(credentials):
    eventId = flask.request.args.get("eventId")
    if not eventId:
        return "No event ID provided"

    service = getGoogleService(credentials)
    event = service.events().get(calendarId='primary', eventId=eventId).execute()

    yes, no, maybe = [], [], []

    if 'attendees' in event:
        for a in event['attendees']:
            match a['responseStatus']:
                case 'needsAction':
                    maybe.append(a['email'])
                case 'declined':
                    no.append(a['email'])
                case 'tentative':
                    maybe.append(a['email'])
                case 'accepted':
                    yes.append(a['email'])

    attendance = {
        'yes': sorted(yes),
        'no': sorted(no),
        'maybe': sorted(maybe),
    }

    event['start']['pretty'] = datetime.datetime.fromisoformat(event['start']['dateTime']).strftime("%Y.%m.%d at %H:%M")


    # return json.dumps(attendance)
    return flask.render_template("attendance.html", attendance=attendance, event=event)

