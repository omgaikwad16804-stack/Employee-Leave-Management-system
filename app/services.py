from datetime import date
from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from .models import LeaveRequest, LeaveStatus, LeaveType


def calculate_days(start_date: date, end_date: date) -> int:
    if end_date < start_date:
        raise HTTPException(400, "End date cannot be before start date")
    return (end_date - start_date).days + 1


def available_balance(balance, leave_type: LeaveType) -> int:
    if leave_type == LeaveType.CASUAL:
        return balance.casual_leave
    if leave_type == LeaveType.SICK:
        return balance.sick_leave
    if leave_type == LeaveType.EARNED:
        return balance.earned_leave
    return 10**9


def deduct_balance(balance, leave_type: LeaveType, days: int):
    if leave_type == LeaveType.CASUAL:
        balance.casual_leave -= days
    elif leave_type == LeaveType.SICK:
        balance.sick_leave -= days
    elif leave_type == LeaveType.EARNED:
        balance.earned_leave -= days


def validate_no_overlap(db: Session, employee_id: int, start_date: date, end_date: date):
    existing = db.scalar(
        select(LeaveRequest).where(
            LeaveRequest.employee_id == employee_id,
            LeaveRequest.status.in_([LeaveStatus.PENDING, LeaveStatus.APPROVED]),
            LeaveRequest.start_date <= end_date,
            LeaveRequest.end_date >= start_date,
        )
    )
    if existing:
        raise HTTPException(409, "Leave dates overlap an existing request")
