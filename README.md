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

## Status

Research prototype from 2023, published as a record of the work. It is not
maintained and has not been hardened for production: for example, it talks to
the internal GitLab without verifying TLS certificates. The sample reports under
`Dev/devias/report/stored_reports/` come from scans of public test targets.
The commit history is the original one, with credentials replaced by
placeholders.
