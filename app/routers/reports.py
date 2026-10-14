from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..database import get_db
from ..dependencies import require_roles
from ..models import Employee, LeaveRequest, LeaveStatus, Role
from ..schemas import LeaveReport

router = APIRouter(prefix="/reports", tags=["Reports"])


@router.get("/leave-summary", response_model=LeaveReport)
def leave_summary(
    db: Session = Depends(get_db),
    _: Employee = Depends(require_roles(Role.MANAGER, Role.ADMIN)),
):
    requests = db.scalars(select(LeaveRequest)).all()

    return LeaveReport(
        total_requests=len(requests),
        pending=sum(r.status == LeaveStatus.PENDING for r in requests),
        approved=sum(r.status == LeaveStatus.APPROVED for r in requests),
        rejected=sum(r.status == LeaveStatus.REJECTED for r in requests),
        cancelled=sum(r.status == LeaveStatus.CANCELLED for r in requests),
        total_days_approved=sum(
            r.days for r in requests if r.status == LeaveStatus.APPROVED
        ),
    )


@router.get("/department-summary")
def department_summary(
    db: Session = Depends(get_db),
    _: Employee = Depends(require_roles(Role.MANAGER, Role.ADMIN)),
):
    employees = db.scalars(select(Employee)).all()
    requests = db.scalars(select(LeaveRequest)).all()

    result = {}
    employee_department = {e.id: e.department for e in employees}

    for request in requests:
        department = employee_department.get(request.employee_id, "UNKNOWN")
        if department not in result:
            result[department] = {
                "total_requests": 0,
                "approved_requests": 0,
                "approved_days": 0,
            }

        result[department]["total_requests"] += 1
        if request.status == LeaveStatus.APPROVED:
            result[department]["approved_requests"] += 1
            result[department]["approved_days"] += request.days

    return result
