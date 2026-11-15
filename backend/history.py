from flask import Blueprint, jsonify
import oracledb

history_bp = Blueprint("history", __name__)

# ---------------- DB CONNECTION ----------------
def get_connection():
    return oracledb.connect(
        user="FMD_IT",
        password="fmd123",
        dsn="localhost:1521/xepdb1"
    )

# ---------------- LOGGER (KEEP HERE) ----------------
def log_action(action, entity_name, performed_by, details):
    try:
        with get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO history
                    (action, entity_name, performed_by, details)
                    VALUES (:1, :2, :3, :4)
                """, [action, entity_name, performed_by, details])

                conn.commit()

    except Exception as e:
        print("History Log Error:", str(e))


# ---------------- HISTORY API ----------------
@history_bp.route("/history", methods=["GET"])
def get_history():
    try:
        with get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT id, action, entity_name, performed_by, timestamp, details
                    FROM history
                    ORDER BY timestamp DESC
                """)
                rows = cursor.fetchall()

        result = [
            {
                "id": r[0],
                "action": r[1],
                "entityName": r[2],
                "performedBy": r[3],
                "timestamp": str(r[4]),
                "details": r[5]
            }
            for r in rows
        ]

        return jsonify(result), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500