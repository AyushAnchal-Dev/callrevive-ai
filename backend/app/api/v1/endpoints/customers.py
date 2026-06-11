"""CallRevive AI — Customer management endpoints."""
from __future__ import annotations

import uuid
from fastapi import APIRouter, HTTPException
from sqlalchemy import select, func, or_
from sqlalchemy.orm import selectinload, joinedload

from app.api.deps import CurrentUser, DBSession
from app.models.customer import Customer
from app.models.call import Call
from app.models.lead import Lead
from app.schemas.customer import CustomerCreate, CustomerUpdate, CustomerResponse, CustomerListResponse
from app.schemas.call import CallResponse
from app.schemas.lead import LeadResponse

router = APIRouter()


@router.get("/", response_model=CustomerListResponse)
async def list_customers(
    db: DBSession,
    current_user: CurrentUser,
    page: int = 1,
    page_size: int = 20,
    search: str | None = None,
    category: str | None = None,
):
    """List customers with optional search and filtering."""
    query = select(Customer).options(selectinload(Customer.calls), selectinload(Customer.leads)).where(Customer.business_id == current_user.business_id)
    if search:
        query = query.where(
            or_(
                Customer.name.ilike(f"%{search}%"),
                Customer.phone_number.ilike(f"%{search}%"),
                Customer.email.ilike(f"%{search}%"),
            )
        )
    if category:
        query = query.where(Customer.category == category)

    total = (await db.execute(select(func.count()).select_from(query.subquery()))).scalar() or 0
    result = await db.execute(query.offset((page - 1) * page_size).limit(page_size))
    return CustomerListResponse(
        items=result.scalars().all(),
        total=total,
        page=page,
        page_size=page_size,
        pages=(total + page_size - 1) // page_size,
    )


@router.get("/{customer_id}", response_model=CustomerResponse)
async def get_customer(customer_id: uuid.UUID, db: DBSession, current_user: CurrentUser):
    """Get customer details."""
    result = await db.execute(
        select(Customer)
        .options(selectinload(Customer.calls), selectinload(Customer.leads))
        .where(Customer.id == customer_id)
    )
    customer = result.scalar_one_or_none()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    return customer


@router.post("/", response_model=CustomerResponse, status_code=201)
async def create_customer(data: CustomerCreate, db: DBSession, current_user: CurrentUser):
    """Create a new customer."""
    customer = Customer(
        phone_number=data.phone_number,
        name=data.name,
        email=data.email,
        whatsapp_number=data.whatsapp_number,
        category=data.category,
        business_id=current_user.business_id,
    )
    db.add(customer)
    await db.commit()
    await db.refresh(customer)
    return customer


@router.put("/{customer_id}", response_model=CustomerResponse)
async def update_customer(
    customer_id: uuid.UUID, data: CustomerUpdate, db: DBSession, current_user: CurrentUser
):
    """Update customer info."""
    result = await db.execute(select(Customer).where(Customer.id == customer_id))
    customer = result.scalar_one_or_none()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    for key, val in data.model_dump(exclude_unset=True).items():
        setattr(customer, key, val)
    await db.commit()
    await db.refresh(customer)
    return customer


@router.get("/{customer_id}/calls", response_model=list[CallResponse])
async def get_customer_calls(
    customer_id: uuid.UUID, db: DBSession, current_user: CurrentUser
):
    """Get customer's call history."""
    query = select(Call).options(joinedload(Call.customer)).where(Call.customer_id == customer_id).order_by(Call.created_at.desc())
    result = await db.execute(query)
    return result.scalars().all()


@router.get("/{customer_id}/leads", response_model=list[LeadResponse])
async def get_customer_leads(
    customer_id: uuid.UUID, db: DBSession, current_user: CurrentUser
):
    """Get customer's leads."""
    query = select(Lead).options(joinedload(Lead.customer)).where(Lead.customer_id == customer_id).order_by(Lead.created_at.desc())
    result = await db.execute(query)
    return result.scalars().all()
