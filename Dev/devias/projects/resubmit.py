from datetime import date
import shutil
from devias.app import project_info, report_info
from devias.submit_code.utils import create_commit
from git import Repo
import devias.config as config
import json
import gitlab
import uuid
import os



def upload_resubmit():

    pass


def gitlab_resubmit(webhook_token, request):
    """Using the informed project UUID and deploy token, resubmits Gitlab project.

    Uses the webhook token to locate the right project to resubmit. 
    Then, accesses the original project using the created deploy token, clones
    from the origin URL and triggers security pipeline.

    Args:
        webhook_token (str): project UUID sent from Gitlab webhook.
        request (json): request data in json format. 
    """

    for key in project_info.keys():
        if webhook_token in project_info[key]:
            project_id = key
            project = project_info.get(project_id)
            break

    if project is not None:
        new_uuid = uuid.uuid4().hex

        project = json.loads(project)

        if ("deploy_token_username" and "deploy_token") in project:
            deploy_token_username = project["deploy_token_username"]
            deploy_token = project["deploy_token"]

            script_dir = os.path.dirname(__file__)
            temp_dir = os.path.join(script_dir,new_uuid)
            os.mkdir(temp_dir)

            source_repo_URL = request["project"]["git_http_url"]
            split_URL = source_repo_URL.split("//")
            clone_URL = f"{split_URL[0]}//{deploy_token_username}:{deploy_token}@{split_URL[1]}"

            # try:
                # repo = Repo.init(temp_dir, bare=True)
            repo = Repo.clone_from(clone_URL, temp_dir, bare=True)
            # repo = Repo.clone_from(clone_URL, temp_dir)
            origin = repo.remote("origin")
            # repo.delete_remote("origin")

            dest_repo_URL = f"https://{project['username']}:{project['project_access_token']}@{config.BARE_URL}/{project['username']}/{project['project_name']}.git"

            origin.set_url(new_url=dest_repo_URL, push=True)
            # origin = repo.create_remote("origin", url=dest_repo_URL)

            # if "main" in repo.branches:
            #     repo.remotes.origin.push(refspec="main:main", env={'GIT_SSL_NO_VERIFY': '1'})
            # elif "master" in repo.branches:
            #     repo.remotes.origin.push(refspec="master:master", env={'GIT_SSL_NO_VERIFY': '1'})
            

            cmd = repo.git
            # cmd.add(all=True)
            # cmd.commit(m="Ressubmissão")
            cmd.push("origin", mirror=True)
            # cmd.push("origin")

            gl = gitlab.Gitlab(config.URL, private_token=project['project_access_token'], api_version=4, ssl_verify=False)


            # move to util function
            ci_file_path = os.path.join(temp_dir, ".gitlab-ci.yml")
            file = open(ci_file_path, "a")

            file.write("variables:\n")
            file.write(f"  DEVIAS_PRJ_UUID: '{new_uuid}'\n\n")

            file.write("include:\n")
            file.write(f"  - project: 'secdevias/ci-templates'\n")
            file.write("    ref: v1\n")
            file.write("    file:\n")
            file.write("      - 'secdevias-gitlab-ci.yml'")

            file.close()


            gitlab_project = gl.projects.get(project_id)
            default_branch = gitlab_project.default_branch

            create_commit(ci_file_path, gitlab_project, default_branch)
            gitlab_project.pipelines.create({'ref': f'{default_branch}', 'variables':[{'key': 'EXECUTE', 'value': 'true'}]})

            shutil.rmtree(temp_dir)

            uuid_list = project["uuid"]
            
            if type(uuid_list) is dict:
                previous_version = len(uuid_list)
                current_version = int(previous_version) + 1
                uuid_list[f"{current_version}"] = new_uuid
                project["uuid"] = uuid_list


            elif type(uuid_list) is str:
                uuid_list = {
                    "1": project["uuid"],
                    "2": new_uuid,
                }

                project["uuid"] = uuid_list


            print(project)
            project_info.set(project_id, json.dumps(project))


            submission_info = {
                "date": f"{date.today()}",
            }

            report_info.set(new_uuid, json.dumps(submission_info))