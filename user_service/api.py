# user_service/api.py
from flask import Blueprint, request, jsonify
from .adapters.repository import UserRepo
from .domain import register_user, authenticate_user
from .security import create_access_token, decode_token

api = Blueprint("user_api", __name__, url_prefix="/api/v1/users")
_repo = UserRepo()


def _require_auth():
    auth = request.headers.get("Authorization", "")
    if not auth.startswith("Bearer "):
        return None, (jsonify({"error": "missing_bearer_token"}), 401)
    payload = decode_token(auth.split(" ", 1)[1])
    if not payload:
        return None, (jsonify({"error": "invalid_or_expired_token"}), 401)
    return payload, None

@api.post("/register")
def register():
    data = request.get_json(force=True) or {}
    try:
        u = register_user(data.get("email"), data.get("password"), _repo)
        return jsonify({"id": u.id, "email": u.email}), 201
    except ValueError as ex:
        return jsonify({"error": str(ex)}), 400

@api.post("/login")
def login():
    data = request.get_json(force=True) or {}
    try:
        u = authenticate_user(data.get("email"), data.get("password"), _repo)
        token = create_access_token(u.id, u.email)
        return jsonify({"access_token": token, "token_type": "Bearer"}), 200
    except ValueError:
        return jsonify({"error": "invalid_credentials"}), 401

@api.get("/me")
def me():
    payload, err = _require_auth()
    if err: return err
    return jsonify({"id": payload["sub"], "email": payload["email"]}), 200

@api.get("/me/bmcs")
def my_bmcs():
    payload, err = _require_auth()
    if err: return err
    items = _repo.list_bmcs(payload["sub"])
    # only expose id, name, updated in the list
    slim = [{"id": b["id"], "name": b["name"], "updated": b["updated"]} for b in items]
    return jsonify(slim), 200

@api.post("/me/bmcs")
def upsert_my_bmc():
    """Create/update a BMC for the authenticated user.
    Body: {id?:str, name:str, data:object}"""
    payload, err = _require_auth()
    if err: return err
    body = request.get_json(force=True) or {}
    name = body.get("name") or ""
    data = body.get("data") or {}
    bmc_id = body.get("id")
    if not name or not isinstance(data, dict):
        return jsonify({"error": "invalid_payload"}), 400
    saved = _repo.upsert_bmc(payload["sub"], bmc_id=bmc_id, name=name, data=data)
    return jsonify(saved), 200

@api.get("/me/bmcs/<bmc_id>")
def get_my_bmc(bmc_id: str):
    payload, err = _require_auth()
    if err: return err
    b = _repo.get_bmc(payload["sub"], bmc_id)
    if not b:
        return jsonify({"error": "not_found"}), 404
    return jsonify(b), 200

@api.delete("/me/bmcs/<bmc_id>")
def delete_my_bmc(bmc_id: str):
    payload, err = _require_auth()
    if err: return err
    ok = _repo.delete_bmc(payload["sub"], bmc_id)
    if not ok:
        return jsonify({"error": "not_found"}), 404
    return jsonify({"status": "deleted"}), 200


@api.post("/lookup")
def lookup_user():
    # Dieser Endpoint sollte idealerweise geschützt sein, 
    # aber für interne Kommunikation nutzen wir hier den User-Token weiter.
    # Wir erwarten: {"email": "..."}
    
    body = request.get_json(force=True) or {}
    email = body.get("email")
    
    if not email:
        return jsonify({"error": "missing_email"}), 400
        
    user = _repo.get_by_email(email)
    if not user:
        return jsonify({"error": "user_not_found"}), 404
        
    return jsonify({"id": user.id, "email": user.email}), 200

#in Endpoint um Details für mehrere IDs zu holen (für die Anzeige der Mitgliederliste)
@api.post("/batch-info")
def get_users_info():
    try:
        # Wir erwarten eine Liste von IDs: {"ids": ["uuid-1", "uuid-2"]}
        body = request.get_json(force=True) or {}
        user_ids = body.get("ids", [])
        
        results = []
        for uid in user_ids:
            u = _repo.get_by_id(uid)
            if u:
                results.append({"id": u.id, "email": u.email})
                
        return jsonify(results), 200
    except Exception as e:
        print(f"Error in batch-info: {e}", flush=True) # Debugging-Ausgabe
        return jsonify({"error": str(e)}), 500
