from flask import Blueprint, render_template

userRoutes = Blueprint('user', __name__)


@userRoutes.get('/events')
def events():
    return render_template("list.html")


@userRoutes.get('/clubs')
def clubs():
    return "CLUBS"
