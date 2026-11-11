from flask import render_template, Blueprint, session, copy_current_request_context
from devias.submit_code.forms import FileForm, GitlabForm
from devias.user.utils import login_required
from devias.submit_code.utils import urlify, create_commit, gitlab_ci_write, write_project_info
from werkzeug.utils import secure_filename
from threading import Thread
from git import GitCommandError, Repo
from devias.app import job_status, project_info 
import devias.config as config
import time
import zipfile
import os
import gitlab
import uuid
import shutil
import glob
import json


submit = Blueprint('submit', __name__,
                        template_folder='templates')


######################################
#               INDEX                #
######################################

@submit.route('/')
@login_required
def index():
    """Renders the page with a zip upload form and a Gitlab project clone form.
    """
    
    zip_form = FileForm()
    gitlab_form = GitlabForm()
    return render_template('upload.html',zip_form=zip_form, gitlab_form=gitlab_form)

    

######################################
#             ZIP UPLOAD             #
######################################

@submit.route('/arquivo', methods=['GET','POST'])
@login_required
def upload_code():
    """Processes a .zip upload

        On submission:
        - Generates a unique identifier for the project
        - Saves the .zip file in a local directory with the uuid name
        - Processes the submission in the background, with threading
    """


    zip_submit_errors = set()
    zip_form = FileForm()
    gitlab_form = GitlabForm()

    project_uuid = None

    if zip_form.validate_on_submit():
        project_uuid = uuid.uuid4().hex

        # Gets file and converts name to secure string
        f = zip_form.file.data
        filename = secure_filename(f.filename)
        
        if filename[-4:] != ".zip":
            error = "Nome de arquivo inválido."
            zip_submit_errors.add(error)
            return render_template('upload.html', zip_form=zip_form,  gitlab_form=gitlab_form, zip_submit_errors=zip_submit_errors)


        script_dir = os.path.dirname(__file__)
        temp_dir = os.path.join(script_dir,project_uuid)
        os.mkdir(temp_dir)

        file_path = os.path.join(temp_dir,filename)
        f.save(file_path)

        input_name = zip_form.zip_project_name.data
        zip_project_name = urlify(input_name)


        try:
            gl = gitlab.Gitlab(config.URL, private_token=session['private_token'], api_version=4, ssl_verify=config.GITLAB_SSL_VERIFY)
            project = gl.projects.create({'name': zip_project_name})

        except gitlab.GitlabCreateError:
            error = "Você já submeteu um projeto com este nome."
            zip_submit_errors.add(error)
            shutil.rmtree(temp_dir)            

            return render_template('upload.html', zip_form=zip_form,  gitlab_form=gitlab_form, zip_submit_errors=zip_submit_errors)


        @copy_current_request_context
        def process_upload_submission(temp_dir, filename, zip_project_name, project, project_uuid):
            """
                Processes the submission:
                - extracts the .zip file into a folder with the same name, in the same directory (temp_dir)
                - initializes git repo in the extracted folder
                - sets remote repo
                - adds, commits and pushes contents of extracted folder to remote
                - sets up pipeline configs and runs pipeline
            """

            # change these first 3 lines to outside the background function
            file_path = os.path.join(temp_dir,filename)

            extracted_folder = os.path.splitext(filename)[0]
            extracted_folder_path = os.path.join(temp_dir,extracted_folder)

            with zipfile.ZipFile(file_path,"r") as zip_ref:
                zip_ref.extractall(extracted_folder_path)

            try:
                # searches for a .git directory in the extracted project
                git_init_directory = glob.glob(extracted_folder_path + '/**/.git', recursive=True)
                for path in git_init_directory:
                    shutil.rmtree(path)

                repo = Repo.init(path=extracted_folder_path)

                remote_url = f"http://{session['user']['username']}:{session['private_token']}@{config.BARE_URL}/{session['user']['username']}/{zip_project_name}.git"
                
                print(f"{config.BARE_URL}/{session['user']['username']}/{zip_project_name}.git")
                origin = repo.create_remote('origin',url=remote_url)

                repo.git.add(all=True)
                repo.index.commit('Upload do projeto no Gitlab.')
                repo.remotes.origin.push(refspec='master:main', env={'GIT_SSL_NO_VERIFY': '1'})

                # test for timeout
                while project.import_status == u'started':
                    time.sleep(1.0)
                print("import complete")

                project_id = project.id
                submit_method = "upload"

                info = write_project_info(session['user']['username'], zip_project_name, project_uuid, submit_method, None, None)
                print("after write_project_info")
                project_info.set(project_id, json.dumps(info))

                file = gitlab_ci_write(project_uuid)
                print("after gitlab_ci_write")
                create_commit(file,project,branch="main")
                print("after create commit of gitlab-ci")

                project.pipelines.create({'ref': 'main', 'variables':[{'key': 'EXECUTE', 'value': 'true'}]})
                
                job_status.set(f'{project_uuid}','running')
                curr_status = job_status.get(f'{project_uuid}')

                print(f'status is {curr_status}')
                print("pipeline running")
            
            except Exception as e:
                print(e)
                job_status.set(f'{project_uuid}','upload import error')
                project.delete()
                    

            shutil.rmtree(temp_dir)


        if project is not None: # add temp_dir validation
            t1 = Thread(target=process_upload_submission, args=(temp_dir, filename, zip_project_name, project, project_uuid,))
            t1.start()

            job_status.set(f'{project_uuid}','started')

            curr_status = job_status.get(f'{project_uuid}')
            print(curr_status)

            print("After thread starts")
            return render_template('upload.html', zip_form=zip_form,  gitlab_form=gitlab_form,
                                    zip_submit_errors=zip_submit_errors, project_uuid=project_uuid, project_name=zip_project_name)

        else:
            error = "Não foi possível importar seu projeto. Por favor tente novamente mais tarde."
            zip_submit_errors.add(error)

            shutil.rmtree(temp_dir)            
            
            return render_template('upload.html', zip_form=zip_form,  gitlab_form=gitlab_form, zip_submit_errors=zip_submit_errors)

        # return redirect(url_for('accept.project_info'))

    return render_template('upload.html', zip_form=zip_form,  gitlab_form=gitlab_form, zip_submit_errors=zip_submit_errors)


