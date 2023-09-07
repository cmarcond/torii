# Informações Armazenadas no Redis
`app.py`

<hr>
`job_status`

Dados da forma `{key: value} = {project_uuid: status}`, usado para monitorar o status de processamento do projeto submetido. Atualmente, pode assumir os seguintes estados:
- `started` : logo depois de iniciar uma thread de submissão (por upload, github ou gitlab).
- `running` : após a importação do projeto no Gitlab e o início da execução do pipeline.
- `getting` : busca de relatório no Kata.
- `done` : relatório gerado com sucesso.

Erros:
- `upload import error` : erro de submissão de projeto por upload, por algum outro motivo.
- `branch error` , `gitlab branch error` : quando não há ramo master/main no repositório Github ou Gitlab original. *(alterar para encontrar ramo default)*
- `invalid repo language` : linguagem de projeto não suportada. *(alterar)*
- `naming error` : nome de projeto já utilizado.
- `github credential error` : token de acesso pessoal Github inválida.
- `repo not found` : ID de repositório Github inválido.
- `github import error` : erro na submissão de projeto por Github, por algum outro motivo.
- `gitlab credential error` : credenciais de acesso ao repositório Gitlab de origem incorretas.
- `gitlab clone error` : erro na clonagem de repositório Gitlab.
- `gitlab ci file error` : o projeto Gitlab de origem já possui um arquivo `.gitlab-ci.yml`. *(Alterar para atualizar o arquivo ci)*
- `gitlab clone error` : erro na submissão de projeto por outra instância Gitlab, por algum outro motivo.
- `report error` : erro na geração / busca de relatório após execução do pipeline.
- `empty report` : relatório em branco. *(Verificar se não há vulnerabilidades, e, em caso afirmativo, gerar relatório em branco, em vez de mensagem de erro)*
- `processing error` : erro no processamento do relatório.
- `project error` : *(Incluir)*


Do script em `upload.html`, após o projeto entrar no estado `started`, um popup é mostrado na tela, informando que o projeto está sendo importado. No estado `running`, o usuário é redirecionado para a página de pré-relatório (`pre_report.html`), com uma mensagem informando que o relatório está sendo gerado.

Após a conclusão da análise do projeto, o relatório é carregado na tela, e o uuid e status do projeto são excluídos do banco de dados. Os uuids de projeto também são deletados após detecção de cada status de erro.

------------
`project_info`

Armazena dados referentes a cada projeto, identificado por seu ID no Gitlab SecDevias, em forma de json, conforme a árvore a seguir:

- ID do projeto (Gitlab SecDevias)
	- Nome do projeto
	- Nome do usuário que submeteu
	- Lista de UUIDs/versões: 
		- UUID1
		- UUID2
		-  ...
	- Método de submissão

--------
`report_info`

Armazena informações referentes a cada relatório/UUID de projeto gerado. Note que um mesmo projeto pode ter diferentes versões, cada uma com um relatório e um UUID correspondente. Cada entrada no banco de dados apresenta o seguinte formato:

- UUID
	- Data de submissão
	- Total de vulnerabilidades
	- Severidade das vulnerabilidades:
		- Crítica: Número de vulnerabilidades críticas
		- Alta: ...
		- Média: ...
		- Baixa: ...
		- Informativa: ...
	- Tipos de vulnerabilidades:
		- SAST: Número de vulnerabilidades SAST
		- Container: ...
		- Secrets: ...
		- Análise de Componente: ...
