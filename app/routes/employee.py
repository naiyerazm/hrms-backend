from fastapi import FastAPI, APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import extract
from app.models import *
from app.schemas import *
from app.db import engine, get_db
from datetime import date
from utils.security import verify_token  # function to verify JWT
import uuid
from typing import List
from datetime import datetime

router = APIRouter()

app = FastAPI(title="HRMS API")

# Create tables
Base.metadata.create_all(bind=engine)


# ----------------- Employee CRUD -----------------
@router.post("/", response_model=EmployeeResponse)
def create_employee(
    employee: EmployeeCreate,
    db: Session = Depends(get_db),
    token_data: dict = Depends(verify_token)
):
    # Check if email already exists
    db_employee = db.query(Employee).filter(Employee.email == employee.email).first()
    if db_employee:
        raise HTTPException(status_code=400, detail="Email already exists")
    
    # Generate unique employee_id
    new_employee_id = str(uuid.uuid4())[:8]  # short UUID
    new_emp = Employee(
        employee_id=new_employee_id,
        full_name=employee.full_name,
        email=employee.email,
        department=employee.department
    )
    
    db.add(new_emp)
    db.commit()
    db.refresh(new_emp)
    return new_emp


@router.get("/", response_model=list[EmployeeResponse])
def list_employees(db: Session = Depends(get_db),
                   token_data: dict = Depends(verify_token)):
    return db.query(Employee).all()


@router.get("/{employee_id}", response_model=EmployeeResponse)
def get_employee(employee_id: str, db: Session = Depends(get_db),
                 token_data: dict = Depends(verify_token)):
    employee = db.query(Employee).filter(Employee.employee_id == employee_id).first()
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    return employee


@router.put("/{employee_id}")
def update_employee(employee_id: str, emp_update: EmployeeUpdate, db: Session = Depends(get_db)):
    emp = db.query(Employee).filter(Employee.employee_id == employee_id).first()
    if not emp:
        raise HTTPException(status_code=404, detail="Employee not found")
    
    # Update fields if provided
    if emp_update.full_name is not None:
        emp.full_name = emp_update.full_name
    if emp_update.email is not None:
        emp.email = emp_update.email
    if emp_update.department is not None:
        emp.department = emp_update.department
    
    db.commit()
    db.refresh(emp)  # refresh the instance to get updated values

    return {"detail": "Employee updated successfully", "employee": {
        "employee_id": emp.employee_id,
        "full_name": emp.full_name,
        "email": emp.email,
        "department": emp.department
    }}


@router.delete("/{employee_id}")
def delete_employee(employee_id: str, db: Session = Depends(get_db)):
    emp = db.query(Employee).filter(Employee.employee_id == employee_id).first()
    if not emp:
        raise HTTPException(status_code=404, detail="Employee not found")
    db.delete(emp)
    db.commit()
    return {"detail": "Employee deleted successfully"}


@router.post("/attendance/bulk/", response_model=List[AttendanceResponse])
def mark_bulk_attendance(
    bulk: AttendanceBulkCreate,
    db: Session = Depends(get_db),
    token_data: dict = Depends(verify_token)
):
    created_attendances = []

    for att_item in bulk.attendances:
        emp = db.query(Employee).filter(Employee.employee_id == att_item.employee_id).first()
        if not emp:
            raise HTTPException(status_code=404, detail=f"Employee not found: {att_item.employee_id}")

        existing = (
            db.query(Attendance)
            .filter(Attendance.employee_id == emp.id)
            .filter(Attendance.date == att_item.date)
            .first()
        )
        if existing:
            raise HTTPException(
                status_code=400,
                detail=f"Attendance already marked for {att_item.employee_id} on {att_item.date}"
            )

        new_att = Attendance(
            employee_id=emp.id,
            date=att_item.date,
            status=att_item.status
        )
        db.add(new_att)
        db.commit()
        db.refresh(new_att)
        created_attendances.append(new_att)

    return created_attendances


@router.get("/attendance/list", response_model=List[AttendanceSummaryResponse])
def get_attendance_list(
    year: Optional[int] = Query(None, description="Year in YYYY format"),
    month: Optional[int] = Query(None, ge=1, le=12, description="Month number 1-12"),
    db: Session = Depends(get_db)
):
    now = datetime.now()
    year = year or now.year
    month = month or now.month

    employees = db.query(Employee).all()
    if not employees:
        raise HTTPException(status_code=404, detail="No employees found")

    result = []
    for emp in employees:
        attendance_records = (
            db.query(Attendance)
            .filter(
                Attendance.employee_id == emp.id,
                extract('year', Attendance.date) == year,
                extract('month', Attendance.date) == month
            )
            .all()
        )

        days_present = sum(1 for a in attendance_records if a.status.lower() == "present")
        days_absent = sum(1 for a in attendance_records if a.status.lower() == "absent")

        result.append({
            "employee_id": emp.employee_id,
            "full_name": emp.full_name,
            "department": emp.department,
            "days_present": days_present,
            "days_absent": days_absent
        })

    return result

# ----------------- Attendance CRUD -----------------
@router.post("/attendance/{employee_id}", response_model=AttendanceResponse)
def mark_attendance(employee_id: str, attendance: AttendanceCreate, db: Session = Depends(get_db),
                    token_data: dict = Depends(verify_token)):
    # Check employee exists
    emp = db.query(Employee).filter(Employee.employee_id == employee_id).first()
    if not emp:
        raise HTTPException(status_code=404, detail="Employee not found")

    # Optional: Prevent duplicate attendance for same date
    existing = (
        db.query(Attendance)
        .filter(Attendance.employee_id == emp.id)  # use internal DB id
        .filter(Attendance.date == attendance.date)
        .first()
    )
    if existing:
        raise HTTPException(status_code=400, detail="Attendance already marked for this date")

    # Create attendance record
    att = Attendance(
        employee_id=emp.id,
        date=attendance.date,
        status=attendance.status
    )
    db.add(att)
    db.commit()
    db.refresh(att)
    return att


@router.get("/attendance/{employee_id}", response_model=list[AttendanceResponse])
def get_attendance(employee_id: str, db: Session = Depends(get_db)):
    emp = db.query(Employee).filter(Employee.employee_id == employee_id).first()
    if not emp:
        raise HTTPException(status_code=404, detail="Employee not found")
    return db.query(Attendance).filter(Attendance.employee_id == emp.id).all()