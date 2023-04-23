import datetime
import sqlite3

import flask
import googleapiclient.discovery
import pytz
from flask import Blueprint, render_template
from helpers import credentials_to_dict

from credentials_required import credentials_required
tz = pytz.timezone('CET')
eventRoutes = Blueprint('event', __name__)

@eventRoutes.get("/confirm")
def confirm():
    return "CONFIRM"

@eventRoutes.get("/reject")
def reject():
    return "REJECT"

@eventRoutes.post("/add")
@credentials_required
def add(credentials, gData):
    service = googleapiclient.discovery.build(
        gData['API_SERVICE_NAME'], gData['API_VERSION'], credentials=credentials)
    #
    calendar = service.calendars().get(calendarId='primary').execute()
    print(calendar['summary'])

    flask.session['credentials'] = credentials_to_dict(credentials)

    start_datetime = datetime.datetime(2023, 3, 28, 8)
    stop_datetime = datetime.datetime(2023, 3, 28, 8, 30)

    attendees = []

    with open("attendees.txt") as fp:
        lines = fp.readlines()
        for line in lines:
            attendees.append({'email': line.strip()})

    name = flask.request.form["name"]
    time = flask.request.form["time"] + ':00'
    print(time, stop_datetime.isoformat())
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
    }
    event = service.events().insert(calendarId='primary', body=event).execute()

    try:
        with sqlite3.connect("identifier.sqlite") as con:
            cur = con.cursor()
            last_id = cur.execute(f'select max(event_db_id) from events').fetchall()[0][0]

            sql = f"INSERT INTO events (event_db_id, summary, description, startDateTime, startTimeZone, endDateTime, endTimeZone, event)" \
                  f"VALUES (?,?,?,?,?,?,?,?)"
            cur.execute(sql, (last_id + 1, name, 'desc', time, 'CET', event['end']['dateTime'], 'CET', event['id']))
            con.commit()
    except Exception as e:
        print(e)
        con.rollback()
    finally:
        return flask.redirect('/event/list')

@eventRoutes.get("/remove")
@credentials_required
def remove(credentials, gData):
    service = googleapiclient.discovery.build(
        gData['API_SERVICE_NAME'], gData['API_VERSION'], credentials=credentials)

    eventId = flask.request.args["eventId"]
    service.events().delete(calendarId='primary', eventId=eventId).execute()

    try:
        with sqlite3.connect("identifier.sqlite") as con:
            cur = con.cursor()
            sql = f" DELETE FROM events WHERE event=\"" + eventId + '";'
            cur.execute(sql)
            con.commit()
    except Exception as e:
        print(e)
        con.rollback()
    finally:
        return flask.redirect('/event/list')

@eventRoutes.get("/edit")
def edit():
    eventId = flask.request.args.get("eventId")
    return render_template("edit.html", eventId=eventId)
@eventRoutes.post("/edited")
@credentials_required
def edited(credentials, gData):
    service = googleapiclient.discovery.build(
        gData['API_SERVICE_NAME'], gData['API_VERSION'], credentials=credentials)

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

    try:
        with sqlite3.connect("identifier.sqlite") as con:
            cur = con.cursor()
            sql = f" UPDATE events SET summary = ?, startDateTime = ?, endDateTime = ? WHERE event= ?"
            cur.execute(sql, (updated_event['summary'], updated_event['start']['dateTime'], updated_event['end']['dateTime'], event['id']))
            con.commit()
    except Exception as e:
        print(e)
        con.rollback()
    finally:
        return flask.redirect('/event/list')


@eventRoutes.get("/list")
@credentials_required
def list_events(credentials, gData):
    service = googleapiclient.discovery.build(
        gData['API_SERVICE_NAME'], gData['API_VERSION'], credentials=credentials)
    #
    calendar = service.calendars().get(calendarId='primary').execute()
    print(calendar['summary'])

    flask.session['credentials'] = credentials_to_dict(credentials)

    timeMin = tz.localize(datetime.datetime.now()).isoformat()
    maybe_events = service.events().list(calendarId='primary', timeMin=timeMin,
                                         maxResults=10, singleEvents=True,
                                         orderBy='startTime').execute()['items']

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

    # return json.dumps(maybe_events)
    return flask.render_template("list.html", events=maybe_events)

