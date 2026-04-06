# Job Tracker App

A FastAPI-based job tracking application for managing job applications and user authentication.

## Features

- User registration and login with JWT authentication
- Create, read, update, and delete job applications
- Job statistics endpoint
- Static frontend served from `templates/index.html`
- MongoDB-backed persistence
- Gmail test endpoint for email integration checks

## Requirements

- Python 3.11+
- MongoDB running locally or remotely
- Python packages from `requirements.txt`

## Setup

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Create a `.env` file if you want to override default settings:
   ```env
   MONGODB_URI=mongodb://localhost:27017
   MONGODB_DATABASE=jobtracker
   SECRET_KEY=your-secret-key
   DEBUG=True
   ```

3. Run the application:
   ```bash
   uvicorn app.main:app --reload
   ```

4. Open your browser to `http://127.0.0.1:8000` for the API docs and root HTML page.

## API Endpoints

### Authentication

- `POST /api/v1/auth/register` - Register a new user
- `POST /api/v1/auth/login` - Log in and receive a bearer token

### Jobs

- `GET /api/v1/jobs/{user_id}` - List jobs for a specific user
- `POST /api/v1/jobs` - Create a new job application
- `GET /api/v1/jobs/{job_id}` - Get a single job application by ID
- `PUT /api/v1/jobs/{job_id}` - Update a job application
- `DELETE /api/v1/jobs/{job_id}` - Delete a job application
- `GET /api/v1/stats` - Get job application statistics

### Utilities

- `GET /` - Serve the frontend HTML page from `templates/index.html`
- `GET /test-gmail` - Test Gmail integration endpoint

## Authentication

Most protected endpoints require a bearer token in the `Authorization` header:

```http
Authorization: Bearer <access_token>
```

## Project Structure

```
job-tracker-app/
├── app/
│   ├── __init__.py
│   ├── config.py
│   ├── db_operations.py
│   ├── db_processor.py
│   ├── main.py
│   ├── models.py
│   └── routers/
│       ├── __init__.py
│       ├── auth.py
│       └── jobs.py
├── static/
│   ├── script.js
│   └── styles.css
├── templates/
│   └── index.html
├── requirements.txt
├── readme.md
└── index.html
```

## Notes

- The app uses JWT tokens with `SECRET_KEY` from the environment or `.env`.
- MongoDB defaults to `mongodb://localhost:27017` and database `jobtracker`.
- Static files are mounted under `/static`.
