# user/views.py

# Cadastro
# Login 
# Editar Informações
# Deletar Conta
# Confirmar email

import gitlab
import requests
import devias.config as config

from bs4 import BeautifulSoup

from flask import render_template, url_for, redirect, request, Blueprint, session, g
from devias.user.forms import ChangePasswordForm, LoginForm, RegisterForm, UpdateForm, RecoverPasswordForm
from devias.user.utils import *


user = Blueprint('user',__name__,
                    template_folder='templates')


@user.before_app_request
def get_gitlab_session():
    user = session.get('user')
    
    if user is None:
        g.user = None
    else:
        g.user = user


@user.route('/sair')
@login_required
def logout():
    """Logs user out.

    Identifies current login private token id, logs user out,
    clears session and revokes private token.
    """

    if g.user is not None:
        gl = gitlab.Gitlab(config.URL, private_token=session['private_token'], api_version=4, ssl_verify=False)
        gl.personal_access_tokens.delete(session['private_token_id'])

    else:
        print("Couldn't logout")
        
    session.clear()
    g.user = None

    return redirect(url_for('home.show'))


# In progress
# So far the changes don't stick ...
@user.route('/perfil', methods = ['GET','POST'])
@login_required
def account():
    # global gl

    info_form = UpdateForm()
    if info_form.validate_on_submit():
        return redirect(url_for('home.under_construction'))

    # if info_form.validate_on_submit():
    #     config.gl.user.email = info_form.email.data
    #     config.gl.user.name = info_form.name.data
    #     config.gl.user.organization = info_form.org.data
        
        ## user.save() -> admin only?

        # gl.user.save()
        # print(g.user)
        # print(gl.user)

    pass_form = ChangePasswordForm()
    if pass_form.validate_on_submit():
        return redirect(url_for('home.under_construction'))        

    # Implement change password feature

    return render_template('account.html', info_form=info_form, pass_form=pass_form)



@user.route('/cadastro', methods=['GET','POST'])
def register_gitlab():
    """Creates a new user in Gitlab instance.

    First name, last name, username, password and authentication token
    are sent to Gitlab to register a new user. 
    """

    # Initializes a set of error messages
    register_error_messages = set()

    # Initialize session object
    s = requests.Session()
    s.verify = False    ## ! Remove after SSL certificate is set
    

    # Loads registration form
    form = RegisterForm()

    if form.validate_on_submit():

        # Get Gitlab register page
        sign_up_page = s.get(config.SIGN_UP_URL).text

        # Looks for regex referring to authenticity token. 
        # Breaks out of search when token is found.
        ## ! Note: Most POST requests to Gitlab Web UI pages require an authenticity 
        ## token to be passed as data
        register_token = get_auth_token(sign_up_page)


        # If no token was found, return error
        if not register_token:
            error = "Não foi possível completar o cadastro. Por favor tente novamente mais tarde."
            register_error_messages.add(error)
            return render_template('register.html',form=form,register_error_messages=register_error_messages)


        data = {
            'new_user[first_name]': form.first_name.data,
            'new_user[last_name]': form.last_name.data,
            'new_user[username]': form.username.data,
            'new_user[email]': form.email.data,
            'new_user[password]': form.password.data,
            'authenticity_token': register_token,
        }
        
        req = s.post(config.REGISTER_URL, data=data)
        if req.status_code != 200:
            error = "Não foi possível completar o cadastro. Por favor tente novamente mais tarde."
            register_error_messages.add(error)
            return render_template('register.html',form=form,register_error_messages=register_error_messages)


        soup = BeautifulSoup(req.text,'html.parser')
        error_tag = soup.find_all("div", {"class": "devise-errors"})
        for item in error_tag:
            list_item = item.find_all("li")
            for item in list_item:
                error = translate_error(item.text)
                register_error_messages.add(error)
            
            
        if len(register_error_messages) == 0:
            return redirect(url_for('user.login_gitlab'))
    
    return render_template('register.html',form=form,register_error_messages=register_error_messages)



