from fastapi import APIRouter, Depends

from app.api.dependencies import require_role
from app.models.user import User, UserRole

router = APIRouter(
    prefix="/roles",
    tags=["Roles"],
)


@router.get("/customer")
def customer_test(
    current_user: User = Depends(require_role(UserRole.CUSTOMER)),
):
    return {
        "message": "Customer access granted",
        "user_id": current_user.id,
        "role": current_user.role,
    }


@router.get("/provider")
def provider_test(
    current_user: User = Depends(require_role(UserRole.PROVIDER)),
):
    return {
        "message": "Provider access granted",
        "user_id": current_user.id,
        "role": current_user.role,
    }


@router.get("/admin")
def admin_test(
    current_user: User = Depends(require_role(UserRole.ADMIN)),
):
    return {
        "message": "Admin access granted",
        "user_id": current_user.id,
        "role": current_user.role,
    }
