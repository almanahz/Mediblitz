#!/usr/bin/env python3
import os
from app import create_app, db
from app.models import User


app = create_app(os.getenv('FLASK_CONFIG') or 'default')

@app.cli.command()
def greet():
    print("Hello, I hope you doing great?")

@app.shell_context_processor
def make_shell_context():
    return dict(app=app, db=db, User=User)




if __name__ == '__main__':
    app.run()
