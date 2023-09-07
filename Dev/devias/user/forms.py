from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, Length
from flask_wtf.file import FileField, FileAllowed


class RegisterForm(FlaskForm):
    first_name = StringField('Nome', 
                            validators=[DataRequired(message="Por favor, informe seu nome."), 
                                        Length(max=127, message="O nome excede o limite de comprimento.")])
  
    last_name = StringField('Sobrenome', 
                            validators=[DataRequired(message="Por favor, informe seu sobrenome."), 
                                        Length(max=127, message="O sobrenome excede o limite de comprimento.")])
    
    username = StringField('Nome de Usuário', 
                            validators=[DataRequired(message="Por favor, informe um nome de usuário."), 
                                        Length(max=128, message="O nome de usuário excede o limite de comprimento.")])
    
    email = StringField('Email', 
                        validators=[DataRequired(message="Por favor, informe seu email."), 
                        Email(message="Email inválido"), Length(max=128, message="O email excede o limite de comprimento.")])
    
    password = PasswordField('Senha', 
                            validators=[DataRequired(message="Por favor, insira uma senha."), 
                            Length(min=8, max=64, message="A senha deve ter no mínimo 8 caracteres."), EqualTo('pass_confirm', message='As senhas não conferem.')])
    
    pass_confirm = PasswordField('Confirme sua senha', validators=[DataRequired(message="Por favor, repita sua senha.")])
    
    submit = SubmitField('Finalizar Cadastro')


class LoginForm(FlaskForm):
    email = StringField('Email', 
                        validators=[DataRequired(), Email(message="Email inválido.")])
    
    password = PasswordField('Senha',
                            validators=[DataRequired()])
    
    submit = SubmitField('Entrar')


class UpdateForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email(message="Email inválido"), Length(max=128, message="O email excede o limite de comprimento.")])
    name = StringField('Nome', validators=[DataRequired()])
    org = StringField('Organização')
    submit = SubmitField('Atualizar Perfil')


class ChangePasswordForm(FlaskForm):
    current = PasswordField('Senha atual', validators=[DataRequired()])
    new = PasswordField('Senha nova', validators=[DataRequired()])
    confirm = PasswordField('Confirme a senha nova', validators=[DataRequired(), Length(min=8, max=64, message="A senha deve ter no mínimo 8 caracteres."),
                                                    EqualTo('pass_confirm', message='As senhas não conferem.')])
    submit = SubmitField('Alterar Senha')


class RecoverPasswordForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email(message="Email inválido"), Length(max=128, message="O email excede o limite de comprimento.")])
    submit = SubmitField('Enviar')

# class DeleteAccountForm(FlaskForm):
