# group_service/api.py
from flask import Blueprint, request, jsonify
import json
from .adapters.repository import _repo
from .domain import create_new_group, add_member_to_group
# Assuming this is available in the environment
from user_service.security import decode_token 
# "Cheat" for monolithic prototype: Access UserRepo to lookup emails
from user_service.adapters.repository import UserRepo 
_user_repo = UserRepo() # Shared memory instance from user_service

api = Blueprint("group_api", __name__, url_prefix="/api/v1/groups")

def _require_auth():
    auth = request.headers.get("Authorization", "")
    if not auth.startswith("Bearer "):
        return None, (jsonify({"error": "missing_bearer_token"}), 401)
    payload = decode_token(auth.split(" ", 1)[1])
    if not payload:
        return None, (jsonify({"error": "invalid_or_expired_token"}), 401)
    return payload, None

# --- Group Management Routes ---

@api.post("/")
def create_group():
    payload, err = _require_auth()
    if err: return err
    body = request.get_json(force=True) or {}
    name = body.get("name")
    owner_id = payload["sub"]
    try:
        group = create_new_group(name, owner_id, _repo)
        return jsonify({"id": group.id, "name": group.name, "owner_id": group.owner_id}), 201
    except ValueError as ex:
        return jsonify({"error": str(ex)}), 400

@api.get("/")
def list_my_groups():
    payload, err = _require_auth()
    if err: return err
    user_id = payload["sub"]
    groups = _repo.list_groups_for_user(user_id)
    slim_groups = [{
        "id": g.id, 
        "name": g.name, 
        "is_owner": g.owner_id == user_id, 
        "member_count": len(g.members)
    } for g in groups]
    return jsonify(slim_groups), 200

@api.get("/<group_id>")
def get_group_details(group_id: str):
    payload, err = _require_auth()
    if err: return err
    user_id = payload["sub"]
    group = _repo.get_by_id(group_id)
    if not group: return jsonify({"error": "group_not_found"}), 404
    if user_id not in group.members: return jsonify({"error": "access_denied"}), 403

    # Resolve member names/emails for display
    member_details = []
    for member_id in group.members:
        u = _user_repo.get_by_id(member_id)
        if u:
            member_details.append({"id": u.id, "email": u.email, "is_owner": member_id == group.owner_id})

    return jsonify({
        "id": group.id,
        "name": group.name,
        "owner_id": group.owner_id,
        "members": member_details # Return detailed list
    }), 200

@api.post("/<group_id>/members")
def add_member_to_group_route(group_id: str):
    payload, err = _require_auth()
    if err: return err
    
    body = request.get_json(force=True) or {}
    email = body.get("email") # Changed from user_id to email for better UX
    admin_id = payload["sub"]
    
    if not email:
        return jsonify({"error": "missing_email"}), 400

    # Lookup User ID by Email
    user_to_add = _user_repo.get_by_email(email)
    if not user_to_add:
        return jsonify({"error": "user_not_found"}), 404

    try:
        group = add_member_to_group(group_id, user_to_add.id, admin_id, _repo)
        return jsonify({"status": "member_added", "group_id": group.id, "member_count": len(group.members)}), 200
    except ValueError as ex:
        return jsonify({"error": str(ex)}), 400
    except PermissionError as ex:
        return jsonify({"error": str(ex)}), 403

# --- Group BMC Management Routes ---

@api.get("/<group_id>/bmcs")
def list_group_bmcs(group_id: str):
    payload, err = _require_auth()
    if err: return err
    user_id = payload["sub"]
    group = _repo.get_by_id(group_id)
    if not group or user_id not in group.members:
        return jsonify({"error": "group_not_found"}), 404
    slim_bmcs = [{"id": b["id"], "name": b["name"], "updated": b["updated"]} for b in _repo.list_group_bmcs(group_id)]
    return jsonify(slim_bmcs), 200

@api.post("/<group_id>/bmcs")
def upsert_group_bmc(group_id: str):
    payload, err = _require_auth()
    if err: return err
    user_id = payload["sub"]
    group = _repo.get_by_id(group_id)
    if not group or user_id not in group.members:
        return jsonify({"error": "group_not_found"}), 404
    body = request.get_json(force=True) or {}
    name = body.get("name") or ""
    data = body.get("data") or {}
    bmc_id = body.get("id")
    if not name or not isinstance(data, dict): return jsonify({"error": "invalid_payload"}), 400
    saved = _repo.upsert_group_bmc(group_id, bmc_id=bmc_id, name=name, data=data)
    return jsonify(saved), 200

@api.get("/<group_id>/bmcs/<bmc_id>")
def get_group_bmc(group_id: str, bmc_id: str):
    payload, err = _require_auth()
    if err: return err
    user_id = payload["sub"]
    group = _repo.get_by_id(group_id)
    if not group or user_id not in group.members: return jsonify({"error": "group_not_found"}), 404
    bmc = _repo.get_group_bmc(group_id, bmc_id)
    if not bmc: return jsonify({"error": "bmc_not_found"}), 404
    return jsonify(bmc), 200
