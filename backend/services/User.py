# services.py (MVC - Service layer) - MySQL Version with Error Handling
import uuid
from typing import Dict, Optional, List
from passlib.context import CryptContext
from models.User import UserCreate, UserUpdate
from database.database import get_connection
import mysql.connector

# -------------------------------------
# Password Hashing (Argon2)
# -------------------------------------
pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

# -------------------------------------
# Helper: Safe DB Execution Wrapper
# -------------------------------------

def execute_query(query, params=None, fetchone=False, fetchall=False):
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute(query, params or [])

        # ---- FIX 1: Only fetch if SELECT returns a result set ----
        has_resultset = cursor.with_rows

        # ---- FIX 2: Consume remaining results to avoid unread result errors ----
        while cursor.nextset():
            pass

        conn.commit()

        if has_resultset:
            if fetchone:
                return cursor.fetchone()
            if fetchall:
                return cursor.fetchall()

        # Non-select queries return True
        return True

    except Exception as e:
        raise Exception(f"Database error: {e}")

    finally:
        if conn:
            conn.close()


# -------------------------------------
# CRUD Operations (MySQL)
# -------------------------------------

def create_user(data: UserCreate) -> Dict:
    user_id = str(uuid.uuid4())
    password_hash = hash_password(data.password)

    query = """
        INSERT INTO users (id, full_name, email, password_hash, role, phone)
        VALUES (%s, %s, %s, %s, %s, %s)
    """

    execute_query(query, (
        user_id,
        data.full_name,
        data.email,
        password_hash,
        data.role,
        data.phone
    ))

    return {
        "id": user_id,
        "full_name": data.full_name,
        "email": data.email,
        "role": data.role,
        "phone": data.phone
    }


def get_all_users() -> List[Dict]:
    query = "SELECT id, full_name, email, role, phone FROM users"
    return execute_query(query, fetch="all") or []


def get_user(user_id: str) -> Optional[Dict]:
    query = "SELECT id, full_name, email, role, phone FROM users WHERE id = %s"
    return execute_query(query, (user_id,), fetch="one")


def update_user(user_id: str, data: UserUpdate) -> Optional[Dict]:
    # Check if exists
    existing = get_user(user_id)
    if not existing:
        return None

    fields = []
    values = []

    if data.full_name is not None:
        fields.append("full_name = %s")
        values.append(data.full_name)
    if data.email is not None:
        fields.append("email = %s")
        values.append(data.email)
    if data.password is not None:
        fields.append("password_hash = %s")
        values.append(hash_password(data.password))
    if data.role is not None:
        fields.append("role = %s")
        values.append(data.role)
    if data.phone is not None:
        fields.append("phone = %s")
        values.append(data.phone)

    if not fields:
        return existing

    query = f"UPDATE users SET {', '.join(fields)} WHERE id = %s"
    values.append(user_id)

    execute_query(query, tuple(values))

    return get_user(user_id)


def delete_user(user_id: str) -> bool:
    query = "DELETE FROM users WHERE id = %s"
    execute_query(query, (user_id,))

    # Check if deleted
    return get_user(user_id) is None