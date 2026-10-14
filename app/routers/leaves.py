from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..crud import apply_leave, decide_leave
from ..database import get_db
from ..dependencies import get_current_user, require_roles
from ..models import Employee, LeaveRequest, LeaveStatus, Role
from ..schemas import LeaveApplication, LeaveDecision, LeaveResponse

router = APIRouter(prefix="/leave-requests", tags=["Leave Management"])


@router.post("", response_model=LeaveResponse, status_code=201)
def create_leave(
    payload: LeaveApplication,
    db: Session = Depends(get_db),
    current: Employee = Depends(get_current_user),
):
    return apply_leave(db, current, payload)


@router.get("", response_model=list[LeaveResponse])
def list_leaves(
    db: Session = Depends(get_db),
    current: Employee = Depends(get_current_user),
):
    if current.role == Role.ADMIN:
        stmt = select(LeaveRequest)
    elif current.role == Role.MANAGER:
        employee_ids = select(Employee.id).where(Employee.manager_id == current.id)
        stmt = select(LeaveRequest).where(
            (LeaveRequest.employee_id.in_(employee_ids)) |
            (LeaveRequest.employee_id == current.id)
        )
    else:
        stmt = select(LeaveRequest).where(LeaveRequest.employee_id == current.id)

    return db.scalars(stmt.order_by(LeaveRequest.created_at.desc())).all()


@router.get("/{leave_id}", response_model=LeaveResponse)
def get_leave(
    leave_id: int,
    db: Session = Depends(get_db),
    current: Employee = Depends(get_current_user),
):
    leave = db.get(LeaveRequest, leave_id)
    if not leave:
        raise HTTPException(404, "Leave request not found")

    employee = db.get(Employee, leave.employee_id)
    allowed = (
        current.role == Role.ADMIN
        or leave.employee_id == current.id
        or employee.manager_id == current.id
    )
    if not allowed:
        raise HTTPException(403, "Not authorized")
    return leave


@router.patch("/{leave_id}/decision", response_model=LeaveResponse)
def decision(
    leave_id: int,
    payload: LeaveDecision,
    db: Session = Depends(get_db),
    current: Employee = Depends(require_roles(Role.MANAGER, Role.ADMIN)),
):
    return decide_leave(db, current, leave_id, payload)
