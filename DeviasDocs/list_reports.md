# Listagem de Projetos Submetidos
**v0.1**

`list_reports.views.user_reports`
Lista todos os projetos submetidos pelo usuário, com paginação - 20 projetos são retornados por vez.

```python
	items = gl.projects.list(owned=True, as_list=False, page=page_number, per_page=20)
```

