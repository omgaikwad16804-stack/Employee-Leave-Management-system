from datetime import date, datetime
from pydantic import BaseModel, ConfigDict, EmailStr, Field

from .models import LeaveStatus, LeaveType, Role


class EmployeeCreate(BaseModel):
    employee_code: str = Field(min_length=2, max_length=30)
    name: str
    email: EmailStr
    password: str = Field(min_length=8)
    department: str
    designation: str
    joining_date: date
    role: Role = Role.EMPLOYEE
    manager_id: int | None = None


class EmployeeUpdate(BaseModel):
    name: str | None = None
    email: EmailStr | None = None
    department: str | None = None
    designation: str | None = None
    role: Role | None = None
    manager_id: int | None = None
    is_active: bool | None = None


class EmployeeResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    employee_code: str
    name: str
    email: EmailStr
    department: str
    designation: str
    joining_date: date
    role: Role
    manager_id: int | None
    is_active: bool


class RegisterRequest(EmployeeCreate):
    pass


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class LeaveBalanceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    employee_id: int
    casual_leave: int
    sick_leave: int
    earned_leave: int


class LeaveApplication(BaseModel):
    leave_type: LeaveType
    start_date: date
    end_date: date
    reason: str = Field(min_length=3, max_length=500)


class LeaveDecision(BaseModel):
    status: LeaveStatus
    manager_comment: str | None = Field(default=None, max_length=500)


class LeaveResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    employee_id: int
    leave_type: LeaveType
    start_date: date
    end_date: date
    days: int
    reason: str
    status: LeaveStatus
    manager_comment: str | None
    approved_by: int | None
    created_at: datetime
    updated_at: datetime


class LeaveReport(BaseModel):
    total_requests: int
    pending: int
    approved: int
    rejected: int
    cancelled: int
    total_days_approved: int
