# Versionamento e Ressubmissão de Projetos
**v0.1**

## Ressubmissão
`projects.views.resubmit`
Armazena os tokens necessários para ressubmeter projetos Github e Gitlab.
Para projetos Github, é necessário que o usuário gere e informe um token de acesso fino, que dá permissões de leitura do repositório desejado.

```python
token = github_token_form.token.data
project["repo_access_token"] = token
```

Para projetos Gitlab, são necessários um "deploy token" e um nome de usuário para o "deploy token".

```python 
token_username = gitlab_token_form.token_username.data
deploy_token = gitlab_token_form.token.data

project["deploy_token_username"] = token_username
project["deploy_token"] = deploy_token
```

--------------
## Dashboard de Projeto
`projects.views.project_page`
Para o projeto selecionado, os UUIDs e os relatórios referentes a cada versão submetida são armazenados e passados para o template de dashboard.

O dashboard contém uma listagem de todas as versões submetidas do projeto, com vulnerabilidades separadas por severidade para cada versão, links de acesso para o relatório de cada versão, bem como um log de modificações (em construção).

------------
## Webhooks
`projects.views.gitlab_hook`
`projects.views.github_hook`

As páginas `app.secdevias.com/gitlab_hook` e `app.secdevias.com/github_hook` são informadas nas opções de Webhook nos repositórios Gitlab e Github de origem, respectivamente. Desse modo, quando o projeto é atualizado, o Gitlab ou o Github irá enviar uma requisição à URL correspondente.

Gitlab:
```python
webhook_token = request.headers["X-Gitlab-Token"]
```

Github:
```python
encrypted_token = request.headers["x-hub-signature-256"]
```

--------------
#### Resubmissão Gitlab
`projects.resubmit.gitlab_resubmit`
Após acionado o webhook, caso o usuário tenha feito as configurações corretamente, o token do webhook deve corresponder ao UUID do projeto desejado. Desse modo, inicialmente realiza-se a determinação do projeto a ser ressubmetido.

```python
for key in project_info.keys():
	if webhook_token in project_info[key]:
		project_id = key
		project = project_info.get(project_id)
		break
```

Então, usando o *deploy token* e o nome de usuário do *deploy token* fornecidos pelo usuário, o repositório original é clonado e ressubmetido à instância Gitlab SecDevias. 

```python
deploy_token_username = project["deploy_token_username"]
deploy_token = project["deploy_token"]

source_repo_URL = request["project"]["git_http_url"]
split_URL = source_repo_URL.split("//")
clone_URL = f"{split_URL[0]}//{deploy_token_username}:{deploy_token}@{split_URL[1]}"
```

Por fim, o pipeline de segurança é acionado novamente, e um novo UUID e relatório são gerados para a versão submetida mais recente. Cabe destacar que as informações do novo relatório somente serão armazenadas após o primeiro acesso.

```python
gitlab_project.pipelines.create({'ref': f'{default_branch}', 'variables':[{'key': 'EXECUTE', 'value': 'true'}]})

# Caso não seja a primeira ressubmissão
if type(uuid_list) is dict:
	previous_version = len(uuid_list)
	current_version = int(previous_version) + 1
	uuid_list[f"{current_version}"] = new_uuid

# Caso seja a primeira ressubmissão:
elif type(uuid_list) is str:
	uuid_list = {
		"1": project["uuid"],
		"2": new_uuid,
	}
```

----------------
#### Resubmissão Github
`projects.resubmit.github_resubmit`
Após acionado o webhook, o Github envia uma requisição à URL `/github_hook`, com um header denominado `x-hub-signature-256`, que corresponde à UUID do projeto desejado criptografada em `sha256`.

Desse modo, para determinar o projeto a ser ressubmetido, o header é comparado com a lista de UUIDs de projeto já existentes.

```python
signature_key = bytes(project_uuid, 'utf-8')
expected_signature = hmac.new(key=signature_key, msg=request_data, digestmod=hashlib.sha256).hexdigest()
incoming_signature = encrypted_token.split('sha256=')[-1].strip()
if hmac.compare_digest(incoming_signature, expected_signature):
	project_id = key
	break
```

Então, de modo similar à ressubmissão Gitlab, o repositório original é clonado por meio de um token de acesso e, em seguida, ressubmetido ao Gitlab SecDevias. O procedimento de versionamento de UUIDs e relatórios é semelhante ao descrito anteriormente.

-----------------
## Deletar Projeto
`projects.views.delete`
Exclui um projeto da instância Gitlab, bem como do banco de dados (Redis) que armazena os dados de cada projeto submetido.

```python
exclude_project = gl.projects.get(project_name_with_namespace)
exclude_project.delete()
project_info.delete(f"{exclude_project.id}")
```
