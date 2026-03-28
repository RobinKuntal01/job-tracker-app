# Job Tracker App

A FastAPI-based job tracking application

## Setup

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Run the application:
   ```bash
   uvicorn app.main:app --reload
   ```

3. Open your browser to `http://127.0.0.1:8000` for the API documentation.

## API Endpoints

- `GET /` - Welcome message
- `GET /api/v1/jobs/` - List jobs
- `POST /api/v1/jobs/` - Create a new job

## Project Structure

```
job-tracker-app/
├── app/
│   ├── __init__.py
│   ├── main.py
│   └── routers/
│       ├── __init__.py
│       └── jobs.py
├── requirements.txt
├── readme.md
└── index.html
```
