# Job Application Tracker (Azure-ready)

A Flask web app for tracking job applications, recruiter interactions, and benchmarking recruiter performance.

## Features

- Track applications by company, role, and status.
- Track recruiter contacts and interaction history.
- Dashboard with status counts and a recruiter benchmark leaderboard.
- Recruiter score model to compare quality of recruiter engagement.

## Local run

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
flask --app app.py init-db
python app.py
```

Open http://localhost:8000

## Azure App Service deployment

1. Create an Azure Web App (Python 3.11 runtime).
2. Configure startup command:
   ```bash
   gunicorn --bind=0.0.0.0:$PORT app:app
   ```
3. Add app setting `SCM_DO_BUILD_DURING_DEPLOYMENT=true`.
4. Deploy with Azure CLI:
   ```bash
   az webapp up --name <your-app-name> --runtime "PYTHON:3.11" --sku B1
   ```

## Recommended production upgrades

- Move from SQLite to Azure Database for PostgreSQL.
- Add authentication (Microsoft Entra ID).
- Add migration tooling (Alembic).
- Add background tasks/notifications for follow-ups.
