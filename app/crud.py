from datetime import date

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from .auth import hash_password, verify_password
from .models import Employee, LeaveBalance, LeaveRequest, LeaveStatus, LeaveType
from .services import calculate_days, available_balance, deduct_balance, validate_no_overlap


def create_employee(db: Session, data):
    if db.scalar(select(Employee).where(Employee.employee_code == data.employee_code)):
        raise HTTPException(409, "Employee code already exists")
    if db.scalar(select(Employee).where(Employee.email == data.email)):
        raise HTTPException(409, "Email already exists")

    employee = Employee(
        **data.model_dump(exclude={"password"}),
        password_hash=hash_password(data.password),
    )
    employee.balance = LeaveBalance()
    db.add(employee)
    db.commit()
    db.refresh(employee)
    return employee


def authenticate(db: Session, email: str, password: str):
    user = db.scalar(select(Employee).where(Employee.email == email))
    if not user or not verify_password(password, user.password_hash):
        return None
    return user


def apply_leave(db: Session, employee: Employee, data):
    days = calculate_days(data.start_date, data.end_date)
    validate_no_overlap(db, employee.id, data.start_date, data.end_date)

    if data.leave_type != LeaveType.UNPAID:
        available = available_balance(employee.balance, data.leave_type)
        if days > available:
            raise HTTPException(
                400,
                f"Insufficient balance. Available {data.leave_type.value}: {available}",
            )

    leave = LeaveRequest(
        employee_id=employee.id,
        leave_type=data.leave_type,
        start_date=data.start_date,
        end_date=data.end_date,
        days=days,
        reason=data.reason,
    )
    db.add(leave)
    db.commit()
    db.refresh(leave)
    return leave


def decide_leave(db: Session, manager: Employee, leave_id: int, decision):
    leave = db.get(LeaveRequest, leave_id)
    if not leave:
        raise HTTPException(404, "Leave request not found")

    employee = db.get(Employee, leave.employee_id)
    if employee.manager_id != manager.id and manager.role.value != "ADMIN":
        raise HTTPException(403, "You are not authorized to decide this leave")

    if leave.status != LeaveStatus.PENDING:
        raise HTTPException(400, "Only pending requests can be decided")

    if decision.status == LeaveStatus.APPROVED and leave.leave_type != LeaveType.UNPAID:
        available = available_balance(employee.balance, leave.leave_type)
        if leave.days > available:
            raise HTTPException(400, "Insufficient leave balance at approval time")
        deduct_balance(employee.balance, leave.leave_type, leave.days)

    if decision.status not in [LeaveStatus.APPROVED, LeaveStatus.REJECTED]:
        raise HTTPException(400, "Status must be APPROVED or REJECTED")

    leave.status = decision.status
    leave.manager_comment = decision.manager_comment
    leave.approved_by = manager.id

    db.commit()
    db.refresh(leave)
    return leave
