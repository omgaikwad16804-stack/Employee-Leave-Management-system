from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..auth import hash_password
from ..database import get_db
from ..dependencies import get_current_user, require_roles
from ..models import Employee, LeaveBalance, Role
from ..schemas import EmployeeCreate, EmployeeResponse, EmployeeUpdate, LeaveBalanceResponse

router = APIRouter(prefix="/employees", tags=["Employees"])


@router.post("", response_model=EmployeeResponse, status_code=201)
def create_employee(
    payload: EmployeeCreate,
    db: Session = Depends(get_db),
    _: Employee = Depends(require_roles(Role.ADMIN)),
):
    if db.scalar(select(Employee).where(Employee.employee_code == payload.employee_code)):
        raise HTTPException(409, "Employee code already exists")
    if db.scalar(select(Employee).where(Employee.email == payload.email)):
        raise HTTPException(409, "Email already exists")

    employee = Employee(
        **payload.model_dump(exclude={"password"}),
        password_hash=hash_password(payload.password),
    )
    employee.balance = LeaveBalance()
    db.add(employee)
    db.commit()
    db.refresh(employee)
    return employee


@router.get("", response_model=list[EmployeeResponse])
def list_employees(
    db: Session = Depends(get_db),
    _: Employee = Depends(get_current_user),
):
    return db.scalars(select(Employee).order_by(Employee.id)).all()


@router.get("/{employee_id}", response_model=EmployeeResponse)
def get_employee(
    employee_id: int,
    db: Session = Depends(get_db),
    current: Employee = Depends(get_current_user),
):
    if current.id != employee_id and current.role not in [Role.ADMIN, Role.MANAGER]:
        raise HTTPException(403, "Not authorized")
    employee = db.get(Employee, employee_id)
    if not employee:
        raise HTTPException(404, "Employee not found")
    return employee


@router.put("/{employee_id}", response_model=EmployeeResponse)
def update_employee(
    employee_id: int,
    payload: EmployeeUpdate,
    db: Session = Depends(get_db),
    _: Employee = Depends(require_roles(Role.ADMIN)),
):
    employee = db.get(Employee, employee_id)
    if not employee:
        raise HTTPException(404, "Employee not found")

    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(employee, key, value)

    db.commit()
    db.refresh(employee)
    return employee


@router.delete("/{employee_id}", status_code=204)
def delete_employee(
    employee_id: int,
    db: Session = Depends(get_db),
    _: Employee = Depends(require_roles(Role.ADMIN)),
):
    employee = db.get(Employee, employee_id)
    if not employee:
        raise HTTPException(404, "Employee not found")
    employee.is_active = False
    db.commit()


@router.get("/{employee_id}/balance", response_model=LeaveBalanceResponse)
def get_balance(
    employee_id: int,
    db: Session = Depends(get_db),
    current: Employee = Depends(get_current_user),
):
    if current.id != employee_id and current.role not in [Role.ADMIN, Role.MANAGER]:
        raise HTTPException(403, "Not authorized")
    employee = db.get(Employee, employee_id)
    if not employee or not employee.balance:
        raise HTTPException(404, "Employee/balance not found")
    return employee.balance