######################################
#            CLONE GITLAB            #
######################################


@submit.route('/gitlab', methods = ['GET', 'POST'])
def clone_gitlab():
    """Processes a Gitlab project submission.

        On submission:
        - Generates a unique project UUID.
        - Saves the original Gitlab project.
        - Uploads the cloned project to local Gitlab instance.
    """

    gitlab_submit_errors = set()

    zip_form = FileForm()
    gitlab_form = GitlabForm()

    project_uuid = None

    if gitlab_form.validate_on_submit():

        original_repo_URL = gitlab_form.gitlab_repo_http.data
        input_name = gitlab_form.gitlab_project_name.data
        project_name = urlify(input_name)
        project_uuid = uuid.uuid4().hex

        username = gitlab_form.username.data
        password = gitlab_form.password.data


        if original_repo_URL[-4:] != ".git":
            error = "URL inválida."
            gitlab_submit_errors.add(error)
            return render_template('upload.html', zip_form=zip_form, gitlab_form=gitlab_form, gitlab_submit_errors=gitlab_submit_errors)


        try:
            gl = gitlab.Gitlab(config.URL, private_token=session['private_token'], api_version=4, ssl_verify=config.GITLAB_SSL_VERIFY)
            project = gl.projects.create({'name': project_name})

        except gitlab.GitlabCreateError:
            error = "Você já submeteu um projeto com este nome."
            gitlab_submit_errors.add(error)

            return render_template('upload.html', zip_form=zip_form, gitlab_form=gitlab_form, gitlab_submit_errors=gitlab_submit_errors)


        @copy_current_request_context
        def process_gitlab_submission(original_repo_URL, project_name, username, password, project, project_uuid):
            """Process Gitlab submission in background.

            Args:
                original_repo_URL (str): original Gitlab repo URL.
                project_name (str): project name.
                username (str): original Gitlab username.
                password (str): original Gitlab password.
                project (Gitlab RESTObject): Gitlab project rest object.
                project_uuid (str): project UUID.
            """
            
            script_dir = os.path.dirname(__file__)
            temp_dir = os.path.join(script_dir,project_uuid)
            os.mkdir(temp_dir)

            split_url = original_repo_URL.split("//")
            auth_repo_URL = f"{split_url[0]}//{username}:{password}@{split_url[1]}"

            try:
                repo = Repo.clone_from(auth_repo_URL, temp_dir)
                repo.delete_remote("origin")

                new_remote_url = f"https://{session['user']['username']}:{session['private_token']}@{config.BARE_URL}/{session['user']['username']}/{project_name}.git"
                origin = repo.create_remote('origin',url=new_remote_url)


                if "main" in repo.branches:
                    repo.remotes.origin.push(refspec="main:main", env={'GIT_SSL_NO_VERIFY': '1'})
                    branch = "main"
                elif "master" in repo.branches:
                    repo.remotes.origin.push(refspec="master:master", env={'GIT_SSL_NO_VERIFY': '1'})
                    branch = "master"
                else:
                    job_status.set(f'{project_uuid}','gitlab branch error')
                    project.delete()
                    branch = None

            
            except GitCommandError as e:
                print(e)
                job_status.set(f'{project_uuid}','gitlab credential error')

                project.delete()
                branch = None

            except Exception as e:
                print(e)
                job_status.set(f'{project_uuid}', 'gitlab clone error')
                
                project.delete()
                branch = None


            if branch is not None:
                while project.import_status == u'started':
                    time.sleep(1.0)
                print("import complete")

                project_id = project.id
                submit_method = "gitlab"

                # create a project access token
                project_access_token = project.access_tokens.create({"name": "Devias", "scopes": ["api"]})
                project_access_token = project_access_token.token


                info = write_project_info(session['user']['username'], project_name, project_uuid, submit_method, 
                                            original_repo_URL, project_access_token)

                project_info.set(project_id, json.dumps(info))
                print(project_info.get(project_id))


                file = gitlab_ci_write(project_uuid)

                try:
                    create_commit(file,project,branch)
                    project.pipelines.create({'ref': f'{branch}', 'variables':[{'key': 'EXECUTE', 'value': 'true'}]})

                    project.protectedbranches.delete(branch)

                    job_status.set(f'{project_uuid}','running')
                    curr_status = job_status.get(f'{project_uuid}')

                    print(f'status is {curr_status}')
                    print("pipeline running")


                except gitlab.GitlabCreateError as e:
                    print(e)
                    job_status.set(f'{project_uuid}', 'gitlab ci file error')

                    project.delete()

                except gitlab.GitlabHttpError as e:
                    print(e)
                    job_status.set(f'{project_uuid}', 'gitlab clone error')

                    project.delete()
                    

            shutil.rmtree(temp_dir)
        

        # *******************
        # Test for exceptions
        # *******************


        if project is not None:
            t3 = Thread(target=process_gitlab_submission, args=(original_repo_URL, project_name, username, password, project, project_uuid,))
            t3.start()

            job_status.set(f'{project_uuid}','started')

            curr_status = job_status.get(f'{project_uuid}')
            print(curr_status)

            print("After thread starts")
            return render_template('upload.html', zip_form=zip_form, gitlab_form=gitlab_form, 
                                    gitlab_submit_errors=gitlab_submit_errors, project_uuid=project_uuid, project_name=project_name)


        else:
            error = "Não foi possível importar seu projeto. Por favor tente novamente mais tarde. Caso o erro persista, verifique suas credenciais Git."
            gitlab_submit_errors.add(error)

            return render_template('upload.html', zip_form=zip_form, gitlab_form=gitlab_form, gitlab_submit_errors=gitlab_submit_errors)


    return render_template('upload.html', zip_form=zip_form, gitlab_form=gitlab_form, gitlab_submit_errors=gitlab_submit_errors)



######################################
#         GET PROJECT STATUS         #
######################################

@submit.route('/<project_uuid>/get_status')
def get_job_status(project_uuid):
    curr_status = job_status.get(f'{project_uuid}')
    print(f"job status: {curr_status}")
    
    if curr_status is not None:
        return curr_status
    else:
        return "No Project"



######################################
#       DELETE PROJECT STATUS        #
######################################

@submit.route('/<project_uuid>/delete_status')
def delete_job_status(project_uuid):
    if project_uuid is not None:
        job_status.delete(f'{project_uuid}')
        return "Status Deleted"

    else:
        return "No Project"
