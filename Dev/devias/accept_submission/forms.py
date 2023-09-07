from flask_wtf import FlaskForm
from wtforms import StringField, RadioField, SubmitField
from wtforms.validators import DataRequired, Length


class ProjectForm(FlaskForm):
    language = RadioField('Linguagem do projeto', choices=[('python', 'Python'),('java', 'Java')], 
                            validators=[DataRequired(message="Por favor, informe a linguagem usada no projeto.")])

    version = StringField('Versão da linguagem', validators=[DataRequired(message="Por favor, informe a versão da linguagem do projeto.")])

    build_file = StringField('Arquivo de build', validators=[DataRequired(message="Por favor, informe o arquivo de build do projeto."), Length(max=128)])

    submit = SubmitField('Próximo')


class JavaForm(FlaskForm):
    compile_platform = StringField('Plataforma de compilação', validators=[DataRequired()])

    run_platform = RadioField('Plataforma onde roda', choices=[('container','Container'),('servidor','Servidor de Aplicação')],
                                validators=[DataRequired(message="Por favor, informe onde seu projeto roda.")])

    java_submit = SubmitField('Próximo')


class JavaContainer(FlaskForm):
    java_docker = StringField('Dockerfile', validators=[DataRequired()])

    java_container_submit = SubmitField('Submeter')


class JavaServer(FlaskForm):


    java_server_submit = SubmitField('Submeter')


class PythonForm(FlaskForm):
    requirements = StringField('Requisitos', validators=[DataRequired()])
    docker = StringField('Dockerfile', validators=[DataRequired()])
    config = StringField('Configuração', validators=[DataRequired()])
    python_submit = SubmitField('Submeter')