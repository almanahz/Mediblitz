from . import main
from flask import render_template

@main.app_errorhandler(404)
def page_not_found():
    return render_template('404.html'), 404

@main.app_errorhandler(401)
def not_authorized():
    return render_template('401.html'), 401
