from itertools import count

import flask
from flask import Blueprint, render_template, request, session
from slugify import slugify
import datetime
from credentials_required import credentials_required
from models.Club import Club
from helpers import getGoogleService
import pytz

tz = pytz.timezone('CET')
clubRoutes = Blueprint('club', __name__)

@clubRoutes.get("/join")
@credentials_required
def join(credentials):
    clubID = request.args.get("clubID")
    userID = session['user_info']['id']
    print(userID)
    club: Club = Club(clubID)
    if not club.exists():
        return "JOIN ERROR: Club do not exists"
    err_msg = club.join(userID, False)
    if err_msg:
        return err_msg

    service = getGoogleService(credentials)
    try:
        club.event_ids()
        for event_id in club.event_ids():
            
            event = service.events().get(calendarId='primary', eventId=event_id).execute()

            if not 'attendees' in event:
                event['attendees'] = []

            for attendee in event['attendees']:
                if attendee['email'] == session['user_info']['email']:
                    attendee['responseStatus'] = 'accepted'
                    break
            else:
                event['attendees'].append({'email': session['user_info']['email']})
                print(event['attendees'])
                updated_event = service.events().update(calendarId='primary', eventId=event['id'], body=event).execute()
                

    except Exception as e:
        print(e)
        return "Older events not updated"

    return "JOIN SUCCESS"

@clubRoutes.get("/leave")
@credentials_required
def leave(credentials):
    club_id = request.args.get("clubID")
    user_id = session['user_info']['id']

    club: Club = Club(club_id)
    if club.count_admins():
        return "LEAVE ERROR: Would have no admins"

    if not club.exists():
        return "LEAVE ERROR: Club do not exists"
    err_msg = club.leave(user_id)
    if err_msg:
        return err_msg
    return "LEAVE SUCCESS"



@clubRoutes.post("/create")
def create():
    name = flask.request.form["name"]
    user_id = session['user_info']['id']

    club_id = Club.create(name, slugify(name))

    if club_id == None:
        return "CLUB ALREADY EXISTS"

    club = Club(club_id)
    print('created', club_id)

    club.join(user_id, True)

    return 'CREATED AND JOINED <br/> <a href="/club">go back</a>'

@clubRoutes.get("/remove")
@credentials_required
def remove(credentials):
    club_id = request.args.get("clubID")
    user_id = session['user_info']['id']
    club: Club = Club(club_id)
    if not club.exists():
        return "LEAVE ERROR: Club do not exists"

    members, admin = club.getMembers()
    for m in members:
        club.leave(m)

    err_msg = club.remove()
    if err_msg:
        return err_msg
    return "REMOVE SUCCESS"

@clubRoutes.get("/edit")
def edit():
    return "EDIT"

@clubRoutes.get("/stats")
@credentials_required
def stats(_):
    club_id = request.args.get("clubID")
    club = Club(club_id)

    data, event = club.getNextTrainingsStats()
    print(data)
    freq = list(map(lambda x:{'mail': x[1], 'status': x[2] is not None}, data))

    cnt = 0
    p = 0.0
    for f in freq:
        if f['status']:
          cnt+=1
    if cnt != 0:
        freq_len = len(data)
        p = cnt/freq_len * 100
    p = round(p, 2)

    time = datetime.datetime.fromisoformat(event[1]).strftime("%Y.%m.%d  %H:%M")
    ev = {'time': time, 'name': event[2]}



    return flask.render_template("stats.html", freq=freq, event=ev, percent=p)
