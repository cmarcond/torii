import re
import os
from devias.app import project_info


def urlify(name):
    """Converts a string input to a URL compatible format.
    
    Args:
        name (str): Input string.
    
    Returns:
        str: Formatted string.
    """

    name = name.lower()
    name = re.sub(r"[^\w\s]", '', name)
    name = re.sub(r"\s+", '-', name)
    return name


def gitlab_ci_write(project_uuid):
    """Write gitlab-ci.yml file.

    Args:
        project_uuid (str): Project UUID.
    
    Returns:
        str: gitlab-ci.yml file path.
    """

    script_dir = os.path.dirname(__file__)
    rel_path = "static/.gitlab-ci.yml"
    abs_file_path = os.path.join(script_dir,rel_path)

    file = open(abs_file_path,"a")

    file.write("variables:\n")
    file.write(f"  DEVIAS_PRJ_UUID: '{project_uuid}'\n\n")

    file.write("include:\n")
    file.write(f"  - project: 'secdevias/ci-templates'\n")
    file.write("    ref: v1\n")
    file.write("    file:\n")
    file.write("      - 'secdevias-gitlab-ci.yml'")

    file.close()

    return abs_file_path


def create_commit(file, project, branch):
    """Creates a Gitlab commit.

    Args:
        file (str): .gitlab-ci.yml file path.
        project (Gitlab RESTObject): Gitlab project object.
        branch (str): default branch name.
    """
    
    actions = []

    actions.append(
        {
            "action": "create",
            "file_path": "./.gitlab-ci.yml",
            "content": open(file).read(),
        }
    )


    data = {
        "branch": branch,
        "commit_message": "Commit de arquivos do pipeline",
        "actions": actions,
    }

    commit = project.commits.create(data)

    os.remove(file)
    return


def write_project_info(username, project_name, project_uuid, submit_method, original_repo, project_access_token):
    """Compiles project info.

    Args:
        username (str): Username of the project owner.
        project_name (str): Project name.
        project_uuid (str): Project UUID.
        submit_method (str): Submission method (e.g.: 'github').
        original_repo (str): Original repo URL.
        project_access_token (str): Project access token (can be Github or Gitlab).

    Returns:
        dict: dict with info such as username, project name, UUID/version list, etc.
    """
    
    info = {
        "username": username,
        "project_name": project_name,
        "uuid": {
            "1": project_uuid,
        },
        "submit_method": submit_method,
        "original_repo": original_repo,
        "project_access_token": project_access_token,
    }

    return info
