from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import Table, MetaData, and_, select
from app.db import get_db, engine
from app.routes.auth import verify_token
router = APIRouter()

metadata = MetaData()

configuration = Table("pist_configuration_mst", metadata, schema="ahism", autoload_with=engine)
department = Table("gblt_department_mst", metadata, schema="ahism", autoload_with=engine)
designation = Table("gblt_designation_mst", metadata, schema="ahism", autoload_with=engine)

@router.get("/employment-types/")
def get_employment_types(
    db: Session = Depends(get_db),
    token_data: dict = Depends(verify_token),
):
    # Build the SELECT query
    query = (
        select(
            configuration.c.num_configuration_id.label("id"),
            configuration.c.str_configuration_code.label("status_code"),
            configuration.c.str_configuration_name.label("status_name"),
        )
        .where(
            and_(
                configuration.c.str_attri_code == "STA",
                configuration.c.gnum_isvalid == 1
                )
        )
    )

    # Execute query
    result = db.execute(query).fetchall()

    # Format response
    data = [
        {
            "id": row.id,
            "status_code": row.status_code,
            "status_name": row.status_name,
        }
        for row in result
    ]

    return {"status": "success", "data": data}

@router.get("/employment-status/")
def get_employment_types(
    db: Session = Depends(get_db),
    token_data: dict = Depends(verify_token),
):

    query = (
        select(
            configuration.c.num_configuration_id.label("id"),
            configuration.c.str_configuration_code.label("status_code"),
            configuration.c.str_configuration_name.label("status_name"),
        )
        .where(
            and_(
                configuration.c.str_attri_code == "FST",
                configuration.c.gnum_isvalid == 1
                )
        )
    )

    # Execute query
    result = db.execute(query).fetchall()

    # Format response
    data = [
        {
            "id": row.id,
            "status_code": row.status_code,
            "status_name": row.status_name,
        }
        for row in result
    ]

    return {"status": "success", "data": data}

@router.get("/designations/")
def get_designations(
    db: Session = Depends(get_db),
    token_data: dict = Depends(verify_token),
):

    query = (
        select(
            designation.c.gnum_desig_code.label("id"),
            designation.c.gstr_desig_name.label("desig_name"),
        )
        .where(designation.c.gnum_isvalid == 1)
        .order_by(designation.c.gnum_desig_code)
    )

    # Execute query
    result = db.execute(query).fetchall()

    # Format response
    data = [
        {
            "id": row.id,
            "desig_name": row.desig_name,
        }
        for row in result
    ]

    return {"status": "success", "data": data}


@router.get("/departments/")
def get_departments(
    db: Session = Depends(get_db),
    token_data: dict = Depends(verify_token),
):

    query = (
        select(
            department.c.gnum_dept_code.label("id"),
            department.c.gstr_dept_name.label("dept_name"),
        )
        .where(department.c.gnum_isvalid == 1)
        .order_by(department.c.gnum_dept_code)
    )

    result = db.execute(query).fetchall()

    data = [
        {
            "id": row.id,
            "dept_name": row.dept_name,
        }
        for row in result
    ]

    return {"status": "success", "data": data}


@router.get("/service-groups/")
def get_service_groups(
    db: Session = Depends(get_db),
    token_data: dict = Depends(verify_token),
):

    query = (
        select(
            configuration.c.num_configuration_id.label("id"),
            configuration.c.str_configuration_code.label("status_code"),
            configuration.c.str_configuration_name.label("status_name"),
        )
        .where(
            and_(
                configuration.c.str_attri_code == "SG",
                configuration.c.gnum_isvalid == 1
                )
        )
    )

    # Execute query
    result = db.execute(query).fetchall()

    # Format response
    data = [
        {
            "id": row.id,
            "group_code": row.status_code,
            "group_name": row.status_name,
        }
        for row in result
    ]

    return {"status": "success", "data": data}