# send_email.py
from flask_mail import Message
from Minimize import mail
from flask import url_for
from Minimize.utils import generate_confirmation_token

def send_verification_email(user):
    token = generate_confirmation_token(user.email)
    confirm_url = url_for('confirm_email', token=token, _external=True)
    subject = "Confirm your account on Minimize"
    body = f"""
    Hi {user.first_name},

    Thanks for signing up for Minimize! Please confirm your email by clicking the link below:

    {confirm_url}

    If you did not sign up, simply ignore this message.
    """

    msg = Message(subject=subject, recipients=[user.email], body=body)
    mail.send(msg)