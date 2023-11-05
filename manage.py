#!/usr/bin/env python3
import os
from app import create_app, db
from app.models import User
from flask import render_template


app = create_app(os.getenv('FLASK_CONFIG') or 'default')

@app.cli.command()
def greet():
    print("Hello, I hope you doing great?")

@app.shell_context_processor
def make_shell_context():
    return dict(app=app, db=db, User=User)

@app.errorhandler(Exception)
def handle_error(error):
    # Custom error handling logic
    return render_template('error.html', error=error), 500

# Define error handler for specific HTTP status code
@app.errorhandler(404)
def handle_not_found_error(error):
    # Custom error handling logic for 404 Not Found
    return render_template('404.html'), 404



if __name__ == '__main__':
    app.run()
