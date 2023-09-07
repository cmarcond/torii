from flask import redirect, url_for, g, request
from functools import wraps
from email.mime.text import MIMEText
import gitlab
import re
import smtplib
import devias.config as config


# Flask default that enables views to be locked behind login
def login_required(view):
    @wraps(view)
    def decorated_function(*args, **kwargs):
        if g.user is None:
            return redirect(url_for('user.login_gitlab', next=request.url))
        return view(*args, **kwargs)
    return decorated_function


def translate_error(error):
    """Gets Gitlab register errors from web UI and translates them.

    Args:
        error (str): Error message to be translated.

    Returns:
        str: String with the translated error message.    
    """

    if error == "Email has already been taken":
        error = "Esse email já foi registrado."
    elif error == "Username has already been taken":
        error = "Esse nome de usuário já foi registrado."
    elif error == "Username is too short (minimum is 2 characters)":
        error = "Nome de usuário muito curto (deve ter no mínimo 2 caracteres)"
    elif error == "Username can contain only letters, digits, '_', '-' and '.'. Cannot start with '-' or end in '.', '.git' or '.atom'.":
        error = "Nome de usuário deve conter apenas letras, números, '_', '-', e '.'. Além disso, não pode iniciar com '-' nem terminar em '.', '.git' ou '.atom'."
    return error


def get_auth_token(page):
    """Searches for authenticity token in response page.

    Args:
        page (response.text object): Page that will be combed for the authenticity token.
    
    Returns:
        str: Authenticity token.
    """
    
    for item in page.split('\n'):
        input = re.search('name="csrf-token" content="([^"]+)"',item)
        if input:
            break

    token = None
    if input:
        token = input.group(1)

    return token


def gitlab_auth(gl, status):
    """Gitlab authentication
    
    Args:
        gl (gitlab.Gitlab object): Gitlab session object
        status (list[str]): List of login statuses

    Returns:
        str: Login status (0 = "Ok", 1 = "None", 2 = "Wrong Credentials", 3 = "Server Error")
    """
    
    login_status = status[1]

    if gl is not None:
        try:
            gl.auth()
            login_status = status[0]
        except gitlab.GitlabAuthenticationError:
            login_status = status[2]

    else:
        login_status = status[3]
 
    return login_status


def send_email(recipient):
    body = 'Tis a test email'
    subject = 'Test email'
    sender = config.MAIL_ADDRESS
    password = config.MAIL_PASSWORD
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = sender
    msg['To'] = recipient

    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp_server:
       smtp_server.login(sender, password)
       smtp_server.sendmail(sender, recipient, msg.as_string())

    print("Confirmation email sent")
