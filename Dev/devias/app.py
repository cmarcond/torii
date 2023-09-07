from flask import Flask
from redis import Redis

import devias.config as config
import os
import secrets

job_status = Redis(host=config.REDIS_MASTER, port=6379, db=0, decode_responses=True, password=config.REDIS_PASSWORD)
project_info = Redis(host=config.REDIS_MASTER, port=6379, db=1, decode_responses=True, password=config.REDIS_PASSWORD)
report_info = Redis(host=config.REDIS_MASTER, port=6379, db=2, decode_responses=True, password=config.REDIS_PASSWORD)

app = Flask(__name__)


###################################
#### MOVE TO CONFIG.PY LATER ######
###################################

app.config['SECRET_KEY'] = secrets.token_hex() # os.getenv('FLASK_SECRET_KEY')
app.config['SERVER_NAME'] = os.getenv('SERVER_NAME')

####################################
########## BLUEPRINTS ##############
####################################

from devias.landing_pages.views import home
from devias.user.views import user 
from devias.report.views import report
from devias.list_reports.views import report_list
from devias.submit_code.views import submit
from devias.projects.views import project


app.register_blueprint(home,url_prefix='/')
app.register_blueprint(user)
app.register_blueprint(report)
app.register_blueprint(report_list)
app.register_blueprint(submit,url_prefix='/submeter')
app.register_blueprint(project)
