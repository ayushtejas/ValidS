from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional
from bson import ObjectId
from app.db.mongodb import get_database
from app.models.user import UserRole
import logging

logger = logging.getLogger(__name__)

security = HTTPBearer()


class RoleChecker:
    def __init__(self, allowed_roles: list[UserRole]):
        self.allowed_roles = allowed_roles

    def __call__(self, current_user: dict):
        if current_user.get("roletype") not in [role.value for role in self.allowed_roles]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions"
            )
        return current_user


async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get current user from token (simplified for now)"""
    # This is a simplified version - in production, you'd validate JWT tokens
    # For now, we'll use a mock implementation
    db = get_database()

    # In a real implementation, you'd decode the JWT token here
    # For now, we'll assume the token contains the user ID
    try:
        user_id = credentials.credentials  # This would be extracted from JWT
        if not ObjectId.is_valid(user_id):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )

        user = await db.users.find_one({"_id": ObjectId(user_id)})
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found"
            )

        if not user.get("is_active", True):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User account is inactive"
            )

        user["_id"] = str(user["_id"])
        return user

    except Exception as e:
        logger.error(f"Authentication error: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication failed"
        )


# Role-based dependencies
def require_superadmin(current_user: dict = Depends(get_current_user)):
    return RoleChecker([UserRole.SUPERADMIN])(current_user)

def require_auditor(current_user: dict = Depends(get_current_user)):
    return RoleChecker([UserRole.SUPERADMIN, UserRole.AUDITOR])(current_user)

def require_spectator(current_user: dict = Depends(get_current_user)):
    return RoleChecker([UserRole.SUPERADMIN, UserRole.AUDITOR, UserRole.SPECTATOR])(current_user)

def require_employee(current_user: dict = Depends(get_current_user)):
    return RoleChecker([UserRole.SUPERADMIN, UserRole.AUDITOR, UserRole.SPECTATOR, UserRole.EMPLOYEE])(current_user)


def check_company_access(user: dict, company_id: str) -> bool:
    """Check if user has access to a specific company"""
    user_role = user.get("roletype")
    user_company_id = user.get("company_id")

    # Superadmin has access to all companies
    if user_role == UserRole.SUPERADMIN.value:
        return True

    # Other users can only access their own company
    return user_company_id == company_id


def check_company_access_dependency(company_id: str):
    """Dependency to check company access"""
    def _check_access(current_user: dict = Depends(get_current_user)):
        if not check_company_access(current_user, company_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to this company"
            )
        return current_user
    return _check_access
