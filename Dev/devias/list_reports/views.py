from flask import Blueprint, render_template, session
from devias.user.utils import login_required
import devias.config as config
import gitlab


report_list = Blueprint('report_list', __name__,
                            template_folder='templates')

# change route
@report_list.route('/projetos/<page_number>')
@login_required
def user_reports(page_number):
    """Lists submitted projects, 20 per page.

    Args:
        page_number (int): page number.
    """

    print("Request list projects")

    gl = gitlab.Gitlab(config.URL, private_token=session['private_token'], api_version=4, ssl_verify=config.GITLAB_SSL_VERIFY)
    print("After session")

    projects_limit = session['user']['projects_limit']

    # test for page_number > total pages
    items = gl.projects.list(owned=True, as_list=False, page=page_number, per_page=20)
    

    return render_template('show_reports.html', items=items, projects_limit=projects_limit)
