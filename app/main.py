from fastapi import FastAPI

from .database import Base, engine
from .routers import auth, employees, leaves, reports

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Employee Leave Management Backend",
    version="1.0.0",
    description="FastAPI + PostgreSQL + SQLAlchemy backend with JWT authentication.",
)

app.include_router(auth.router)
app.include_router(employees.router)
app.include_router(leaves.router)
app.include_router(reports.router)


@app.get("/health", tags=["System"])
def health():
    return {"status": "UP", "service": "employee-leave-management"}