@user.route('/entrar', methods=['GET','POST'])
def login_gitlab():
    """Logs a user in, by also logging in to Gitlab.
        
    First, gets authentication token from gitlab sign in page, then posts
    the user input data to gitlab.
    Logs user in if authentication is correct.
    
    Then, if it is user's first login (just registered), configures user role
    as 'software developer' in the welcome page.
    
    Lastly, generates private access token, updates session headers, and 
    creates a gitlab session object. 
    
    The gitlab user's attributes are saved as session attributes, including
    password and personal access token.
    """

    status = ["Ok", "None", "Wrong Credentials", "Server Error"]
    login_status = status[1]

    s = requests.Session()
    s.verify = False

    form = LoginForm()
    if form.validate_on_submit():
        sign_in_page = s.get(config.SIGN_IN_URL).text
        sign_in_token = get_auth_token(sign_in_page)

        if not sign_in_token:
            login_status = status[3]
            return render_template('login.html', form=form, login_status=login_status)


        data = {
            'user[login]': form.email.data,
            'user[password]': form.password.data,
            'authenticity_token': sign_in_token,
        }

        
        req = s.post(config.LOGIN_URL, data=data)
        if req.status_code != 200:
            login_status = status[3]
            return render_template('login.html', form=form, login_status=login_status)


        gl = gitlab.Gitlab(config.URL,api_version=4,session=s)
        print("before login status")
        login_status = gitlab_auth(gl, status)

        if login_status == "Ok":
            session.clear()
            print("login_status == ok")
            welcome_page = s.get(config.URL)
            soup = BeautifulSoup(welcome_page.text, "html.parser")
            if soup.find(id="user_role") is not None:
                print("user_role is None")
                welcome_URL = f"{config.SIGN_UP_URL}/welcome"
                welcome_page_text = welcome_page.text
                welcome_token = get_auth_token(welcome_page_text)

                if not welcome_token:
                    login_status = status[3]
                    return render_template('login.html', form=form, login_status=login_status)

                data = {
                    '_method': "patch",
                    'user[role]': 'software_developer',
                    'commit': 'Get started!',
                    'authenticity_token': welcome_token,
                }
                print("software developer role")

                role_select = s.post(welcome_URL, data=data)
                if role_select.status_code != 200:
                    login_status = status[3]
                    print("no welcome page or role select")
                    return render_template('login.html', form=form, login_status=login_status)


            tokens_page = s.get('/'.join((config.URL, '/-/profile/personal_access_tokens')), allow_redirects=False)
            private_token = None

            if tokens_page.ok:
                pat_creation_token = get_auth_token(tokens_page.text)
                print("found personal token page = ok")
                body = {
                    "personal_access_token[name]": 'devias',
                    "personal_access_token[scopes][]": 'api',
                    'authenticity_token': pat_creation_token,
                }

                response = s.post('/'.join((config.URL, '/-/profile/personal_access_tokens')), data=body)
                if response.ok:
                    response_content = response.json()
                    private_token = response_content.get('new_token')
                    print("New token: ", private_token)
                    print("token created successfully")
                elif response.status_code != 200:
                    login_status = status[3]
                    print("token not created")
                    return render_template('login.html', form=form, login_status=login_status)

            if not private_token:
                login_status = status[3]
                print("not private token: 264")
                return render_template('login.html', form=form, login_status=login_status)


            s.headers.update({'Private-Token': private_token})

            gl = gitlab.Gitlab(config.URL,api_version=4,session=s)
            login_with_pat_status = gitlab_auth(gl, status)

            if login_with_pat_status == "Ok":

                # Get Private Token ID:
                print("Get Private Token ID")
                access_tokens = gl.personal_access_tokens.list()
                private_token_id = access_tokens[-1].get_id()
                
                session['user'] = gl.user._attrs
                session['password'] = form.password.data
                session['private_token'] = private_token
                session['private_token_id'] = private_token_id

                next = request.args.get('next')

                if next == None or not next[0]=='/':
                    print("next == None?")
                    next = url_for('home.show')

                print("before redirect page")
                return redirect(next)

            else:
                print("Private Token ID not found")
                return render_template('login.html', form=form, login_status=login_with_pat_status)

    return render_template('login.html', form=form, login_status=login_status)


@user.route('/sso', methods=['GET', 'POST'])
def saml_sso():
    return redirect(url_for('home.under_construction'))


@user.route('/confirmar')
def confirm_account():
    recipient = session['user']['email']
    send_email(recipient)
    return redirect(url_for('home.under_construction'))