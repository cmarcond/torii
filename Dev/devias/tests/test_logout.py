from flask import session
import pytest
import gitlab
import devias.config as config
from bs4 import BeautifulSoup
import requests
from devias.user.utils import get_auth_token


@pytest.mark.parametrize("data",[
    {
        'user[login]': 'tester2@test.com',
        'user[password]': 'tester2spwd',
    },
    {
        'user[login]': 'tester3@test.com',
        'user[password]': 'tester3spwd',
    },
    {
        'user[login]': 'tester1@test.com',
        'user[password]': 'tester1spwd',
    },
])
def test_logout_list_tokens_ok(data):
    s = requests.Session()
    s.verify = False

    sign_in_page = s.get(config.SIGN_IN_URL).text
    sign_in_token = get_auth_token(sign_in_page)

    data['authenticity_token'] = sign_in_token
    req = s.post(config.LOGIN_URL, data=data)
    
    gl = gitlab.Gitlab(config.URL,api_version=4,session=s)
    gl.auth()

    tokens_page = s.get('/'.join((config.URL, '/-/profile/personal_access_tokens')), allow_redirects=False)
    pat_creation_token = get_auth_token(tokens_page.text)

    body = {
        "personal_access_token[name]": 'devias',
        "personal_access_token[scopes][]": 'api',
        'authenticity_token': pat_creation_token,
    }

    response = s.post('/'.join((config.URL, '/-/profile/personal_access_tokens')), data=body)
    private_token_page = BeautifulSoup(response.text, "html.parser")
    private_token = private_token_page.find_all('input', id='created-personal-access-token')[0]['value']

    s.headers.update({'Private-Token': private_token})
    gl = gitlab.Gitlab(config.URL,api_version=4,session=s)
    gl.auth()

    user = gl.user._attrs

    access_tokens = gl.personal_access_tokens.list(user_id=user['id'])
    assert access_tokens is not None


# This test shows all tokens are deleted only if there are less than 25(?) already existing.
# tester3 fails.
@pytest.mark.parametrize("data",[
    {
        'user[login]': 'tester2@test.com',
        'user[password]': 'tester2spwd',
    },
    {
        'user[login]': 'tester3@test.com',
        'user[password]': 'tester3spwd',
    },
    {
        'user[login]': 'tester1@test.com',
        'user[password]': 'tester1spwd',
    },
])
def test_logout_delete_tokens_ok(data):
    s = requests.Session()
    s.verify = False

    sign_in_page = s.get(config.SIGN_IN_URL).text
    sign_in_token = get_auth_token(sign_in_page)

    data['authenticity_token'] = sign_in_token
    req = s.post(config.LOGIN_URL, data=data)
    
    gl = gitlab.Gitlab(config.URL,api_version=4,session=s)
    gl.auth()

    tokens_page = s.get('/'.join((config.URL, '/-/profile/personal_access_tokens')), allow_redirects=False)
    pat_creation_token = get_auth_token(tokens_page.text)

    body = {
        "personal_access_token[name]": 'devias',
        "personal_access_token[scopes][]": 'api',
        'authenticity_token': pat_creation_token,
    }

    response = s.post('/'.join((config.URL, '/-/profile/personal_access_tokens')), data=body)
    private_token_page = BeautifulSoup(response.text, "html.parser")
    private_token = private_token_page.find_all('input', id='created-personal-access-token')[0]['value']

    s.headers.update({'Private-Token': private_token})
    gl = gitlab.Gitlab(config.URL,api_version=4,session=s)
    gl.auth()

    user = gl.user._attrs

    access_tokens = gl.personal_access_tokens.list(user_id=user['id'])
    for token in access_tokens:
        token.delete()

    try:
        access_tokens = gl.personal_access_tokens.list(user_id=user['id'])
    except gitlab.GitlabAuthenticationError:
        access_tokens = None

    assert access_tokens == None


## RuntimeError: working outside of request context (session)
# @pytest.mark.parametrize("data",[
#     {
#         'user[login]': 'tester2@test.com',
#         'user[password]': 'tester2spwd',
#     },
#     {
#         'user[login]': 'tester3@test.com',
#         'user[password]': 'tester3spwd',
#     },
#     {
#         'user[login]': 'tester1@test.com',
#         'user[password]': 'tester1spwd',
#     },
# ])
# def test_logout_session_clear_ok(data):
#     s = requests.Session()
#     s.verify = False

#     sign_in_page = s.get(config.SIGN_IN_URL).text
#     sign_in_token = get_auth_token(sign_in_page)

#     data['authenticity_token'] = sign_in_token
#     req = s.post(config.LOGIN_URL, data=data)
    
#     gl = gitlab.Gitlab(config.URL,api_version=4,session=s)
#     gl.auth()

#     tokens_page = s.get('/'.join((config.URL, '/-/profile/personal_access_tokens')), allow_redirects=False)
#     pat_creation_token = get_auth_token(tokens_page.text)

#     body = {
#         "personal_access_token[name]": 'devias',
#         "personal_access_token[scopes][]": 'api',
#         'authenticity_token': pat_creation_token,
#     }

#     response = s.post('/'.join((config.URL, '/-/profile/personal_access_tokens')), data=body)
#     private_token_page = BeautifulSoup(response.text, "html.parser")
#     private_token = private_token_page.find_all('input', id='created-personal-access-token')[0]['value']

#     s.headers.update({'Private-Token': private_token})
#     gl = gitlab.Gitlab(config.URL,api_version=4,session=s)
#     gl.auth()

#     session['user'] = gl.user._attrs

#     session.clear()

#     assert session['user'] == None
