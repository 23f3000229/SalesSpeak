# SalesSpeak — Sales & Inventory Management (Local + Replit-ready)

Quick start instructions for running locally and notes about deployment.

Prerequisites
- Python 3.11+
- Git (optional)

Local setup (recommended)

1. Create a virtual environment and activate it (PowerShell):

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

2. Install dependencies:

```powershell
pip install -r requirements.txt
```

3. Provide Google Sheets credentials:
- Recommended: create a Google service account, give it access to the target spreadsheet, and set `GOOGLE_APPLICATION_CREDENTIALS` to the JSON key path. Or set `SERVICE_ACCOUNT_JSON` env var with the JSON content.
- You can copy `.env.example` to `.env` and fill values.

4. Run Streamlit:

```powershell
streamlit run app.py
```

Notes about Replit
- The project includes Replit connector support (used when no local credentials are present). Deploying to Replit can use its connectors and environment variables (`REPL_IDENTITY`).

Developer notes
- The code is being modularized under `src/features/*` and `src/core/*`.
- `src/core/sheets_manager.py` supports both service-account local auth and Replit connector fallback.
