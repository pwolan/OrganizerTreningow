import flask
from flask import Blueprint, render_template, request, session

from credentials_required import credentials_required
from models.Club import Club
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
    err_msg = club.join(userID)
    if err_msg:
        return err_msg

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


