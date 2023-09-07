import pytest
# import responses
import requests
import gitlab 
import devias.config as config
import tests.conftest as conftest
from bs4 import BeautifulSoup

from devias.user.views import login_gitlab
from devias.user.utils import gitlab_auth, get_auth_token


@pytest.fixture
def status():
    return ["Ok", "None", "Wrong Credentials", "Server Error"]


# Note this test could fail if the Gitlab server is down, for example.
def test_get_auth_token_sign_in_ok():
    s = requests.Session()
    s.verify = False
    sign_in_page = s.get(config.SIGN_IN_URL).text
    assert get_auth_token(sign_in_page) is not None
    

## Test passed (need to create new user to reevaluate)
# def test_get_auth_token_welcome_page_ok():
#     s = requests.Session()
#     s.verify = False

#     sign_in_page = s.get(config.SIGN_IN_URL).text
#     sign_in_token = get_auth_token(sign_in_page)

#     data = {
#         'user[login]': 'tester2@test.com',
#         'user[password]': 'tester2spwd',
#         'authenticity_token': sign_in_token,
#     }

#     s.post(config.LOGIN_URL, data=data)
#     gl = gitlab.Gitlab(config.URL,api_version=4,session=s)
#     gl.auth()

#     welcome_page = s.get(config.URL)
#     soup = BeautifulSoup(welcome_page.text, "html.parser")
#     welcome_URL = f"{config.SIGN_UP_URL}/welcome"
#     welcome_page_text = welcome_page.text
#     assert get_auth_token(welcome_page_text) is not None



@pytest.mark.parametrize("data",[
    {
        'user[login]': 'tester3@test.com',
        'user[password]': 'tester3spwd',
    },
    {
        'user[login]': 'tester1@test.com',
        'user[password]': 'tester1spwd',
    }

])
def test_get_auth_token_welcome_page_fail(data):
    s = requests.Session()
    s.verify = False

    sign_in_page = s.get(config.SIGN_IN_URL).text
    sign_in_token = get_auth_token(sign_in_page)

    data['authenticity_token'] = sign_in_token

    s.post(config.LOGIN_URL, data=data)
    gl = gitlab.Gitlab(config.URL,api_version=4,session=s)
    gl.auth()

    welcome_page = s.get(config.URL)
    soup = BeautifulSoup(welcome_page.text, "html.parser")
    welcome_URL = f"{config.SIGN_UP_URL}/welcome"
    welcome_page_text = welcome_page.text
    assert get_auth_token(welcome_page_text) is None



## Test passed (need to create new user to reevaluate)
# def test_role_selection_ok():
#     s = requests.Session()
#     s.verify = False

#     sign_in_page = s.get(config.SIGN_IN_URL).text
#     sign_in_token = get_auth_token(sign_in_page)

#     data = {
#         'user[login]': 'tester2@test.com',
#         'user[password]': 'tester2spwd',
#         'authenticity_token': sign_in_token,
#     }

#     s.post(config.LOGIN_URL, data=data)
#     gl = gitlab.Gitlab(config.URL,api_version=4,session=s)
#     gl.auth()

#     welcome_page = s.get(config.URL)
#     soup = BeautifulSoup(welcome_page.text, "html.parser")
#     welcome_URL = f"{config.SIGN_UP_URL}/welcome"
#     welcome_page_text = welcome_page.text
#     welcome_token = get_auth_token(welcome_page_text)

#     data = {
#         '_method': "patch",
#         'user[role]': 'software_developer',
#         'commit': 'Get started!',
#         'authenticity_token': welcome_token,
#     }

#     role_select = s.post(welcome_URL, data=data)
#     assert role_select.status_code == 200


@pytest.mark.parametrize("data", [
    {
        'user[login]': 'tester3@test.com',
        'user[password]': 'tester3spwd',
    },
    {
        'user[login]': 'tester2@test.com',
        'user[password]': 'tester2spwd',
    },
    {
        'user[login]': 'tester1@test.com',
        'user[password]': 'tester1spwd',
    }
])
def test_get_pat_page_ok(data):
    s = requests.Session()
    s.verify = False

    sign_in_page = s.get(config.SIGN_IN_URL).text
    sign_in_token = get_auth_token(sign_in_page)

    data['authenticity_token'] = sign_in_token
    req = s.post(config.LOGIN_URL, data=data)
    
    gl = gitlab.Gitlab(config.URL,api_version=4,session=s)
    gl.auth()

    tokens_page = s.get('/'.join((config.URL, '/-/profile/personal_access_tokens')), allow_redirects=False)
    assert tokens_page.ok



@pytest.mark.parametrize("data", [
    {
        'user[login]': 'tester3@test.com',
        'user[password]': 'tester3spwd',
    },
    {
        'user[login]': 'tester2@test.com',
        'user[password]': 'tester2spwd',
    },
    {
        'user[login]': 'tester1@test.com',
        'user[password]': 'tester1spwd',
    }
])
def test_get_auth_token_pat_page_ok(data):
    s = requests.Session()
    s.verify = False

    sign_in_page = s.get(config.SIGN_IN_URL).text
    sign_in_token = get_auth_token(sign_in_page)

    data['authenticity_token'] = sign_in_token
    req = s.post(config.LOGIN_URL, data=data)
    
    gl = gitlab.Gitlab(config.URL,api_version=4,session=s)
    gl.auth()

    tokens_page = s.get('/'.join((config.URL, '/-/profile/personal_access_tokens')), allow_redirects=False)
    assert get_auth_token(tokens_page.text) is not None



