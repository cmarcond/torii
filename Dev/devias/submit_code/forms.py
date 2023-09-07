from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms import StringField, SubmitField, PasswordField
from wtforms.validators import DataRequired, Length, URL


class FileForm(FlaskForm):
    file = FileField('Escolher Arquivo', validators=[FileRequired(), 
                        FileAllowed(['zip'],message="Tipo de arquivo inválido.")])
    
    zip_project_name = StringField('Nome do Projeto',
                                validators=[DataRequired() , Length(max=128, message="O nome do projeto excede o limite de comprimento.")])

    submit = SubmitField('Submeter')

class GitlabForm(FlaskForm):
    username = StringField('Nome de Usuário', 
                            validators=[DataRequired(message="Por favor, informe seu nome de usuário.")])
    password = PasswordField('Senha', 
                            validators=[DataRequired(message="Por favor, insira sua senha.")])

    # Verify if http is valid
    gitlab_repo_http = StringField('URL do Repositório Gitlab',
                                    validators=[DataRequired(), URL("URL inválida.")])
    gitlab_project_name = StringField('Nome do Projeto',
                                validators=[DataRequired() ,Length(max=128, message="O nome do projeto excede o limite de comprimento.")])

    submit = SubmitField('Clonar Gitlab')