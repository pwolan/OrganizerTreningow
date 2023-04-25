import flask
from flask import Blueprint, render_template, request, session

from credentials_required import credentials_required
from models.Club import Club
from helpers import getGoogleService

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
    err_msg = club.join(userID, True)
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
    if not club.exists():
        return "LEAVE ERROR: Club do not exists"
    err_msg = club.leave(user_id)
    if err_msg:
        return err_msg
    return "LEAVE SUCCESS"



@clubRoutes.get("/add")
def add():
    return "ADD"

@clubRoutes.get("/remove")
def remove():
    return "REMOVE"

@clubRoutes.get("/edit")
def edit():
    return "EDIT"

@clubRoutes.get("/stats")
@credentials_required
def stats(_):
    club_id = request.args.get("clubID")
    club = Club(club_id)

    data = club.getIncomingTrainingsStats(3)
    return flask.render_template("stats.html", data=data)

@clubRoutes.get("/show")
@credentials_required
def show(_):
    club_id = request.args.get("clubID")
    club = Club(club_id)

    data = club.getIncomingTrainingsStats(3)

    your = []
    managed = []
    other = []

    user_id = session['user_info']['id']
    clubs = Club.userClubs(user_id)

    your = clubs
    managed = clubs
    other = clubs

    clubs = {
        "your" : your,
        "managed" : managed,
        "other" : other
    }

    return flask.render_template("clubs.html", clubs=clubs)


