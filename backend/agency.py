from flask import Blueprint, request, jsonify
import oracledb
from history import log_action

agency_bp = Blueprint("agency", __name__)

# ---------------- Oracle Connection ----------------
def get_connection():
    return oracledb.connect(
        user="FMD_IT",
        password="fmd123",
        dsn="localhost:1521/xepdb1"
    )

# ---------------- CREATE AGENCY ----------------
@agency_bp.route("/create-agency", methods=["POST"])
def create_agency():
    try:
        data = request.get_json()
        agency_name = data.get("name", "").strip()
        admin_name = data.get("adminName")

        if not agency_name:
            return jsonify({"error": "Agency name is required"}), 400

        with get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    "INSERT INTO agencies (agency_name) VALUES (:name)",
                    {"name": agency_name}
                )
                conn.commit()

        log_action(
            action="Agency Created",
            entity_name=agency_name,
            performed_by=admin_name,
            details=f"Agency '{agency_name}' created"
        )

        return jsonify({"message": "Agency created successfully"}), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ---------------- GET ALL AGENCIES ----------------
@agency_bp.route("/agencies", methods=["GET"])
def get_agencies():
    try:
        with get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT id, agency_name FROM agencies ORDER BY id")
                rows = cursor.fetchall()

        return jsonify([{"id": r[0], "name": r[1]} for r in rows]), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ---------------- DELETE AGENCY ----------------
@agency_bp.route("/delete-agency/<int:agency_id>", methods=["DELETE"])
def delete_agency(agency_id):
    try:
        admin_name = request.headers.get("adminName")

        with get_connection() as conn:
            with conn.cursor() as cursor:

                cursor.execute(
                    "SELECT agency_name FROM agencies WHERE id = :id",
                    {"id": agency_id}
                )
                row = cursor.fetchone()

                if not row:
                    return jsonify({"error": "Agency not found"}), 404

                agency_name = row[0]

                cursor.execute(
                    "DELETE FROM agencies WHERE id = :id",
                    {"id": agency_id}
                )
                conn.commit()

        log_action(
            action="Agency Deleted",
            entity_name=agency_name,
            performed_by=admin_name,
            details=f"Agency '{agency_name}' deleted"
        )

        return jsonify({"message": "Agency deleted successfully"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500