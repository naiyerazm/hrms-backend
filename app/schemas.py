from pydantic import BaseModel, EmailStr
from datetime import date
from typing import List, Optional


# Employee Schemas
class EmployeeBase(BaseModel):
    employee_id: str
    full_name: str
    email: EmailStr
    department: str


class EmployeeCreate(BaseModel):
    full_name: str
    email: EmailStr
    department: str

class EmployeeUpdate(BaseModel):
    full_name: Optional[str] = None
    email: Optional[str] = None
    department: Optional[str] = None

class EmployeeResponse(EmployeeBase):
    id: int

    class Config:
        orm_mode = True


# Attendance Schemas
class AttendanceBase(BaseModel):
    date: date
    status: str  # "Present" or "Absent"


class AttendanceCreate(AttendanceBase):
    pass

class AttendanceResponse(AttendanceBase):
    id: int

    class Config:
        orm_mode = True


# Optional: Employee with attendance
class EmployeeWithAttendance(EmployeeResponse):
    attendance_records: List[AttendanceResponse] = []


class AttendanceBulkItem(BaseModel):
    employee_id: str
    date: date
    status: str  # "Present" / "Absent"

class AttendanceBulkCreate(BaseModel):
    attendances: List[AttendanceBulkItem]

class AttendanceSummaryResponse(BaseModel):
    employee_id: str
    full_name: str
    department: str
    days_present: int
    days_absent: int