from flask import Blueprint, request, jsonify
import oracledb
from history import log_action
from datetime import datetime

dispatch_bp = Blueprint("dispatch", __name__)

# ---------------- Oracle Connection ----------------
def get_connection():
    return oracledb.connect(
        user="FMD_IT",
        password="fmd123",
        dsn="localhost:1521/xepdb1"
    )


# 🔹 Create Dispatch
@dispatch_bp.route("/create-dispatch", methods=["POST"])
def create_dispatch():
    try:
        data = request.json

        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
        INSERT INTO DISPATCHES (
            DOCUMENT_REF_NO,
            CREATED_BY_PB,
            CREATED_BY_NAME,
            INWARD_NUMBER,
            AGENCY,
            TO_ADDRESS,
            TO_PB_NO,
            SUBJECT,
            DOCUMENT_TYPE,
            MISC_TEXT,
            REMARK,
            FILE_STATUS,
            CREATED_AT
        ) VALUES (
            :document_ref_no,
            :created_by_pb,
            :created_by_name,
            :inward_number,
            :agency,
            :to_address,
            :to_pb_no,
            :subject,
            :document_type,
            :misc_text,
            :remark,
            :file_status,
            :created_at
        )
        """, {
            "document_ref_no": data.get("documentRefNo"),
            "created_by_pb": int(data.get("createdByPb")),
            "created_by_name": data.get("createdByName"),
            "inward_number": data.get("inwardNumber"),
            "agency": data.get("agency"),
            "to_address": data.get("toAddress"),
            "to_pb_no": int(data.get("toPbNumber")) if data.get("toPbNumber") else None,
            "subject": data.get("subject"),
            "document_type": data.get("documentType"),
            "misc_text": data.get("miscellaneousText"),
            "remark": data.get("remark"),
            "file_status": "open",
            "created_at": datetime.now()
        })

        conn.commit()

        log_action(
            action="Dispatch Created",
            entity_name=data.get("inwardNumber"),
            performed_by=data.get("createdByName"),
            details=f"Dispatch '{data.get('inwardNumber')}' created"
        )

        cursor.close()
        conn.close()

        return jsonify({"message": "Dispatch created successfully"}), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# 🔹 Get Dispatches
@dispatch_bp.route("/dispatches", methods=["GET"])
def get_dispatches():
    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
        SELECT ID, DOCUMENT_REF_NO, CREATED_BY_PB, CREATED_BY_NAME,
               INWARD_NUMBER, AGENCY, TO_ADDRESS, TO_PB_NO,
               SUBJECT, DOCUMENT_TYPE, MISC_TEXT, REMARK,
               FILE_STATUS, REPLIED_ON, REPLIED_BY, CREATED_AT
        FROM DISPATCHES
        ORDER BY CREATED_AT DESC
        """)

        columns = [col[0].lower() for col in cursor.description]
        rows = cursor.fetchall()

        result = [dict(zip(columns, r)) for r in rows]

        cursor.close()
        conn.close()

        return jsonify(result), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# 🔹 Update Dispatch
@dispatch_bp.route("/update-dispatch/<int:id>", methods=["PUT"])
def update_dispatch(id):
    try:
        data = request.json

        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            "SELECT INWARD_NUMBER, CREATED_BY_NAME FROM DISPATCHES WHERE ID = :id",
            {"id": id}
        )
        row = cursor.fetchone()

        if not row:
            return jsonify({"error": "Dispatch not found"}), 404

        inward_number, name = row

        cursor.execute("""
        UPDATE DISPATCHES
        SET REMARK = :remark,
            FILE_STATUS = :status,
            REPLIED_ON = :replied_on,
            REPLIED_BY = :replied_by
        WHERE ID = :id
        """, {
            "remark": data.get("remark"),
            "status": data.get("status"),
            "replied_on": datetime.now(),
            "replied_by": data.get("repliedBy"),
            "id": id
        }) 

        conn.commit()


        log_action(
            action="Dispatch Updated",
            entity_name=inward_number,
            performed_by=name,
            details=f"Dispatch '{inward_number}' updated"
        )

        cursor.close()
        conn.close()

        return jsonify({"message": "Updated successfully"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500