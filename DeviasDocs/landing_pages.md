# Páginas Iniciais
**v0.1**

## Home
`landing_pages.views.show`

Caso o usuário não esteja logado, a página inicial mostrada consiste apenas em uma tela padrão com o nome da aplicação (SecDevias).

Caso contrário, são mostradas uma mensagem de boas-vindas e estatísticas de projeto.

---------------------
## Estatísticas Recentes
`landing_pages.project_stats.get_recent_stats`
Contabiliza a quantidade de vulnerabilidades por tipo e por severidade de todos os projetos submetidos nos últimos 30 dias. Essas informações são utilizadas na geração dos *PieCharts* da página inicial.

Por exemplo, o código a seguir, em JavaScript, descreve a geração do gráfico de vulnerabilidades por tipo.

```js
function drawVulnTypesChart() {
	var data = google.visualization.arrayToDataTable([
		["Tipo de Vulnerabilidade", "Quantidade"],
		["SAST", parseInt("{{ recent_stats['types']['SAST'] }}")],
		["Secrets", parseInt("{{ recent_stats['types']['secrets'] }}")],
		["Containers", parseInt("{{ recent_stats['types']['containers'] }}")],
		["SCA", parseInt("{{ recent_stats['types']['component'] }}")],
	]);

	// ...

	var chart = new google.visualization.PieChart(document.getElementById('vulntypeschart'));
	chart.draw(data, options);
}
```

-----------
#### Projetos Submetidos por Data
`landing_pages.project_stats.get_all_project_dates`
Lista todos os projetos submetidos, acessa as datas de submissão de cada projeto e armazena as informações em um dicionário, em que cada chave corresponde a uma data (formatada) e cada valor ao respectivo número de projetos submetidos naquela data.

Esse dicionário é utilizado para gerar um gráfico de calendário na página inicial, conforme o trecho de código (em JavaScript) a seguir.

```js
function drawCalendar() {
	var dataTable = new google.visualization.DataTable();
	dataTable.addColumn({ type: 'date', id: 'Date' });7
	dataTable.addColumn({ type: 'number', id: 'Projects' });

	json = '{{dates | safe}}';
	var dates = JSON.parse(json);

	var calendar_rows = [];
	for (var date in dates) {
		calendar_rows.push([new Date(date), parseInt(dates[date])]);
	}

	dataTable.addRows(calendar_rows);

	var chart = new google.visualization.Calendar(document.getElementById('submitcalendar'));

	// ...

	chart.draw(dataTable, options);
}
```

-----------
#### Formatação de Data
`landing_pages.project_stats.format_date_time`
Modifica as datas para o formato "YYYY-MM-DD", para compatibilidade com calendário Google.

--------------------
#### Projetos Recentes
`landing_pages.project_stats.get_recent_projects`
`landing_pages.project_stats.get_uuid_list`
`landing_pages.project_stats.get_report_info`
Lista os IDs dos projetos submetidos nos últimos 30 dias. A partir dos IDs, são extraídos os UUIDs da versão mais recente de cada projeto e, assim, os relatórios gerados mais recentemente para cada projeto.
