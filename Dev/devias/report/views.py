import json
import os
import gitlab
import time
import devias.config as config
import requests
import re
from flask import redirect, render_template, url_for, Blueprint, session, copy_current_request_context, request
from devias.user.utils import login_required
from devias.report.utils import format_report_vuln, format_report_sev, write_report_info, get_report_datetime
from devias.app import job_status, report_info 
from threading import Thread
from datetime import date


report = Blueprint('report',__name__,
                    template_folder='templates')



######################################
#           FETCH REPORT             #
######################################

@report.route('/get/<project_name>')
@login_required
def get(project_name):
    """Fetches security report.
    
    First, checks for previous URL (referer), solely to determine whether the
    project has just been submitted or not.

    Then, gets UUID from the Gitlab project page and sends requests to Kata
    until the report is ready (with a 30 minute limit).
    
    Args:
        project_name (str): Project name.
    """
    
    report_error_messages = set()
    req = None
    project_uuid = None
    

    previous_url = request.headers.get("Referer")
    if "submeter" in previous_url:
        new_project = True
    else:
        new_project = False


    if project_name is not None:
        try:
            gl = gitlab.Gitlab(config.URL, private_token=session['private_token'], api_version=4, ssl_verify=config.GITLAB_SSL_VERIFY)
            project_name_with_namespace = f"{session['user']['username']}/{project_name}"
            project = gl.projects.get(project_name_with_namespace)
        except:
            error = "Projeto não encontrado. Por favor tente novamente mais tarde."
            report_error_messages.add(error)
            return render_template('pre_report.html', req=req, project_uuid=project_uuid, project_name=project_name, report_error_messages=report_error_messages)
            
        if project is not None:    
            try:
                f = project.files.get(file_path='.gitlab-ci.yml', ref='master')
            except gitlab.GitlabGetError:
                try:
                    f = project.files.get(file_path='.gitlab-ci.yml', ref='main')
                except:
                    error = "Não foi possível encontrar seu projeto. Por favor tente novamente mais tarde."
                    report_error_messages.add(error)
                    return render_template('pre_report.html', req=req, project_uuid=project_uuid, project_name=project_name, report_error_messages=report_error_messages)

            f = f.decode()
            yml_text = f.decode("utf-8")

            project_uuid = yml_text.splitlines()[1][20:-1]
    

        @copy_current_request_context
        def get_project_after_import(project_uuid):
            max_retries = 50
            tries = 0
            
            report_URL = f"{config.KATA_URL}{project_uuid}"
            s = requests.Session()

            while tries < max_retries:
                req = s.get(report_URL)

                if req.status_code == 200:
                    match = re.findall(r'"number_findings": [0-9]+', req.text)
                    if match is not None:
                        # findings = re.findall(r'[0-9]+', match[0])
                        # if findings[0] != '0':
                        #     break
                        break

                tries = tries + 1
                time.sleep(20)    


            if tries == max_retries:
                if req.status_code == 500 or req.status_code == 405:
                    job_status.set(f'{project_uuid}','report error')
                
                elif req.status_code == 200:
                    job_status.set(f'{project_uuid}','empty report')

            
            if req.status_code == 200:
                script_dir = os.path.dirname(__file__)
                rel_path = f"stored_reports/{project_uuid}.json"
                abs_file_path = os.path.join(script_dir,rel_path)

                file = open(abs_file_path, "w")
                file.write(req.text)
                file.close()

                job_status.set(f'{project_uuid}','done')
                

        t1 = Thread(target=get_project_after_import, args=(project_uuid,))
        t1.start()

        job_status.set(f'{project_uuid}','getting')

    return render_template('pre_report.html', req=req, new_project=new_project, project_uuid=project_uuid, project_name=project_name, report_error_messages=report_error_messages)



######################################
#            SHOW REPORT             #
######################################

@report.route('/relatorio/<project_name>/<project_uuid>')
@login_required
def show(project_name, project_uuid):
    """Compiles report info.
    
    Gets the stored report and extracts vulnerabilities, severity types, etc.

    Args:
        project_name (str): Project name.
        project_uuid (str): Project UUID.
    """

    script_dir = os.path.dirname(__file__)
    rel_path = f"stored_reports/{project_uuid}.json"
    abs_file_path = os.path.join(script_dir,rel_path)
 
    try:
        file = open(abs_file_path, "r")
    except FileNotFoundError:
        return redirect(url_for('report.get', project_name=project_name))
    
    data = json.load(file)
    data["report_name"] = f"Relatório: {project_name}"

    vuln_report = format_report_vuln(data)
    SAST_report, Containers_report, Secrets_report, SCA_report = vuln_report[0:4]

    sev_report = format_report_sev(data)
    Critical, High, Medium, Low, Info = sev_report[0:5]

    file.close()
    os.remove(abs_file_path)

    # report = report_info.get(project_uuid)

    # if report_info.get(f"{project_uuid}") == None:
    project = write_report_info(data, Critical, High, Medium, Low, Info, SAST_report, Containers_report, Secrets_report, SCA_report)
    print(project)

    report_info.set(f"{project_uuid}", json.dumps(project))

    job_status.delete(f'{project_uuid}')                

    # except:
    #     error = "Projeto não encontrado"
    #     report_error_messages.add(error)
    #     return render_template('pre_report.html', req=req, project_uuid=project_uuid, project_name=project_name, report_error_messages=report_error_messages)

    # return render_template('report.html', data=data, report_uuid=report_uuid)
    
    return render_template('report.html', data=data, project_name=project_name, SAST_report=SAST_report, Containers_report=Containers_report, 
                                        Secrets_report=Secrets_report, SCA_report=SCA_report,
                                        Critical = Critical, High = High, Medium = Medium,
                                        Low = Low, Info = Info)



######################################
#          EXAMPLE REPORTS           #
######################################

@report.route('/relatorio/exemplo')
# @login_required
def sample_report():
    """
    """
    
    script_dir = os.path.dirname(__file__)
    rel_path = "stored_reports/report_with_heatmap.json"
    abs_file_path = os.path.join(script_dir,rel_path)
    
    file = open(abs_file_path, "r")
    data = json.load(file)

    vuln_report = format_report_vuln(data)
    sev_report = format_report_sev(data)

    file.close()
    
    return render_template('report.html', data=data, SAST_report=vuln_report[0], Containers_report=vuln_report[1], 
                                        Secrets_report=vuln_report[2], SCA_report=vuln_report[3],
                                        Critical = sev_report[0], High = sev_report[1], Medium = sev_report[2],
                                        Low = sev_report[3], Info = sev_report[4])


@report.route('/relatorio/heatmap')
# @login_required
def sample_heatmap():
    """
    """
    
    script_dir = os.path.dirname(__file__)
    rel_path = "stored_reports/heatmap.html"
    abs_file_path = os.path.join(script_dir,rel_path)
    
    file = open(abs_file_path, "r")
    data = file.read()
    file.close()

    return render_template("heatmap.html", data=data)

