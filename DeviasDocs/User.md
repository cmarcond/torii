# Funcionalidades de usuário
**v0.1**

## Cadastro
`user.views.register_gitlab`
O cadastro é realizado através do Web UI Gitlab. É criado um objeto de sessão, que faz um request `GET` da página de cadastro (`SIGN_UP_URL`). Feito o request, usa-se a biblioteca `re` para buscar o regex que corresponde ao token de autenticidade.

```python
data = {
 'new_user[first_name]': form.first_name.data,
 'new_user[last_name]': form.last_name.data,
 'new_user[username]': form.username.data,
 'new_user[email]': form.email.data,
 'new_user[password]': form.password.data,
 'authenticity_token': register_token,
 }

req = s.post(config.REGISTER_URL, data=data)
```

**Importante:**
Requests (especialmente `POST`) via Web UI Gitlab geralmente necessitam que um token de autenticidade seja passado junto.

As informações são postadas à página de cadastro, e eventuais mensagens de erro são renderizadas na página.

-------------------------------------
##### Tradução de erros
`user.utils.translate_error`
Erros de cadastro:
- Email já registrado
- Nome de usuário já registrado
- Nome de usuário muito curto (deve ter no mínimo 2 caracteres)
- Nome de usuário deve conter apenas letras, números, '_', '-', e '.'. Além disso, não pode iniciar com '-' nem terminar em '.', '.git' ou '.atom'.

-------------------------------------

## Login
`user.views.login_gitlab`
Realiza o login através do Gitlab. 
Primeiro, cria uma sessão, passa usuário, senha e token de autenticação à página de login e, se as credenciais estiverem corretas, cria um objeto de sessão Gitlab.

```python
data = {
 'user[login]': form.email.data,
 'user[password]': form.password.data,
 'authenticity_token': sign_in_token,
 }

req = s.post(config.LOGIN_URL, data=data)
	
gl = gitlab.Gitlab(config.URL,api_version=4,session=s)
login_status = gitlab_auth(gl, status)
```

Em seguida, se for primeiro login (usuário recém cadastrado), seleciona o *role* do usuário na página de "boas vindas".

```python
data = {
 '_method': "patch",
 'user[role]': 'software_developer',
 'commit': 'Get started!',
 'authenticity_token': welcome_token,
 }

role_select = s.post(welcome_URL, data=data)
```

Por fim, gera um token de acesso pessoal, necessário para realizar operações mais complexas no Gitlab (como submissão de projeto).

```python
body = {
 "personal_access_token[name]": 'devias',
 "personal_access_token[scopes][]": 'api',
 'authenticity_token': pat_creation_token,
 }

response = s.post('/'.join((config.URL, '/-/profile/personal_access_tokens')), data=body)

s.headers.update({'Private-Token': private_token})
gl = gitlab.Gitlab(config.URL,api_version=4,session=s)
login_with_pat_status = gitlab_auth(gl, status)
```

Feito o login, é criada uma sessão Flask para o usuário, que tem duração indefinida. São armazenados os atributos do usuário `Gitlab.CurrentUser`, a senha e o token de acesso pessoal, bem como o ID deste token.

```python
session['user'] = gl.user._attrs
session['password'] = form.password.data
session['private_token'] = private_token
session['private_token_id'] = private_token_id
```

------------------------------
##### Autenticação Gitlab
`user.utils.gitlab_auth`
Realiza a autenticação do objeto de sessão Gitlab (`gl.auth()`).
Apresenta os seguintes status:
- Ok \[0\]
- Nenhum \[1\]
- Credenciais Erradas \[2\]
- Erro de Servidor \[3\]

Inicializado em `status[1]` ("None").
Se as credenciais estão certas (incluindo token de acesso pessoal, se for o caso), retorna `status[0]` ("Ok").
Se houver erro de autenticação, retorna `status[2]` ("Wrong Credentials").
Se houver algum erro 500, erro em algum `POST` ou `GET`, retorna `status[3]` ("Server Error").

------------------------------
##### Obtenção de Token de Autenticação
`user.utils.get_auth_token`
Recebe o texto de uma resposta de `GET` de alguma página (login, cadastro, geração de token de acesso pessoal). 

```python
for item in page.split('\n'):
	input = re.search('name="authenticity_token" value="([^"]+)"',item)
	if input:
		break
		
if input:
	token = input.group(1)
```

-------------------------------------
## Logout
`user.utils.logout`
Se o usuário estiver logado, cria conexão Gitlab usando token de acesso pessoal armazenado na sessão Flask, e revoga este token.

```python
gl = gitlab.Gitlab(config.URL, private_token=session['private_token'], api_version=4, ssl_verify=False)
gl.personal_access_tokens.delete(session['private_token_id'])

```

Ao fim, limpa a sessão Flask e configura o usuário `g.user = None`.

--------------------------------------
##  Alteração do Perfil
`user.views.account`
Em construção

----------------
## Alteração de Senha
`user.views.recover_password`

**A instância Gitlab necessita de Postfix para envio de emails de recuperação de senha.**

```python
'user[email]': form.email.data,
'authenticity_token': recover_token,
```

O email do usuário e o token de autenticidade do formulário são submetidos à página de recuperação de senha do Gitlab.
