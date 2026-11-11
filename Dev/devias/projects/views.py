from flask import Blueprint, render_template, session, redirect, url_for, request, Response
from devias.user.utils import login_required
from devias.report.views import show
from devias.projects.resubmit import gitlab_resubmit
from devias.projects.forms import GitlabTokenForm
from devias.app import project_info, report_info
from threading import Thread
import gitlab
import json
import devias.config as config

project = Blueprint('project', __name__,
                    template_folder='templates')


@project.route('/ressubmeter/<project_id>', methods=['GET','POST'])
@login_required
def resubmit(project_id):
    """Sets up necessary tokens for Gitlab project resubmissions.
    
    For Gitlab project: requires a deploy token username and a deploy token.

    Args:
        project_id (int): Gitlab ID of the project to be resubmitted.
    """

    project = project_info.get(project_id)
    project_name = None
    project_uuid = None
    submit_method = None
    gitlab_token_form = GitlabTokenForm()
    
    if project is not None:
        project = json.loads(project)
        project_name = project["project_name"]

        try:
            project_uuid = project["uuid"]["1"]
        except:
            project_uuid = project["uuid"]
            
        submit_method = project["submit_method"]


        if project["username"] == session['user']['username']: 
            if submit_method == "gitlab":    
                if gitlab_token_form.validate_on_submit():
                    token_username = gitlab_token_form.token_username.data
                    deploy_token = gitlab_token_form.token.data

                    project["deploy_token_username"] = token_username
                    project["deploy_token"] = deploy_token

                    project_info.set(project_id, json.dumps(project))

                    # return render_template('resubmit.html', project_name=project_name, project_uuid=project_uuid, submit_method=submit_method, token_form=token_form)            

    return render_template('resubmit.html', project_name=project_name, project_uuid=project_uuid, submit_method=submit_method, 
                            gitlab_token_form=gitlab_token_form)



@project.route('/gitlab_hook', methods=['POST'])
def gitlab_hook():
    """Webhook URL to enable Gitlab resubmission."""

    webhook_token = request.headers["X-Gitlab-Token"]

    t = Thread(target=gitlab_resubmit, args=(webhook_token, request.json))
    t.start()

    return Response(status=200)



@project.route('/dashboard/<project_name>')
@login_required
def project_page(project_name):
    """Project Dashboard
    
    Stores reports for all versions of the selected project.

    Args:
        project_name (str): Project name.
    """

    project_id = None

    for key in project_info.keys():
        project = json.loads(project_info[key])

        if project["username"] == session['user']['username'] and project["project_name"] == project_name:
            project_id = key
            break

    reports = []

    if project is not None:
        uuid_list = project["uuid"]
        print(uuid_list)

        if type(uuid_list) is dict:
            for uuid_key in uuid_list:
                report = report_info.get(uuid_list[uuid_key])

                # if report is None:
                    

                if report is not None:
                    report = json.loads(report)
                    reports.append(report)

        elif type(uuid_list) is str:
            report = report_info.get(uuid_list)

            if report is not None:
                print(report)
                report = json.loads(report)
                reports.append(report)

    return render_template('project_page.html', project=project, reports=reports, project_id=project_id)



@project.route('/excluir/<project_name>')
@login_required
def delete(project_name):
    """Deletes a project (from Gitlab as well).
    
    Args:
        project_name (str): Project name
    """

    if project_name is not None:
        gl = gitlab.Gitlab(config.URL, private_token=session['private_token'], api_version=4, ssl_verify=config.GITLAB_SSL_VERIFY)
        project_name_with_namespace = f"{session['user']['username']}/{project_name}"
        exclude_project = gl.projects.get(project_name_with_namespace)
        exclude_project.delete()
        project_info.delete(f"{exclude_project.id}")
        
    return redirect(url_for('report_list.user_reports', page_number = "1"))
