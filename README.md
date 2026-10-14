# Employee Leave Management Backend

Production-style REST API backend for employee leave management.

## Requirements
- Python
- FastAPI
- PostgreSQL
- SQLAlchemy
- JWT Authentication
- Employee CRUD
- Leave applications
- Manager approvals/rejections
- Leave balances
- Reports

## Project Structure

app/
  main.py
  database.py
  models.py
  schemas.py
  auth.py
  dependencies.py
  crud.py
  routers/
    auth.py
    employees.py
    leaves.py
    reports.py

## Setup

1. Install PostgreSQL and create a database:

```sql
CREATE DATABASE leave_management;
```

2. Create a virtual environment:

```bash
python -m venv .venv
```

Windows:
```bash
.venv\Scripts\activate
```

Linux/macOS:
```bash
source .venv/bin/activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Copy `.env.example` to `.env` and update PostgreSQL credentials.

5. Start the application:

```bash
uvicorn app.main:app --reload
```

6. Open Swagger:

http://127.0.0.1:8000/docs

## Default workflow

1. Register an employee/manager using `/auth/register`.
2. Login using `/auth/login`.
3. Copy the JWT access token.
4. Click **Authorize** in Swagger and enter `Bearer <token>`.
5. Employee applies for leave.
6. Manager approves/rejects the request.
7. Approved leave automatically reduces the leave balance.
8. Reports APIs provide leave summaries.

## Roles

- EMPLOYEE: Can view own profile, balance and leave requests; can apply for leave.
- MANAGER: Can view team leave requests and approve/reject them.
- ADMIN: Can manage employees and access reports.

For a real production deployment, use Alembic migrations, HTTPS, secret management, refresh tokens, audit logging and stronger authorization policies.
