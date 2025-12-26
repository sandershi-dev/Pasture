# tenants/services.py
from database.database import get_connection
import uuid
import json

def execute_query(query, params=None, fetchone=False, fetchall=False):
    """
    Robust execute helper:
    - returns fetched rows when requested
    - avoids 'Unread result found' by consuming remaining result sets
    - avoids 'No result set to fetch from' by checking cursor.with_rows
    """
    conn = None
    cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute(query, params or [])

        # Does this statement produce rows (SELECT)?
        has_rows = getattr(cursor, "with_rows", False)

        result = None

        if has_rows:
            # fetch the requested data first
            if fetchone:
                result = cursor.fetchone()
            elif fetchall:
                result = cursor.fetchall()
            else:
                # caller didn't request rows; consume nothing yet
                result = None

            # consume any additional result sets (metadata / warnings / triggers)
            # each nextset may itself have rows that must be fetched/discarded
            while cursor.nextset():
                try:
                    # fetch to clear results
                    _ = cursor.fetchall()
                except Exception:
                    # ignore any fetch errors while draining
                    pass
        else:
            # No row-producing result; but there may be additional result sets to drain
            while cursor.nextset():
                try:
                    _ = cursor.fetchall()
                except Exception:
                    pass
            result = True  # indicate non-select success

        # commit after clearing results
        conn.commit()
        return result

    except Exception as e:
        # include query info for debugging
        raise Exception(f"Database error: {e} (query={query!r}, params={params!r})")
    finally:
        try:
            if cursor is not None:
                cursor.close()
        except Exception:
            pass
        try:
            if conn is not None:
                conn.close()
        except Exception:
            pass


def _decode_json_fields(record):
    if not record:
        return record
    if record.get("emergency_contact"):
        try:
            record["emergency_contact"] = json.loads(record["emergency_contact"])
        except Exception:
            record["emergency_contact"] = None
    return record


def create_tenant(data):
    tenant_id = str(uuid.uuid4())

    query = """
        INSERT INTO tenants (id, full_name, email, phone, date_of_birth, government_id, emergency_contact)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """

    params = [
        tenant_id,
        data.full_name,
        data.email,
        data.phone,
        data.date_of_birth,
        data.government_id,
        json.dumps(data.emergency_contact) if data.emergency_contact is not None else None,
    ]

    execute_query(query, params)          # insert (non-select)
    tenant = get_tenant(tenant_id)        # select afterwards using same helper
    return tenant


def get_all_tenants():
    query = "SELECT * FROM tenants"
    rows = execute_query(query, fetchall=True) or []
    return [_decode_json_fields(r) for r in rows]


def get_tenant(tenant_id):
    query = "SELECT * FROM tenants WHERE id = %s"
    row = execute_query(query, (tenant_id,), fetchone=True)
    return _decode_json_fields(row)


def update_tenant(tenant_id, data):
    query = """
        UPDATE tenants
        SET full_name = COALESCE(%s, full_name),
            email = COALESCE(%s, email),
            phone = COALESCE(%s, phone),
            date_of_birth = COALESCE(%s, date_of_birth),
            government_id = COALESCE(%s, government_id),
            emergency_contact = COALESCE(%s, emergency_contact)
        WHERE id = %s
    """

    params = [
        data.full_name,
        data.email,
        data.phone,
        data.date_of_birth,
        data.government_id,
        json.dumps(data.emergency_contact) if data.emergency_contact is not None else None,
        tenant_id,
    ]

    execute_query(query, tuple(params))
    updated = get_tenant(tenant_id)
    return updated


def delete_tenant(tenant_id):
    query = "DELETE FROM tenants WHERE id = %s"
    execute_query(query, (tenant_id,))
    # verify deletion
    return get_tenant(tenant_id) is None
