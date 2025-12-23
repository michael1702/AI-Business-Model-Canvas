from flask import Blueprint, request, jsonify
# Wir nutzen die lokale Domain-Logik der Alten Version
from .adapters.repository import _repo

# WICHTIG: Damit das hier läuft, muss die security.py im group_service liegen,
# oder wir fangen den Import-Fehler ab.
try:
    from .security import decode_token
except ImportError:
    # Fallback, falls du die Datei noch nicht kopiert hast
    print("WARNUNG: security.py fehlt! Nutze Dummy-Token-Logik.")
    def decode_token(token): return {"sub": "1"} 

api = Blueprint("group_api", __name__, url_prefix="/api/v1/groups")

# --- AUTHENTIFIZIERUNG (Aus der Alten Version) ---
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
    return payload, None

# --- ROUTEN ---

@api.post("/")
def create_group():
    payload, err = _require_auth()
    if err: return err
    
    body = request.get_json(force=True) or {}
    name = body.get("name")
    owner_id = payload["sub"]

    # ÄNDERUNG: Direkt das Repo nutzen, da die Domain-Logik dort integriert wurde
    try:
        # Hier nutzen wir direkt dein Repo, wie du sagtest
        group = _repo.create_group(name, owner_id) 
        return jsonify(group.to_dict()), 201 
        # Hinweis: create_group im Repo gibt bei dir vermutlich schon das Domain-Objekt zurück
        # oder das Model. Falls es ein Model ist, pass auf .to_dict() auf.
    except Exception as ex:
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
    
    # Check Access
    if user_id not in group.members: 
        return jsonify({"error": "access_denied"}), 403

    # CRITICAL FIX: Kein Zugriff auf UserRepo (verursacht Crash)!
    # Wir geben die Member-IDs zurück ohne Email-Lookup.
    member_details = []
    for member_id in group.members:
        member_details.append({
            "id": member_id, 
            "email": "hidden_in_microservice", # E-Mail Auflösung benötigt HTTP-Request
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
    payload, err = _require_auth()
    if err: return err
    
    body = request.get_json(force=True) or {}
    email = body.get("email")
    admin_id = payload["sub"]
    
    if not email:
        return jsonify({"error": "missing_email"}), 400

    # FIX: Wir können UserRepo hier NICHT benutzen.
    # Damit der Code nicht crasht, geben wir "Not Implemented" zurück 
    # oder faken das Hinzufügen, wenn du die ID direkt sendest.
    
    return jsonify({
        "error": "Adding by Email requires User-Service Communication (HTTP). Logic disabled to prevent crash."
    }), 501

# --- BMC Routen (Funktionieren in beiden Versionen ähnlich) ---

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
    
    # Nutze Repo direkt (wie in beiden Versionen okay)
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