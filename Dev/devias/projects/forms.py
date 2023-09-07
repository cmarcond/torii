from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField

class GitlabTokenForm(FlaskForm):
    token_username = StringField('Nome de Usuário do Token')
    
    token = PasswordField('Token')
    
    submit = SubmitField('Submeter')