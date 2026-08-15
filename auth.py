import sqlite3
from database import get_connection, hash_password

def user_exists(username: str) -> bool:
    """Check if a username exists in the database."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
    row = cursor.fetchone()
    conn.close()
    return row is not None

def authenticate_user(username, password):
    """Authenticate existing user with matching password."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, username, email, role, password_hash FROM users WHERE username = ?",
        (username,)
    )
    row = cursor.fetchone()
    conn.close()

    if row:
        user_id, uname, email, role, stored_hash = row
        if stored_hash == hash_password(password):
            return {"id": user_id, "username": uname, "email": email, "role": role}
    return None

def register_user(username, email, password, role="User"):
    """Register a new user in the database."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO users (username, email, password_hash, role) VALUES (?, ?, ?, ?)",
            (username, email, hash_password(password), role)
        )
        conn.commit()
        # Fetch created user info
        user_id = cursor.lastrowid
        conn.close()
        return True, "User registered successfully!", {"id": user_id, "username": username, "email": email, "role": role}
    except sqlite3.IntegrityError:
        conn.close()
        return False, "Username already exists!", None

def reset_password(username, new_password):
    """Reset user password."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
    row = cursor.fetchone()
    if not row:
        conn.close()
        return False, "Username not found!"

    cursor.execute(
        "UPDATE users SET password_hash = ? WHERE username = ?",
        (hash_password(new_password), username)
    )
    conn.commit()
    conn.close()
    return True, "Password reset successfully! Please login with your new password."
