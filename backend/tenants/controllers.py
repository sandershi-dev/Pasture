# tenants/controllers.py
from fastapi import APIRouter, HTTPException, status
from tenants.models import TenantCreate, TenantUpdate, TenantResponse
from tenants.services import (
    create_tenant,
    get_all_tenants,
    get_tenant,
    update_tenant,
    delete_tenant,
)

router = APIRouter(prefix="/tenants", tags=["Tenants"])


@router.post("/", response_model=TenantResponse, status_code=status.HTTP_201_CREATED)
def create_tenant_endpoint(data: TenantCreate):
    try:
        tenant = create_tenant(data)
        return TenantResponse(**tenant)
    except Exception as e:
        raise HTTPException(500, f"Failed to create tenant: {e}")


@router.get("/", response_model=list[TenantResponse])
def list_tenants():
    tenants = get_all_tenants()
    return [TenantResponse(**t) for t in tenants]


@router.get("/{tenant_id}", response_model=TenantResponse)
def get_tenant_endpoint(tenant_id: str):
    tenant = get_tenant(tenant_id)
    if not tenant:
        raise HTTPException(404, "Tenant not found")
    return TenantResponse(**tenant)


@router.put("/{tenant_id}", response_model=TenantResponse)
def update_tenant_endpoint(tenant_id: str, data: TenantUpdate):
    try:
        updated = update_tenant(tenant_id, data)
        if not updated:
            raise HTTPException(404, "Tenant not found")
        return TenantResponse(**updated)

    except Exception as e:
        raise HTTPException(500, f"Failed to update tenant: {e}")


@router.delete("/{tenant_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_tenant_endpoint(tenant_id: str):
    try:
        deleted = delete_tenant(tenant_id)
        if not deleted:
            raise HTTPException(404, "Tenant not found")
    except Exception as e:
        raise HTTPException(500, f"Failed to delete tenant: {e}")
