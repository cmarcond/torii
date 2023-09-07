import os

# Fetch the value of the environment variable "BARE_URL" and use a default value if not set
URL = os.environ.get('GITLAB_DEVIAS_URL', 'https://gitlab.secdevias.com/')
# Fetch the value of the environment variable "GITLAB_DEVIAS_IP" and use a default value if not set
BARE_URL = os.environ.get('GITLAB_DEVIAS_IP', 'gitlab.secdevias.com')

#URL = 'https://gitlab.secdevias.com/'
#BARE_URL = 'gitlab.secdevias.com'

#URL = 'http://gitlab-webservice-default.gitlab.svc.cluster.local:8080'
#BARE_URL = 'gitlab-webservice-default.gitlab.svc.cluster.local:8080'

SIGN_IN_URL = URL + '/users/sign_in'
LOGIN_URL = URL + '/users/sign_in'
SIGN_UP_URL = URL + '/users/sign_up'
REGISTER_URL = URL + '/users'
RECOVER_URL = URL + '/users/password/new'
RECOVER_ACTION_URL = URL + '/users/password'

MAIL_ADDRESS = 'no-reply@secdevias.com'
MAIL_PASSWORD = 'change-me'

REDIS_MASTER = 'redis-dev'
REDIS_PASSWORD = 'redis_password'
KATA_URL = 'http://kata.devias.com.br/defectdojofinds?key='

# KATA_URL = 'http://kata.devias.com.br/defectdojofinds?key='
# KATA_URL = 'http://kata.devias-desenv.svc.cluster.local:5000/defectdojofinds?key='
