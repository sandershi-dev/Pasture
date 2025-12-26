# services.py (MVC - Service layer) - MySQL Version with Error Handling
import uuid
from typing import Dict, Optional, List
from passlib.context import CryptContext
from users.models import UserCreate, UserUpdate
from database.database import get_connection
import mysql.connector
from typing import Literal, Optional, List, Dict


# -------------------------------------
# Password Hashing (Argon2)
# -------------------------------------
pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

# -------------------------------------
# Helper: Safe DB Execution Wrapper
# -------------------------------------


def execute_query(
    query: str,
    params: tuple | None = None,
    fetch: Literal["one", "all", None] = None
):
    conn = None
    cursor = None

    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(query, params or ())

        result = None
        if cursor.with_rows:
            if fetch == "one":
                result = cursor.fetchone()
            elif fetch == "all":
                result = cursor.fetchall()

        # consume remaining result sets (important for MySQL)
        while cursor.nextset():
            pass

        # commit only if not SELECT
        if not cursor.with_rows:
            conn.commit()

        return result if fetch else True

    except mysql.connector.Error as e:
        raise Exception(f"Database error: {e}")

    finally:
        if cursor:
            cursor.close()
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
    result = execute_query(query, (user_id,))
    return result