from flask_mail import Message
from flask import render_template
from threading import Thread
from flask import current_app
from . import mail

def send_async_email(app, msg):
     with app.app_context():
        mail.send(msg)
    
def send_mail(app, to, subject, template, **kwargs):
    msg = Message(app.config['FLASKY_MAIL_SUBJECT_PREFIX'] + subject,
                    sender=app.config['FLASKY_MAIL_SENDER'], recipients=[to])
    msg.body = render_template(template + '.txt', **kwargs)
    msg.html = render_template(template + '.html', **kwargs)
    # thread = Thread(target=send_async_email, args=[app, msg])
    # return thread
    mail.send(msg)

        # else:
        #     for field, errors in form.errors.items():
        #         for error in errors:
        #             return f"Error in field '{field}': {error}"

