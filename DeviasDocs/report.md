# Busca e Renderização de Relatórios
**v0.1**

## Busca
`report.views.get`
Inicialmente, estabelece uma conexão Gitlab e busca o UUID do projeto no repositório. Em seguida, envia requisições à API Kata para buscar o relatório, em intervalos de 20 segundos e limite de 50 requisições (totalizando tempo de espera máximo de em torno de 30 minutos). Durante esse tempo o status de projeto é configurado em "getting".

```python
report_URL = f"{config.KATA_URL}{project_uuid}"
s = requests.Session()

while tries < max_retries:
	req = s.get(report_URL)

	if req.status_code == 200:
		match = re.findall(r'"number_findings": [0-9]+', req.text)
		if match is not None:
			findings = re.findall(r'[0-9]+', match[0])
			if findings[0] != '0':
				break
				
	time.sleep(20)
```

Caso o número de tentativas atinja o limite estabelecido, o status do projeto é configurado como "erro de relatório", caso o Kata retorne códigos 500 ou 405; ou "relatório em branco", caso o Kata retorne codigo 200.

```python
if tries == max_retries:
	if req.status_code == 500 or req.status_code == 405:
		job_status.set(f'{project_uuid}','report error')

	elif req.status_code == 200:
		job_status.set(f'{project_uuid}','empty report')
```

Por outro lado, caso o Kata retorne 200, dentro do tempo máximo, o status de projeto é alterado para "done", e a função de renderizar relatório é chamada.

------------
## Renderização
`report.views.show`
Inicialmente, busca o relatório `project_uuid.json` localmente. Caso o relatório não tenha sido salvo, a função de busca de relatório é invocada.

```python
script_dir = os.path.dirname(__file__)
rel_path = f"stored_reports/{project_uuid}.json"
abs_file_path = os.path.join(script_dir,rel_path)

try:
	file = open(abs_file_path, "r")
except FileNotFoundError:
	return redirect(url_for('report.get', project_name=project_name))
```

Então, são extraídas as vulnerabilidades por tipo e por severidade. Essas informações são enviadas ao template html que renderiza o relatório, e o status de projeto é excluído ao fim do processamento.

```python    
vuln_report = format_report_vuln(data)
SAST_report, Containers_report, Secrets_report, Component_report = vuln_report[0:4]

sev_report = format_report_sev(data)
Critical, High, Medium, Low, Info = sev_report[0:5]
```

---------------
#### Formatação de Vulnerabilidades
`report.utils.format_report_vuln`
`report.utils.format_report_sev`

As funções listadas separam as vulnerabilidades encontradas, agrupando por tipo (`format_report_vuln`) e por severidade (`format_report_sev`).

```python
for item in range(data['number_findings']):
	if data[str(item)]['type'] == 'SAST':
		SAST_report.append(data[str(item)])
	elif data[str(item)]['type'] == 'CONTAINERS':
		Containers_report.append(data[str(item)])
	elif data[str(item)]['type'] == 'SECRETS':
		Secrets_report.append(data[str(item)])
	elif data[str(item)]['type'] == 'COMPONENT':
		Component_report.append(data[str(item)])
```

```python
for item in range(data['number_findings']):
	if data[str(item)]['severity'] == 'Crítica':
		Critical.append(data[str(item)])
	elif data[str(item)]['severity'] == 'Alta':
		High.append(data[str(item)])
	elif data[str(item)]['severity'] == 'Média':
		Medium.append(data[str(item)])
	elif data[str(item)]['severity'] == 'Baixa':
		Low.append(data[str(item)])
	elif data[str(item)]['severity'] == 'Informativa':
		Info.append(data[str(item)])
```

----------------
#### Estatísticas de Relatório
`report.utils.write_report_info`
Reúne as informações do relatório em um dicionário, incluindo data e horário de submissão, total de vulnerabilidades e número de vulnerabilidades de cada tipo e de cada severidade.

```python
project = {
	"date": date_time,
	"number_findings": f"{data['number_findings']}",
	"severity_types": {
		"critical": f"{len(Critical)}",
		"high": f"{len(High)}",
		"medium": f"{len(Medium)}",
		"low": f"{len(Low)}",
		"info": f"{len(Info)}",
	},

	"vuln_types": {
		"SAST": f"{len(SAST_report)}",
		"containers": f"{len(Containers_report)}",
		"secrets": f"{len(Secrets_report)}",
		"component": f"{len(Component_report)}",
	},
}
```

