import pytest
import requests
from bs4 import BeautifulSoup
import devias.config as config

from devias.user.utils import get_auth_token


# Note this test could fail if the Gitlab server is down, for example.
def test_get_auth_token_sign_up_page_ok():
    s = requests.Session()
    s.verify = False

    sign_up_page = s.get(config.SIGN_UP_URL).text
    register_token = get_auth_token(sign_up_page)

    assert register_token is not None


@pytest.mark.parametrize("data",[
    {   
        'new_user[first_name]': "Tester",
        'new_user[last_name]': "Four",
        'new_user[username]': "Tester4",
        'new_user[email]': "tester4@test.com",
        'new_user[password]': "tester4spwd",
    },
    {   
        'new_user[first_name]': "Tester",
        'new_user[last_name]': "Five",
        'new_user[username]': "Tester5",
        'new_user[email]': "tester5@test.com",
        'new_user[password]': "tester5spwd",
    },
])
def test_register_no_token_fail(data):
    s = requests.Session()
    s.verify = False

    sign_up_page = s.get(config.SIGN_UP_URL).text
    register_token = get_auth_token(sign_up_page)

    req = s.post(config.REGISTER_URL,data=data)
    
    assert req.status_code != 200



@pytest.mark.parametrize("data",[
    {   
        'new_user[first_name]': "",
        'new_user[last_name]': "Four",
        'new_user[username]': "Tester4",
        'new_user[email]': "tester4@test.com",
        'new_user[password]': "tester4spwd",
    },
    {   
        'new_user[first_name]': "Tester",
        'new_user[last_name]': "",
        'new_user[username]': "Tester4",
        'new_user[email]': "tester4@test.com",
        'new_user[password]': "tester4spwd",
    },
    {   
        'new_user[first_name]': "Tester",
        'new_user[last_name]': "Four",
        'new_user[username]': "",
        'new_user[email]': "tester4@test.com",
        'new_user[password]': "tester4spwd",
    },
    {   
        'new_user[first_name]': "Tester",
        'new_user[last_name]': "Four",
        'new_user[username]': "Tester4",
        'new_user[email]': "",
        'new_user[password]': "tester4spwd",
    },
    {   
        'new_user[first_name]': "Tester",
        'new_user[last_name]': "Four",
        'new_user[username]': "Tester4",
        'new_user[email]': "tester4@test.com",
        'new_user[password]': "",
    },
])
def test_register_fields_blank_fail(data):
    s = requests.Session()
    s.verify = False

    sign_up_page = s.get(config.SIGN_UP_URL).text
    register_token = get_auth_token(sign_up_page)

    data['authenticity_token'] = register_token
    req = s.post(config.REGISTER_URL, data=data)
    
    soup = BeautifulSoup(req.text,'html.parser')
    error_tag = soup.find_all("div", {"class": "devise-errors"})
    for item in error_tag:
        list_item = item.find_all("li")

    assert len(list_item) != 0



@pytest.mark.parametrize("data",[
    {   
        'new_user[first_name]': "Tester",
        'new_user[last_name]': "Four",
        'new_user[username]': "Tester3",
        'new_user[email]': "newemail3@test.com",
        'new_user[password]': "tester3spwd",
    },
    {   
        'new_user[first_name]': "Tester",
        'new_user[last_name]': "Four",
        'new_user[username]': "Tester2",
        'new_user[email]': "newemail2@test.com",
        'new_user[password]': "tester2spwd",
    },
])
def test_register_with_taken_username_fail(data):
    s = requests.Session()
    s.verify = False

    sign_up_page = s.get(config.SIGN_UP_URL).text
    register_token = get_auth_token(sign_up_page)

    data['authenticity_token'] = register_token
    req = s.post(config.REGISTER_URL, data=data)
    
    soup = BeautifulSoup(req.text,'html.parser')
    error_tag = soup.find_all("div", {"class": "devise-errors"})
    for item in error_tag:
        list_item = item.find_all("li")

    assert len(list_item) != 0



@pytest.mark.parametrize("data",[
    {   
        'new_user[first_name]': "Tester",
        'new_user[last_name]': "Four",
        'new_user[username]': "NewUsername3",
        'new_user[email]': "tester3@test.com",
        'new_user[password]': "tester3spwd",
    },
    {   
        'new_user[first_name]': "Tester",
        'new_user[last_name]': "Four",
        'new_user[username]': "NewUsername2",
        'new_user[email]': "tester2@test.com",
        'new_user[password]': "tester2spwd",
    },
])
def test_register_with_taken_email_fail(data):
    s = requests.Session()
    s.verify = False

    sign_up_page = s.get(config.SIGN_UP_URL).text
    register_token = get_auth_token(sign_up_page)

    data['authenticity_token'] = register_token
    req = s.post(config.REGISTER_URL, data=data)
    
    soup = BeautifulSoup(req.text,'html.parser')
    error_tag = soup.find_all("div", {"class": "devise-errors"})
    for item in error_tag:
        list_item = item.find_all("li")

    assert len(list_item) != 0




@pytest.mark.parametrize("data",[
    {   
        'new_user[first_name]': "Bob",
        'new_user[last_name]': "Bob",
        'new_user[username]': "i",
        'new_user[email]': "new1@test.com",
        'new_user[password]': "tester2spwd",
    },
    {   
        'new_user[first_name]': "Bob",
        'new_user[last_name]': "Bob",
        'new_user[username]': "UH@",
        'new_user[email]': "new2@test.com",
        'new_user[password]': "tester2spwd",
    },
    {   
        'new_user[first_name]': "Bob",
        'new_user[last_name]': "Bob",
        'new_user[username]': "UH#",
        'new_user[email]': "new1@test.com",
        'new_user[password]': "tester2spwd",
    },
    {   
        'new_user[first_name]': "Bob2",
        'new_user[last_name]': "Bob2",
        'new_user[username]': "new3",
        'new_user[email]': "glubglub@test.com",
        'new_user[password]': "toshort",
    },
])
def test_register_invalid_username_email_or_pwd(data):
    s = requests.Session()
    s.verify = False

    sign_up_page = s.get(config.SIGN_UP_URL).text
    register_token = get_auth_token(sign_up_page)

    data['authenticity_token'] = register_token
    req = s.post(config.REGISTER_URL, data=data)
    
    soup = BeautifulSoup(req.text,'html.parser')
    error_tag = soup.find_all("div", {"class": "devise-errors"})
    for item in error_tag:
        list_item = item.find_all("li")

    assert len(list_item) != 0



@pytest.mark.parametrize("data", [
    {   
        'new_user[first_name]': "Tester",
        'new_user[last_name]': "Seven",
        'new_user[username]': "Tester7",
        'new_user[email]': "tester7@test.com",
        'new_user[password]': "tester7spwd",
    },
])
def test_register_new_user_ok(data):
    s = requests.Session()
    s.verify = False

    sign_up_page = s.get(config.SIGN_UP_URL).text
    register_token = get_auth_token(sign_up_page)

    data['authenticity_token'] = register_token
    req = s.post(config.REGISTER_URL, data=data)
    
    soup = BeautifulSoup(req.text,'html.parser')
    error_tag = soup.find_all("div", {"class": "devise-errors"})
    for item in error_tag:
        list_item = item.find_all("li")

    assert len(list_item) == 0



