import pymysql
from pymysql.cursors import DictCursor

db_config = {
    "host": "localhost",
    "user": "root",
    "password": "Praveen@8343",
    "database": "job_tracker",
    "cursorclass": DictCursor
}

def get_conn():
    return pymysql.connect(**db_config)

def db_init():
    conn = get_conn()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INT AUTO_INCREMENT PRIMARY KEY,
        username VARCHAR(50) UNIQUE NOT NULL,
        email VARCHAR(100) UNIQUE NOT NULL,
        password VARCHAR(200) NOT NULL
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS applications (
        id INT AUTO_INCREMENT PRIMARY KEY,
        user_id INT NOT NULL,
        company VARCHAR(100) NOT NULL,
        role VARCHAR(100) NOT NULL,
        date_applied DATE NOT NULL,
        status VARCHAR(50) NOT NULL,
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
    );
    """)

    conn.commit()
    cursor.close()
    conn.close()

db_init()

def db_check_user_by_email(email):
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM users WHERE email=%s", (email,))
    user = cursor.fetchone()
    cursor.close()
    conn.close()
    return user

def db_insert_user(username, email, password):
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO users (username, email, password) VALUES (%s, %s, %s)",
        (username, email, password)
    )
    conn.commit()
    cursor.close()
    conn.close()

def db_get_user(email):
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE email=%s", (email,))
    user = cursor.fetchone()
    cursor.close()
    conn.close()
    return user

def db_get_applications(user_id, search="", status=""):
    query = "SELECT * FROM applications WHERE user_id=%s"
    params = [user_id]

    if search:
        query += " AND (company LIKE %s OR role LIKE %s)"
        params.extend([f"%{search}%", f"%{search}%"])
    if status:
        query += " AND status=%s"
        params.append(status)

    query += " ORDER BY date_applied DESC"

    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute(query, params)
    apps = cursor.fetchall()
    cursor.close()
    conn.close()
    return apps

def db_insert_application(user_id, company, role, date_applied, status):
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO applications (user_id, company, role, date_applied, status) VALUES (%s, %s, %s, %s, %s)",
        (user_id, company, role, date_applied, status)
    )
    conn.commit()
    cursor.close()
    conn.close()

def db_get_application(app_id, user_id):
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM applications WHERE id=%s AND user_id=%s", (app_id, user_id))
    app = cursor.fetchone()
    cursor.close()
    conn.close()
    return app

def db_update_application(app_id, user_id, company, role, date_applied, status):
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE applications SET company=%s, role=%s, date_applied=%s, status=%s WHERE id=%s AND user_id=%s",
        (company, role, date_applied, status, app_id, user_id)
    )
    conn.commit()
    cursor.close()
    conn.close()

def db_delete_application(app_id, user_id):
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM applications WHERE id=%s AND user_id=%s", (app_id, user_id))
    conn.commit()
    cursor.close()
    conn.close()

def db_get_reports(user_id):
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT status, COUNT(*) as count FROM applications WHERE user_id=%s GROUP BY status",
        (user_id,)
    )
    stats = cursor.fetchall()
    cursor.close()
    conn.close()
    return stats

def db_export_applications(user_id):
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT company, role, date_applied, status FROM applications WHERE user_id=%s",
        (user_id,)
    )
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows