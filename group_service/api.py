from flask import Blueprint, request, jsonify
import os, requests
from .adapters.repository import _repo


try:
    from .security import decode_token
except ImportError:
    # Fallback, falls du die Datei noch nicht kopiert hast
    print("WARNUNG: security.py fehlt! Nutze Dummy-Token-Logik.")
    def decode_token(token): return {"sub": "1"} 

api = Blueprint("group_api", __name__, url_prefix="/api/v1/groups")
USER_SERVICE_URL = os.getenv("USER_SERVICE_URL", "http://user-service:5002")

# --- AUTHENTIFIZIERUNG 
# Wir nutzen diese Funktion, da wir den Decorator aus user_service nicht importieren können.
def _require_auth():
    auth = request.headers.get("Authorization", "")
    if not auth.startswith("Bearer "):
        return None, (jsonify({"error": "missing_bearer_token"}), 401)
    try:
        token = auth.split(" ", 1)[1]
    except IndexError:
        return None, (jsonify({"error": "invalid_auth_header"}), 401)
    
    payload = decode_token(token)
    if not payload:
        return None, (jsonify({"error": "invalid_or_expired_token"}), 401)
    return payload, None, token  # <--- WICHTIG: Token zurückgeben für Weiterleitung!



# --- HELPER: Kommunikation mit User Service ---
def resolve_email_to_id(email, auth_token):
    try:
        resp = requests.post(
            f"{USER_SERVICE_URL}/api/v1/users/lookup",
            json={"email": email},
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        if resp.status_code == 200:
            return resp.json(), None
        return None, resp.json().get("error", "lookup_failed")
    except Exception as e:
        return None, str(e)

def resolve_ids_to_emails(user_ids, auth_token):
    try:
        # Wir fragen den User Service nach Details für alle IDs auf einmal, user_ids werden in Liste umgewandelt für die JSON
        resp = requests.post(
            f"{USER_SERVICE_URL}/api/v1/users/batch-info",
            json={"ids": list(user_ids)},
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        if resp.status_code == 200:
            return resp.json() # Erwartet Liste: [{"id": "...", "email": "..."}, ...]
        print(f"User Service Error: {resp.status_code} - {resp.text}", flush=True)
        return []
    except Exception as e:
        # NEU: Exception ausgeben
        print(f"Connection Error to User Service: {e}", flush=True)
        return []
    

@api.get("/<group_id>/bmcs")
def list_group_bmcs(group_id: str):
    payload, err, token = _require_auth()
    if err: return err
    user_id = payload["sub"]
    group = _repo.get_by_id(group_id)
    if not group or user_id not in group.members:
        return jsonify({"error": "group_not_found"}), 404
    slim_bmcs = [{"id": b["id"], "name": b["name"], "updated": b["updated"]} for b in _repo.list_group_bmcs(group_id)]
    return jsonify(slim_bmcs), 200

@api.post("/<group_id>/bmcs")
def upsert_group_bmc(group_id: str):
    payload, err, token = _require_auth()
    if err: return err
    user_id = payload["sub"]
    group = _repo.get_by_id(group_id)
    if not group or user_id not in group.members:
        return jsonify({"error": "group_not_found"}), 404
    body = request.get_json(force=True) or {}
    name = body.get("name") or ""
    data = body.get("data") or {}
    bmc_id = body.get("id")
    
    # Nutze Repo direkt (wie in beiden Versionen okay)
    saved = _repo.upsert_group_bmc(group_id, bmc_id=bmc_id, name=name, data=data)
    return jsonify(saved), 200

@api.get("/<group_id>/bmcs/<bmc_id>")
def get_group_bmc(group_id: str, bmc_id: str):
    payload, err, token = _require_auth()
    if err: return err
    user_id = payload["sub"]
    group = _repo.get_by_id(group_id)
    if not group or user_id not in group.members: return jsonify({"error": "group_not_found"}), 404
    bmc = _repo.get_group_bmc(group_id, bmc_id)
    if not bmc: return jsonify({"error": "bmc_not_found"}), 404
    return jsonify(bmc), 200


@api.post("/")
def create_group():
    payload, err, token = _require_auth() # <--- Unpacking updated
    if err: return err
    
    body = request.get_json(force=True) or {}
    name = body.get("name")
    owner_id = payload["sub"]

    try:
        group = _repo.create_group(name, owner_id) 
        return jsonify(group.to_dict()), 201 
    except Exception as ex:
        return jsonify({"error": str(ex)}), 400

@api.get("/")
def list_my_groups():
    payload, err, token = _require_auth()
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
    payload, err, token = _require_auth()
    if err: return err
    user_id = payload["sub"]
    
    group = _repo.get_by_id(group_id)
    if not group: return jsonify({"error": "group_not_found"}), 404
    
    # Prüfen, ob der Anfragende überhaupt Mitglied ist
    if user_id not in group.members: 
        return jsonify({"error": "access_denied"}), 403

    # 1. Wir holen die Infos für ALLE Mitglieder auf einmal
    members_info = resolve_ids_to_emails(group.members, token)
    
    # 2. Wir bauen eine Map für schnellen Zugriff: ID -> Email
    email_map = {m["id"]: m["email"] for m in members_info}

    # 3. Wir bauen die Antwort zusammen
    member_details = []
    for member_id in group.members:
        member_details.append({
            "id": member_id, 
            # Hier setzen wir die Email ein (oder "Unknown", falls User gelöscht wurde)
            "email": email_map.get(member_id, "Unknown User"), 
            "is_owner": member_id == group.owner_id
        })

    return jsonify({
        "id": group.id,
        "name": group.name,
        "owner_id": group.owner_id,
        "members": member_details 
    }), 200


@api.post("/<group_id>/members")
def add_member_to_group_route(group_id: str):
    payload, err, token = _require_auth()
    if err: return err
    
    requester_id = payload["sub"]
    group = _repo.get_by_id(group_id)
    if not group: return jsonify({"error": "group_not_found"}), 404
    
    # Nur Owner darf hinzufügen
    if group.owner_id != requester_id:
        return jsonify({"error": "only_owner_can_add_members"}), 403

    body = request.get_json(force=True) or {}
    email = body.get("email")
    if not email: return jsonify({"error": "missing_email"}), 400

    # 1. User ID per Email holen
    user_info, error_msg = resolve_email_to_id(email, token)
    if not user_info:
        return jsonify({"error": f"User not found or service error: {error_msg}"}), 404
    
    new_member_id = user_info["id"]

    # 2. Prüfen ob schon drin
    if new_member_id in group.members:
        return jsonify({"error": "user_already_in_group"}), 409

    # 3. Hinzufügen
    updated_group = _repo.add_member(group.id, new_member_id)
    
    if updated_group:
            return jsonify({"status": "added", "user": user_info}), 200
    else:
            return jsonify({"error": "database_error"}), 500


@api.delete("/<group_id>/members/<member_id>")
def remove_member_from_group_route(group_id: str, member_id: str):
    payload, err, token = _require_auth()
    if err: return err
    
    requester_id = payload["sub"]
    group = _repo.get_by_id(group_id)
    if not group: return jsonify({"error": "group_not_found"}), 404

    # Nur Owner darf löschen oder User sich selbst
    if group.owner_id != requester_id and member_id != requester_id:
        return jsonify({"error": "permission_denied"}), 403
    
    if member_id == group.owner_id:
        return jsonify({"error": "owner_cannot_leave_group"}), 400

    # FIX: Nutze die neue Repo-Methode remove_member
    success = _repo.remove_member(group.id, member_id)
    
    if success:
        return jsonify({"status": "removed"}), 200
    else:
        return jsonify({"error": "member_not_found"}), 404