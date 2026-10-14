from datetime import date, datetime
from enum import Enum

from sqlalchemy import Boolean, Date, DateTime, Enum as SAEnum, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .database import Base


class Role(str, Enum):
    EMPLOYEE = "EMPLOYEE"
    MANAGER = "MANAGER"
    ADMIN = "ADMIN"


class LeaveType(str, Enum):
    CASUAL = "CASUAL"
    SICK = "SICK"
    EARNED = "EARNED"
    UNPAID = "UNPAID"


class LeaveStatus(str, Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    CANCELLED = "CANCELLED"


class Employee(Base):
    __tablename__ = "employees"

    id: Mapped[int] = mapped_column(primary_key=True)
    employee_code: Mapped[str] = mapped_column(String(30), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(120))
    email: Mapped[str] = mapped_column(String(150), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    department: Mapped[str] = mapped_column(String(100))
    designation: Mapped[str] = mapped_column(String(100))
    joining_date: Mapped[date] = mapped_column(Date)
    role: Mapped[Role] = mapped_column(SAEnum(Role), default=Role.EMPLOYEE)
    manager_id: Mapped[int | None] = mapped_column(ForeignKey("employees.id"), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    manager: Mapped["Employee | None"] = relationship(
        remote_side=[id],
        back_populates="team",
    )
    team: Mapped[list["Employee"]] = relationship(back_populates="manager")
    balance: Mapped["LeaveBalance | None"] = relationship(
        back_populates="employee",
        uselist=False,
        cascade="all, delete-orphan",
    )
    leave_requests: Mapped[list["LeaveRequest"]] = relationship(
        back_populates="employee",
        foreign_keys="LeaveRequest.employee_id",
        cascade="all, delete-orphan",
    )
    decisions: Mapped[list["LeaveRequest"]] = relationship(
        back_populates="approver",
        foreign_keys="LeaveRequest.approved_by",
    )


class LeaveBalance(Base):
    __tablename__ = "leave_balances"

    id: Mapped[int] = mapped_column(primary_key=True)
    employee_id: Mapped[int] = mapped_column(ForeignKey("employees.id"), unique=True)
    casual_leave: Mapped[int] = mapped_column(default=12)
    sick_leave: Mapped[int] = mapped_column(default=10)
    earned_leave: Mapped[int] = mapped_column(default=15)

    employee: Mapped[Employee] = relationship(back_populates="balance")


class LeaveRequest(Base):
    __tablename__ = "leave_requests"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    employee_id: Mapped[int] = mapped_column(ForeignKey("employees.id"), index=True)
    leave_type: Mapped[LeaveType] = mapped_column(SAEnum(LeaveType))
    start_date: Mapped[date] = mapped_column(Date)
    end_date: Mapped[date] = mapped_column(Date)
    days: Mapped[int] = mapped_column(Integer)
    reason: Mapped[str] = mapped_column(String(500))
    status: Mapped[LeaveStatus] = mapped_column(
        SAEnum(LeaveStatus), default=LeaveStatus.PENDING, index=True
    )
    manager_comment: Mapped[str | None] = mapped_column(String(500))
    approved_by: Mapped[int | None] = mapped_column(ForeignKey("employees.id"))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    employee: Mapped[Employee] = relationship(
        back_populates="leave_requests",
        foreign_keys=[employee_id],
    )
    approver: Mapped[Employee | None] = relationship(
        back_populates="decisions",
        foreign_keys=[approved_by],
    )
