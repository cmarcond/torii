# Torii: web front end of SecDevias

Torii is the web application of **SecDevias**, a DevSecOps-as-a-service platform
built at ITA (Brazil) with the national research network (RNP). A user submits a
software project, SecDevias scans it for vulnerabilities, and Torii shows the
findings as reports. This repository is the 2023 refactor of that front end.

## What it does

- User registration, login and logout, backed by a GitLab instance.
- Project submission as a zip file or from a GitHub or GitLab repository.
- Webhooks so that a new push triggers a new scan.
- Reports: list, detail view, per-project dashboard and statistics, with a
  heat map of findings per file.
- Resubmission and deletion of submitted projects.

## Layout

| Path | Contents |
|---|---|
| `Dev/devias/` | Flask application: one blueprint per area (`user`, `projects`, `submit_code`, `accept_submission`, `report`, `list_reports`, `landing_pages`) |
| `Dev/devias/tests/` | pytest tests for registration, login and logout |
| `Dev/helm/` | Helm chart to deploy on Kubernetes |
| `Dev/Dockerfile`, `Dev/docker_compose_torii.yml`, `Dev/uwsgi.ini` | Container image and local stack (Torii and Redis) |
| `DeviasDocs/` | Developer notes on each blueprint (in Portuguese) |

## How it fits together

```
 browser ──► Torii (Flask + uWSGI) ──► GitLab          accounts, repositories, mirrors, webhooks
                 │        ▲
                 │        └────────── scanning back end  reports back as a scan progresses
                 ▼
               Redis                                    job status, project data, reports
```

Torii keeps no database of its own. Accounts and repositories live in GitLab,
which Torii drives through its API with the user's own token; a submitted
project becomes a GitLab project (uploaded, or mirrored from GitHub/GitLab), and
a webhook starts a scan on each push. The scanning back end reports
back to Torii, which stores job status, project data and reports in three Redis
databases and renders them.

## Running locally

```sh
cd Dev
export FLASK_SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_hex())")
docker compose -f docker_compose_torii.yml up --build
```

Torii expects a GitLab instance and the SecDevias scanning back end, which are
not part of this repository. Their addresses come from the environment
(`GITLAB_DEVIAS_URL`, `GITLAB_DEVIAS_IP`, `KATA_URL`); passwords come from
`MAIL_PASSWORD` and `REDIS_PASSWORD`. The interface text is in Portuguese.

## Status and known limitations

Research prototype from 2023, published as a record of the work. It is not
maintained. Things I would change before running it anywhere that matters:

- **Session key.** The Flask secret key is generated at start-up, so sessions do
  not survive a restart or work across replicas.
- **Secrets.** Passwords come from environment variables; there is no secret
  store, and the Helm chart does not template them yet.
- **Container.** The image runs as root and its Python dependencies are not
  pinned.
- **Tests.** The tests cover registration, login and logout and need a live
  GitLab; there is no CI.
- **Logging.** The code uses `print` for diagnostics.

The sample reports under `Dev/devias/report/stored_reports/` come from scans of
public test targets. The commit history is the original one, with credentials
replaced by placeholders.
