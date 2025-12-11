# controllers.py (MVC - Controller layer) with Improved HTTP Error Responses
from fastapi import APIRouter, HTTPException, status
from models.User import UserCreate, UserUpdate, UserResponse
from services.User import create_user, get_all_users, get_user, update_user, delete_user

router = APIRouter(prefix="/users", tags=["Users"])

# -----------------------------
# CREATE USER
# -----------------------------
@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user_endpoint(data: UserCreate):
    try:
        user = create_user(data)
        return UserResponse(**user)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create user: {e}"
        )

# -----------------------------
# GET ALL USERS
# -----------------------------
@router.get("/", response_model=list[UserResponse])
def list_users():
    users = get_all_users()
    return [UserResponse(**u) for u in users]

# -----------------------------
# GET USER BY ID
# -----------------------------
@router.get("/{user_id}", response_model=UserResponse)
def get_user_endpoint(user_id: str):
    user = get_user(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return UserResponse(**user)

# -----------------------------
# UPDATE USER
# -----------------------------
@router.put("/{user_id}", response_model=UserResponse)
def update_user_endpoint(user_id: str, data: UserUpdate):
    try:
        updated = update_user(user_id, data)

        if not updated:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        return UserResponse(**updated)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update user: {e}"
        )

# -----------------------------
# DELETE USER
# -----------------------------
@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user_endpoint(user_id: str):
    try:
        deleted = delete_user(user_id)
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        return
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete user: {e}"
        )
