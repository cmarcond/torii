import gitlab
import devias.config as config
from flask import Blueprint, render_template, g, session
from devias.landing_pages.project_stats import get_all_project_dates, get_recent_stats


home = Blueprint('home',__name__,
                            template_folder='templates')

@home.route('/')
def show():
    """Renders home page.

    If user is not logged in, shows only a standard home screen.
    Otherwise, shows a welcome message and project statistics.
    """

    if g.user is not None:
        gl = gitlab.Gitlab(config.URL, private_token=session['private_token'], api_version=4, ssl_verify=config.GITLAB_SSL_VERIFY)

        dates = get_all_project_dates(gl)
        recent_stats = get_recent_stats(gl)

        return render_template('home.html', recent_stats=recent_stats, dates=dates)

    return render_template('home.html')
    

@home.route('/ops')
def under_construction():
    """Renders a standard 'under construction' screen."""
    
    return render_template('under_construction.html')