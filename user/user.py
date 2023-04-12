from flask import Blueprint, render_template
import flask
import json

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
def edited():
    eventId = flask.request.form["eventId"]
    print(eventId)


    return json.dumps(eventId)
    return render_template("edit.html")
