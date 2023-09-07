**v0.1**

# Submissão por Zip
`submit_code.views.upload_code`

Após o usuário submeter um projeto .zip, é gerado um uuid (ientificador único) para identificar o projeto.
`project_uuid = uuid.uuid4().hex`

O nome do arquivo é corrigido para uma string segura por meio da função `wekzeug.utils.secure_filename`. Em seguida, é criado um diretório no mesmo local da aplicação, com nome do uuid do projeto, e o .zip é salvo nele. O nome de projeto submetido pelo usuário é modificado para ser representado em url.

Então, realiza-se uma conexão Gitlab, usando o token de acesso pessoal salvo na sessão, e é criado um projeto na conta do usuário, com o mesmo nome submetido no formulário.
```python
gl = gitlab.Gitlab(config.URL, private_token=session['private_token'], api_version=4, ssl_verify=False)

project = gl.projects.create({'name': zip_project_name})
```

Caso o usuário já tenha um projeto com esse nome, a submissão é interrompida, o usuário é redirecionado para a página de submissão, e aparece uma mensagem de erro.

Caso contrário, é criada uma thread para processar o restante da submissão em background. Nesse instante a variável global `config.job_status[f'{project_uuid}']` é configurada em "started".

A página `upload_in_progress.html` é renderizada enquanto o processamento acontece no fundo.

------------
## Processamento da Submissão em Background
`submit_code.views.process_upload_submission`

Inicia extraindo o arquivo .zip, em uma pasta com mesmo nome do arquivo submetido:
```python
extracted_folder = os.path.splitext(filename)[0]

extracted_folder_path = os.path.join(temp_dir,extracted_folder)

with zipfile.ZipFile(file_path,"r") as zip_ref:
	zip_ref.extractall(extracted_folder_path)

```

Depois, inicializa um repositório GIT na pasta extraída. 
```python
repo = Repo.init(path=extracted_folder_path)
```

O repo remoto ('origin') é configurado como um URL com formato:
`http://Tester1:PWD@gitlab.secdevias.com/Tester1/project_name.git`

Então, são realizados os comandos `git add .`, `git commit`, `git push`, para importar os conteúdos na pasta extraída para o projeto Gitlab.
```python
repo.git.add(all=True)
repo.index.commit('Upload do projeto no Gitlab.')
repo.remotes.origin.push(refspec='master:master', env={'GIT_SSL_NO_VERIFY': '1'})
```

Depois que a importação do projeto é finalizada, o diretório temporário é excluído.

Então, são chamadas as funções de análise e configuração de pipeline do projeto, e o pipeline é executado. Para tal, a variável `EXECUTE` tem valor estabelecido em `true`.
```python
languages = project_languages(project)
file = gitlab_ci_write(languages,project_uuid)

create_commit(file,project,branch="master")
project.pipelines.create({'ref': 'master', 'variables':[{'key': 'EXECUTE', 'value': 'true'}]})
```

Com a inicialização do pipeline, a variável `config.job_status[f'{project_uuid}']` é configurada para "running".

-------------------
##### Escrita do arquivo .gitlab-ci.yml
`submit_code.utils.gitlab_ci_write`

O arquivo de configuração de pipeline `.gitlab-ci.yml` é escrito, com a inclusão de um arquivo `<language>-gitlab-ci.yaml`, presente no projeto `secdevias/ci-templates`, para cada linguagem encontrada no projeto, caso o projeto contenha Python ou Java. A função retorna o `.gitlab-ci.yml` modificado.

Caso o projeto não contenha nem Python nem Java, a função retorna `None`, e a variável `config.job_status[f'{project_uuid}']` é configurada em "invalid upload language".

------------------
##### Commit do arquivo .gitlab-ci.yml
`submit_code.utils.create_commit`

Recebe o arquivo `.gitlab-ci.yml` e faz o commit dele no projeto Gitlab, no ramo `master`.

------------------
##### Mudança de nome de projeto para compatibilidade com URL
`submit_code.utils.urlify`

Essa função muda nomes com espaços em branco, letras maiúsculas, acentos e outros símbolos em strings com apenas letras minúsculas, números e traços ("-").

------------------
# Submissão por Clonagem de Repositorio Github
`submit_code.views.clone_repo`

