from flask import Blueprint, render_template

clubRoutes = Blueprint('event', __name__)

@clubRoutes.get("/confirm")
def confirm():
    return "CONFIRM"

@clubRoutes.get("/reject")
def reject():
    return "REJECT"

@clubRoutes.get("/add")
def add():
    return "ADD"

@clubRoutes.get("/remove")
def remove():
    return "REMOVE"

@clubRoutes.get("/edit")
def edit():
    return "EDIT"


