from flask import Blueprint, render_template

clubRoutes = Blueprint('club', __name__)

@clubRoutes.get("/join")
def join():
    return "JOIN"

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

