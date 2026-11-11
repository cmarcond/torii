import os

URL = os.environ.get('GITLAB_DEVIAS_URL', 'https://gitlab.secdevias.com/')
BARE_URL = os.environ.get('GITLAB_DEVIAS_IP', 'gitlab.secdevias.com')

# TLS certificate verification for the GitLab API. On by default; set
# GITLAB_SSL_VERIFY=false only for a lab instance with a self-signed certificate.
GITLAB_SSL_VERIFY = os.environ.get('GITLAB_SSL_VERIFY', 'true').lower() not in ('0', 'false', 'no')

SIGN_IN_URL = URL + '/users/sign_in'
LOGIN_URL = URL + '/users/sign_in'
SIGN_UP_URL = URL + '/users/sign_up'
REGISTER_URL = URL + '/users'
RECOVER_URL = URL + '/users/password/new'
RECOVER_ACTION_URL = URL + '/users/password'

MAIL_ADDRESS = 'no-reply@secdevias.com'
MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD', '')

REDIS_MASTER = 'redis-dev'
REDIS_PASSWORD = os.environ.get('REDIS_PASSWORD', 'redis_password')
KATA_URL = os.environ.get('KATA_URL', 'http://kata.devias.com.br/defectdojofinds?key=')

def print_all_variables():
    variables = [
        ('URL', URL),
        ('BARE_URL', BARE_URL),
        ('SIGN_IN_URL', SIGN_IN_URL),
        ('LOGIN_URL', LOGIN_URL),
        ('SIGN_UP_URL', SIGN_UP_URL),
        ('REGISTER_URL', REGISTER_URL),
        ('RECOVER_URL', RECOVER_URL),
        ('RECOVER_ACTION_URL', RECOVER_ACTION_URL),
        ('MAIL_ADDRESS', MAIL_ADDRESS),
        ('REDIS_MASTER', REDIS_MASTER),
        ('KATA_URL', KATA_URL)
    ]
    
    for name, value in variables:
        print(f"{name} = {value}")

print_all_variables()
