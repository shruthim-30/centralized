from flask import Blueprint, request, jsonify
import oracledb
from history import log_action

login_bp = Blueprint("login", __name__)

# ---------------- DB CONNECTION ----------------
def get_connection():
    return oracledb.connect(
        user="FMD_IT",
        password="fmd123",
        dsn="localhost:1521/xepdb1"
    )

# ---------------- USER LOGIN ----------------
@login_bp.route("/login/user", methods=["POST"])
def login_user():
    try:
        data = request.json
        pb_number = data.get("pbNumber")
        password = data.get("password")

        if not pb_number or not password:
            return jsonify({"error": "PB Number and password are required"}), 400

        with get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT name, role
                    FROM users
                    WHERE pb_number = :1 AND password = :2
                    AND role IN ('user','hr')
                """, [pb_number, password])

                user = cursor.fetchone()

        if not user:
            return jsonify({"error": "Invalid credentials or not a user"}), 401

        name, role = user

        log_action(
            action="User Login",
            entity_name=name,
            performed_by=name,
            details=f"{role} logged in"
        )

        return jsonify({
            "message": "Login successful",
            "name": name,
            "pbNumber": pb_number,
            "role": role
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ---------------- ADMIN LOGIN ----------------
@login_bp.route("/login/admin", methods=["POST"])
def login_admin():
    try:
        data = request.json
        pb_number = data.get("pbNumber")
        password = data.get("password")

        if not pb_number or not password:
            return jsonify({"error": "PB Number and password are required"}), 400

        with get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT name, role
                    FROM users
                    WHERE pb_number = :1 AND password = :2
                    AND role = 'admin'
                """, [pb_number, password])

                admin = cursor.fetchone()

        if not admin:
            return jsonify({"error": "Invalid credentials or not an admin"}), 401

        name, role = admin

        log_action(
            action="Admin Login",
            entity_name=name,
            performed_by=name,
            details="Admin logged in"
        )

        return jsonify({
            "message": "Admin login successful",
            "name": name,
            "pbNumber": pb_number,
            "role": role
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500