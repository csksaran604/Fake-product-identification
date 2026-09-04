"""
database.py - SQLite Database Management & Data Layer

Handles schema creation, parameterized SQL queries, admin credentials,
product registrations, verification logs, and blockchain persistence.
"""

import json
import os
import sqlite3
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple
from werkzeug.security import check_password_hash, generate_password_hash

DB_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "database")
DB_PATH = os.path.join(DB_DIR, "products.db")


def get_db_connection() -> sqlite3.Connection:
    """Establish connection to SQLite database with Row mapping enabled."""
    os.makedirs(DB_DIR, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    """Initialize database tables if they do not already exist."""
    os.makedirs(DB_DIR, exist_ok=True)
    conn = get_db_connection()
    cursor = conn.cursor()

    # 1. Admin users table
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS admins (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
        """
    )

    # 2. Registered products table
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            manufacturer TEXT NOT NULL,
            category TEXT NOT NULL,
            batch_number TEXT NOT NULL,
            mfg_date TEXT NOT NULL,
            exp_date TEXT,
            description TEXT,
            verification_code TEXT UNIQUE NOT NULL,
            qr_code_path TEXT,
            created_at TEXT NOT NULL
        )
        """
    )

    # 3. Blockchain blocks persistence table
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS blockchain_blocks (
            block_index INTEGER PRIMARY KEY,
            timestamp TEXT NOT NULL,
            product_id TEXT NOT NULL,
            data_json TEXT NOT NULL,
            previous_hash TEXT NOT NULL,
            block_hash TEXT NOT NULL,
            nonce INTEGER NOT NULL
        )
        """
    )

    # 4. Verification audit logs table
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS verification_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            verification_code TEXT NOT NULL,
            product_id TEXT,
            status TEXT NOT NULL,
            ip_address TEXT,
            scanned_at TEXT NOT NULL
        )
        """
    )

    conn.commit()
    conn.close()


def seed_default_admin(username: str = "admin", password: str = "admin123") -> None:
    """Ensure a default admin account exists with a secure password hash."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM admins WHERE username = ?", (username,))
    existing = cursor.fetchone()

    if not existing:
        hashed_pw = generate_password_hash(password, method="pbkdf2:sha256")
        now_ts = datetime.now(timezone.utc).isoformat()
        cursor.execute(
            "INSERT INTO admins (username, password_hash, created_at) VALUES (?, ?, ?)",
            (username, hashed_pw, now_ts),
        )
        conn.commit()

    conn.close()


def verify_admin_login(username: str, password: str) -> bool:
    """Verify administrator login credentials against stored password hash."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT password_hash FROM admins WHERE username = ?", (username,))
    row = cursor.fetchone()
    conn.close()

    if not row:
        return False
    return check_password_hash(row["password_hash"], password)


# =====================================================================
# Product Management CRUD
# =====================================================================


def add_product(product_data: Dict[str, Any]) -> Tuple[bool, str]:
    """
    Insert a new product record using parameterized SQL.
    Prevents duplicates by product_id or verification_code.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            """
            INSERT INTO products (
                product_id, name, manufacturer, category, batch_number,
                mfg_date, exp_date, description, verification_code,
                qr_code_path, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                product_data["product_id"].strip().upper(),
                product_data["name"].strip(),
                product_data["manufacturer"].strip(),
                product_data["category"].strip(),
                product_data["batch_number"].strip().upper(),
                product_data["mfg_date"],
                product_data.get("exp_date") or None,
                product_data.get("description", "").strip(),
                product_data["verification_code"].strip().upper(),
                product_data.get("qr_code_path", ""),
                datetime.now(timezone.utc).isoformat(),
            ),
        )
        conn.commit()
        return True, "Product registered successfully in database."
    except sqlite3.IntegrityError as e:
        err_msg = str(e).lower()
        if "product_id" in err_msg:
            return False, f"Product ID '{product_data['product_id']}' already exists. IDs must be unique."
        if "verification_code" in err_msg:
            return False, f"Verification code '{product_data['verification_code']}' already exists. Codes must be unique."
        return False, f"Database constraint violation: {str(e)}"
    except Exception as e:
        return False, f"Error saving product: {str(e)}"
    finally:
        conn.close()


def get_product_by_id(product_id: str) -> Optional[sqlite3.Row]:
    """Retrieve product record by Product ID."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM products WHERE UPPER(product_id) = UPPER(?)",
        (product_id.strip(),),
    )
    row = cursor.fetchone()
    conn.close()
    return row


def get_product_by_code(code: str) -> Optional[sqlite3.Row]:
    """Retrieve product record by Verification Code."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM products WHERE UPPER(verification_code) = UPPER(?)",
        (code.strip(),),
    )
    row = cursor.fetchone()
    conn.close()
    return row


def get_product_by_id_or_code(query_val: str) -> Optional[sqlite3.Row]:
    """Flexible lookup: match either Product ID or Verification Code."""
    cleaned = query_val.strip()
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT * FROM products 
        WHERE UPPER(product_id) = UPPER(?) OR UPPER(verification_code) = UPPER(?)
        """,
        (cleaned, cleaned),
    )
    row = cursor.fetchone()
    conn.close()
    return row


def get_all_products(search: Optional[str] = None, category: Optional[str] = None) -> List[sqlite3.Row]:
    """Retrieve all products with optional text search and category filter."""
    conn = get_db_connection()
    cursor = conn.cursor()

    query = "SELECT * FROM products WHERE 1=1"
    params: List[Any] = []

    if search:
        s_clean = f"%{search.strip()}%"
        query += " AND (name LIKE ? OR product_id LIKE ? OR manufacturer LIKE ? OR verification_code LIKE ? OR batch_number LIKE ?)"
        params.extend([s_clean, s_clean, s_clean, s_clean, s_clean])

    if category and category.lower() != "all":
        query += " AND category = ?"
        params.append(category.strip())

    query += " ORDER BY id DESC"

    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()
    return rows


def delete_product(product_id: str) -> Tuple[bool, str]:
    """Delete a product by Product ID."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM products WHERE UPPER(product_id) = UPPER(?)", (product_id.strip(),))
        affected = cursor.rowcount
        conn.commit()
        if affected > 0:
            return True, f"Product '{product_id}' was removed successfully."
        return False, f"Product '{product_id}' not found."
    except Exception as e:
        return False, f"Error deleting product: {str(e)}"
    finally:
        conn.close()


def get_categories() -> List[str]:
    """Return distinct categories available in the database."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT category FROM products ORDER BY category ASC")
    rows = cursor.fetchall()
    conn.close()
    return [r["category"] for r in rows if r["category"]]


# =====================================================================
# Verification Audit Logging
# =====================================================================


def log_verification(verification_code: str, product_id: Optional[str], status: str, ip_address: Optional[str] = None) -> None:
    """Record customer product verification attempt in audit log."""
    conn = get_db_connection()
    cursor = conn.cursor()
    now_ts = datetime.now(timezone.utc).isoformat()
    cursor.execute(
        """
        INSERT INTO verification_logs (verification_code, product_id, status, ip_address, scanned_at)
        VALUES (?, ?, ?, ?, ?)
        """,
        (verification_code.strip(), product_id, status, ip_address or "127.0.0.1", now_ts),
    )
    conn.commit()
    conn.close()


def get_recent_logs(limit: int = 20) -> List[sqlite3.Row]:
    """Retrieve recent verification attempts."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT v.*, p.name as product_name, p.manufacturer
        FROM verification_logs v
        LEFT JOIN products p ON UPPER(v.product_id) = UPPER(p.product_id)
        ORDER BY v.id DESC LIMIT ?
        """,
        (limit,),
    )
    rows = cursor.fetchall()
    conn.close()
    return rows


def get_dashboard_metrics() -> Dict[str, Any]:
    """Calculate real-time analytics for the administrator dashboard."""
    conn = get_db_connection()
    cursor = conn.cursor()

    # Product counts
    cursor.execute("SELECT COUNT(*) as total FROM products")
    total_products = cursor.fetchone()["total"]

    # Verification attempt counts
    cursor.execute("SELECT COUNT(*) as total FROM verification_logs")
    total_scans = cursor.fetchone()["total"]

    cursor.execute("SELECT COUNT(*) as verified FROM verification_logs WHERE status = 'VERIFIED'")
    verified_count = cursor.fetchone()["verified"]

    cursor.execute("SELECT COUNT(*) as failed FROM verification_logs WHERE status != 'VERIFIED'")
    failed_count = cursor.fetchone()["failed"]

    # Blockchain blocks count
    cursor.execute("SELECT COUNT(*) as total_blocks FROM blockchain_blocks")
    total_blocks = cursor.fetchone()["total_blocks"]

    # Category distribution
    cursor.execute("SELECT category, COUNT(*) as count FROM products GROUP BY category")
    category_rows = cursor.fetchall()
    categories = {r["category"]: r["count"] for r in category_rows}

    # Verification status distribution
    cursor.execute("SELECT status, COUNT(*) as count FROM verification_logs GROUP BY status")
    status_rows = cursor.fetchall()
    statuses = {r["status"]: r["count"] for r in status_rows}

    conn.close()

    return {
        "total_products": total_products,
        "total_scans": total_scans,
        "verified_count": verified_count,
        "failed_count": failed_count,
        "total_blocks": total_blocks,
        "categories": categories,
        "statuses": statuses,
    }


# =====================================================================
# Blockchain Database Persistence
# =====================================================================


def save_all_blocks_to_db(blockchain_instance: Any) -> None:
    """Synchronize the in-memory blockchain into SQLite blockchain_blocks table."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM blockchain_blocks")

    for block in blockchain_instance.chain:
        data_json = json.dumps(block.data, sort_keys=True)
        cursor.execute(
            """
            INSERT INTO blockchain_blocks (block_index, timestamp, product_id, data_json, previous_hash, block_hash, nonce)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                block.index,
                block.timestamp,
                block.product_id,
                data_json,
                block.previous_hash,
                block.hash,
                block.nonce,
            ),
        )

    conn.commit()
    conn.close()


def load_blockchain_from_db(blockchain_instance: Any) -> bool:
    """Load existing blockchain records from SQLite database into memory."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM blockchain_blocks ORDER BY block_index ASC")
    rows = cursor.fetchall()
    conn.close()

    if not rows:
        return False

    blocks_dict_list = []
    for r in rows:
        try:
            data = json.loads(r["data_json"])
        except Exception:
            data = {"raw": r["data_json"]}

        blocks_dict_list.append(
            {
                "index": r["block_index"],
                "timestamp": r["timestamp"],
                "product_id": r["product_id"],
                "data": data,
                "previous_hash": r["previous_hash"],
                "hash": r["block_hash"],
                "nonce": r["nonce"],
            }
        )

    blockchain_instance.load_from_dict_list(blocks_dict_list)
    return True
