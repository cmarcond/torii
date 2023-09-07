from flask import flash, redirect, render_template, Blueprint, g, url_for
from devias.accept_submission.forms import ProjectForm, JavaForm, JavaContainer, JavaServer, PythonForm
from devias.user.utils import login_required

import devias.config as config


accept = Blueprint('accept', __name__,
                        template_folder='templates')


@accept.route('/', methods=['GET','POST'])
@login_required
def project_info():

    form = ProjectForm()
    if form.validate_on_submit():
        if form.language.data == 'python':
            print("Python")
            return redirect(url_for('accept.python_project_info'))

        elif form.language.data == 'java':
        
            return redirect(url_for('accept.java_project_info'))

    return render_template("project_form.html",form=form,page="Project")


@accept.route('/java', methods=['GET','POST'])
@login_required
def java_project_info():
    form = JavaForm()
    if form.validate_on_submit():
        
        if form.run_platform.data == 'container':
            return redirect(url_for('accept.java_container'))

        elif form.run_platform.data == 'servidor':
            return redirect(url_for('accept.java_server'))

    return render_template("project_form.html", form=form, page="Java")


@accept.route('/java/container', methods=['GET','POST'])
@login_required
def java_container():
    form = JavaContainer()
    if form.validate_on_submit():
        print("Java Container OK")

    return render_template("project_form.html", form=form, page="JavaContainer")


@accept.route('/java/server', methods=['GET','POST'])
@login_required
def java_server():
    form = JavaServer()
    if form.validate_on_submit():
        print("Java Server Ok")

    return render_template("project_form.html", form=form, page="JavaServer")


@accept.route('/python', methods=['GET','POST'])
@login_required
def python_project_info():
    form = PythonForm()
    if form.validate_on_submit():

        flash("Projeto Python importado com sucesso.")

    return render_template("project_form.html", form=form, page="Python")