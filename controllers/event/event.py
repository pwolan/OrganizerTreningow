from flask import Blueprint, render_template

eventRoutes = Blueprint('event', __name__)

@eventRoutes.get("/confirm")
def confirm():
    return "CONFIRM"

@eventRoutes.get("/reject")
def reject():
    return "REJECT"

@eventRoutes.get("/add")
def add():
    return "ADD"

@eventRoutes.get("/remove")
def remove():
    return "REMOVE"

@eventRoutes.get("/edit")
def edit():
    return "EDIT"