O usuário deve submeter:
- Token de acesso pessoal Github,
- ID do repositório a ser clonado,
- Nome do projeto.

Com essas informações, é gerado um uuid para identificar o projeto, bem como um nome compatível com URL a partir do nome de projeto fornecido. 

Além disso, é realizada uma conexão Gitlab, que será passada para o processamento em background. 
```python
gl = gitlab.Gitlab(config.URL, private_token=session['private_token'], api_version=4, ssl_verify=False)
```

Caso a conexão Gitlab e/ou o nome de projeto sejam `None`, o usuário é redirecionado para a submissão, com uma mensagem de erro de importação.

Caso contrário, a variável `config.job_status[f'{project_uuid}']` é configurada para "started". Então, é iniciado o processamento em background.

---------------
## Processamento da Submissão em Background
`submit_code.views.process_github_submission`

Inicia-se a importação do repositório para o Gitlab, fazendo uso da conexão Gitlab estabelecida anteriormente. A função verifica periodicamente se a importação foi concluída, e acessa o projeto em caso afirmativo. 

```python
result = gl.projects.import_github(personal_access_token=access_token,repo_id=repo_id,target_namespace=project_namespace,new_name=project_name)

project = gl.projects.get(result['id'])

print("Waiting for import to complete")

while project.import_status == u'started':
	time.sleep(1.0)
	project = gl.projects.get(project.id)
	
print("Github import complete")
```

Então, de modo similar à submissão de código por upload, é escrito o arquivo `.gitlab-ci.yml`.

Antes de realizar o commit deste arquivo no projeto Gitlab, é preciso determinar o ramo principal do projeto Github original (dependendo de quando o projeto foi criado, pode ser `master` ou `main`). Caso não seja encontrado nenhum ramo com estes nomes, a variável `config.job_status[f'{project_uuid}']` retorna "branch error".

Após determinar o ramo, é realizado o commit do arquivo `.gitlab-ci.yml` no projeto, e a pipeline é executada. Com sucesso, o `job_status` é configurado para "running", e o usuário é redirecionado para a página de coleta de relatório.

As exceções configuradas atualmente são:
- "naming error": se o usuário já tiver um projeto de mesmo nome,
- "github credential error": se o token de acesso pessoal Github não for válido,
- "repo not found": se o ID do repositório não existir.
- "github import error": se ocorrer algum outro erro na importação.

--------------------
# Submissão por Clonagem de Projeto Gitlab
`submit_code.views.clone_gitlab`

O usuário deve informar:
- suas credenciais do Gitlab de origem,
- a URL do repositório Gitlab de origem,
- nome do projeto.

Inicialmente, verifica-se a URL informada, certificando-se que esta termina em ".git". Em seguida, o projeto recebe um UUID, e uma conexão Gitlab é estabelecida. O status de projeto é configurado como "started".

-----------------
## Processamento em Background
`submit_code.views.process_gitlab_submission`
Inicialmente, cria um diretório com nome igual ao UUID do projeto, e clona o repositório Gitlab de origem para esse local.

```python
repo = Repo.clone_from(auth_repo_URL, temp_dir)
repo.delete_remote("origin")

new_remote_url = f"http://{session['user']['username']}:{session['private_token']}@{config.BARE_URL}/{session['user']['username']}/{project_name}.git"
origin = repo.create_remote('origin',url=new_remote_url)
```

Caso não haja erros de credenciamento nem de clonagem, o arquivo `.gitlab-ci.yml` é escrito, e, de modo semelhante aos procedimentos descritos anteriormente, o pipeline de segurança é acionado, e o status de projeto é configurado para "running".

---------------
# Status de Projeto
`submit_code.views.get_job_status`
`submit_code.views.delete_job_status`

As funções `get_job_status` e `delete_job_status` são invocadas para consultar e deletar o status do projeto desejado, respectivamente. Mais informações sobre os status de projeto estão descritas na página [[Redis]]. 

----------------
#### Informações de Projeto
`submit_code.utils.write_project_info`
Reúne as seguintes informações de projeto em um dicionário:
- Nome do usuário (Gitlab) que submeteu o projeto,
- Nome do projeto,
- Lista de UUIDs/versões,
- Método de submissão (zip, Github ou Gitlab),
- URL do repositório de origem,
- Token de acesso do projeto (Github ou Gitlab).