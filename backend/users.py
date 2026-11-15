from flask import Blueprint, request, jsonify
import oracledb
from history import log_action

users_bp = Blueprint("users", __name__)

# ---------------- DB CONNECTION ----------------
def get_connection():
    return oracledb.connect(
        user="FMD_IT",
        password="fmd123",
        dsn="localhost:1521/xepdb1"
    )

# ---------------- REGISTER USER ----------------
@users_bp.route("/register", methods=["POST"])
def register_user():
    try:
        data = request.json

        name = data.get("name")
        pb_number = data.get("pbNumber")
        password = data.get("password")
        role = data.get("role")
        performed_by = data.get("performedBy")

        if not name or not pb_number or not password:
            return jsonify({"error": "All fields are required"}), 400

        with get_connection() as conn:
            with conn.cursor() as cursor:

                # check duplicate PB number
                cursor.execute(
                    "SELECT COUNT(*) FROM users WHERE pb_number = :1",
                    [pb_number]
                )
                count = cursor.fetchone()[0]

                if count > 0:
                    return jsonify({"error": "PB Number already exists"}), 400

                # insert user
                cursor.execute("""
                    INSERT INTO users (name, pb_number, password, role)
                    VALUES (:1, :2, :3, :4)
                """, [name, pb_number, password, role])

                conn.commit()

        log_action(
            action="User Created",
            entity_name=name,
            performed_by=performed_by,
            details=f"User {name} created with role {role}"
        )

        return jsonify({
            "message": "User registered successfully",
            "pbNumber": pb_number,
            "role": role
        }), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ---------------- GET ALL USERS ----------------
@users_bp.route("/users", methods=["GET"])
def get_users():
    try:
        with get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT name, pb_number, role
                    FROM users
                    ORDER BY pb_number
                """)
                rows = cursor.fetchall()

        return jsonify([
            {
                "name": r[0],
                "pbNumber": r[1],
                "role": r[2]
            }
            for r in rows
        ]), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ---------------- DELETE USER ----------------
@users_bp.route("/delete-user/<int:pb_number>", methods=["DELETE"])
def delete_user(pb_number):
    try:
        admin_name = request.headers.get("adminName")

        with get_connection() as conn:
            with conn.cursor() as cursor:

                cursor.execute(
                    "SELECT name FROM users WHERE pb_number = :1",
                    [pb_number]
                )
                user = cursor.fetchone()

                if not user:
                    return jsonify({"error": "User not found"}), 404

                user_name = user[0]

                cursor.execute(
                    "DELETE FROM users WHERE pb_number = :1",
                    [pb_number]
                )

                conn.commit()

        log_action(
            action="User Deleted",
            entity_name=user_name,
            performed_by=admin_name,
            details=f"User {user_name} deleted"
        )

        return jsonify({"message": "User deleted successfully"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500