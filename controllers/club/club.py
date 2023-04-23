from flask import Blueprint, render_template, request
from models.Club import Club
clubRoutes = Blueprint('club', __name__)

@clubRoutes.get("/join")
def join():
    clubID = request.args.get("clubID")
    club: Club = Club(clubID)
    if not club.exists():
        return "JOIN ERROR: Club do not exists"
    


    return "JOIN SUCCESS"

@clubRoutes.get("/leave")
def leave():
    return "LEAVE"

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
def stats():
    return "STATS"