@pytest.mark.parametrize("url",[
    conftest.host,
    f"{config.SIGN_UP_URL}/welcome",
    '/'.join((config.URL, '/-/profile/personal_access_tokens'))
])
def test_get_auth_token_server_error(url):
    s = requests.Session()
    s.verify = False
    unaccessible_page = s.get(url,allow_redirects=False).text
    assert get_auth_token(unaccessible_page) is None



@pytest.mark.parametrize("data",[
    {
        'user[login]': 'tester3@test.com',
        'user[password]': 'tester3spwd',
    },
    {
        'user[login]': 'tester2@test.com',
        'user[password]': 'tester2spwd',
    },
    {
        'user[login]': 'tester1@test.com',
        'user[password]': 'tester1spwd',
    }
])
def test_gitlab_auth_ok(data,status):
    s = requests.Session()
    s.verify = False

    sign_in_page = s.get(config.SIGN_IN_URL).text
    sign_in_token = get_auth_token(sign_in_page)

    data['authenticity_token'] = sign_in_token
    s.post(config.LOGIN_URL, data=data)
    gl = gitlab.Gitlab(config.URL,api_version=4,session=s)
    assert gitlab_auth(gl,status) == status[0]



@pytest.mark.parametrize("data", [
    {
        'user[login]': "tester3@test.com",
        'user[password]': "tester3spwd",
    },
    {
        'user[login]': "tester3@test.com",
        'user[password]': "tester3spwd",
        'authenticity_token': '',
    },
    {
        'user[login]': "tester3@test.com",
        'user[password]': "tester3spwd",
        'authenticity_token': 'Not a Valid Auth Token',
    }
])
def test_gitlab_auth_no_auth_token(data, status):
    s = requests.Session()
    s.verify = False
    req = s.post(config.LOGIN_URL,data=data)
    gl = gitlab.Gitlab(config.URL, api_version=4, session=s)
    assert gitlab_auth(gl,status) == status[2]



@pytest.mark.parametrize("data",[
    {
        'user[login]': 'tester3@test.com',
        'user[password]': 'Tester3spwd',
    },
    {
        'user[login]': 'tester1@test.com',
        'user[password]': 'tester2spwd',
    },
    {
        'user[login]': '',
        'user[password]': '',
    },
    {
        'user[login]': 'tester2@test.com',
        'user[password]': '',
    },
    {
        'user[login]': 'Not a real user',
        'user[password]': 'Not a real password',
    }
])
def test_gitlab_auth_wrong_credentials(data,status):
    s = requests.Session()
    s.verify = False

    sign_in_page = s.get(config.SIGN_IN_URL).text
    sign_in_token = get_auth_token(sign_in_page)

    data['authenticity_token'] = sign_in_token
    s.post(config.LOGIN_URL, data=data)
    gl = gitlab.Gitlab(config.URL,api_version=4,session=s)
    assert gitlab_auth(gl,status) == status[2]



def test_gitlab_auth_server_error(status):
    assert gitlab_auth(None,status) == status[3]



@pytest.mark.parametrize("data", [
    {
        'user[login]': 'tester3@test.com',
        'user[password]': 'tester3spwd',
    },
    {
        'user[login]': 'tester2@test.com',
        'user[password]': 'tester2spwd',
    },
    {
        'user[login]': 'tester1@test.com',
        'user[password]': 'tester1spwd',
    }
])
def test_create_pat_ok(data):
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

    assert private_token is not None



@pytest.mark.parametrize("data", [
    {
        'user[login]': 'tester3@test.com',
        'user[password]': 'tester3spwd',
    },
    {
        'user[login]': 'tester2@test.com',
        'user[password]': 'tester2spwd',
    },
    {
        'user[login]': 'tester1@test.com',
        'user[password]': 'tester1spwd',
    }
])
def test_create_pat_fail(data):
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
        'authenticity_token': '',
    }

    response = s.post('/'.join((config.URL, '/-/profile/personal_access_tokens')), data=body)
    # private_token_page = BeautifulSoup(response.text, "html.parser")
    # private_token = private_token_page.find_all('input', id='created-personal-access-token')[0]['value']

    assert response.status_code!=200



@pytest.mark.parametrize("data", [
    {
        'user[login]': 'tester3@test.com',
        'user[password]': 'tester3spwd',
    },
    {
        'user[login]': 'tester2@test.com',
        'user[password]': 'tester2spwd',
    },
    {
        'user[login]': 'tester1@test.com',
        'user[password]': 'tester1spwd',
    }
])
def test_gitlab_auth_with_pat_ok(data,status):
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

    assert gitlab_auth(gl,status) == "Ok"

