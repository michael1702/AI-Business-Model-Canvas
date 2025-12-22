import logging
from flask import Blueprint, request, jsonify, g
from .adapters.repository import _repo
from user_service.security import login_required
from user_service.adapters.repository import _repo as _user_repo

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

api = Blueprint('group_api', __name__, url_prefix='/api/v1/groups')

# --- GRUPPEN ROUTEN ---

@api.route('/', methods=['POST'])
@login_required
def create_group():
    try:
        data = request.get_json() or {}
        name = data.get('name')
        if not name: return jsonify({"error": "name_required"}), 400
        
        group = _repo.create_group(name, g.user_id)
        return jsonify(group.to_dict()), 201
    except Exception as e:
        logger.error(f"Create Group Error: {e}")
        return jsonify({"error": str(e)}), 500

@api.route('/', methods=['GET'])
@login_required
def list_groups():
    groups = _repo.list_groups_for_user(g.user_id)
    return jsonify([grp.to_dict() for grp in groups]), 200

@api.route('/<group_id>', methods=['GET'])
@login_required
def get_group(group_id):
    """Liefert Details einer einzelnen Gruppe."""
    group = _repo.get_by_id(group_id)
    if not group:
        return jsonify({"error": "group_not_found"}), 404
    return jsonify(group.to_dict()), 200

@api.route('/<group_id>/members', methods=['POST'])
@login_required
def add_member(group_id):
    try:
        data = request.get_json() or {}
        email = data.get('email')
        if not email: return jsonify({"error": "email_required"}), 400
        
        user = _user_repo.get_by_email(email)
        if not user: return jsonify({"error": "user_not_found"}), 404
            
        group = _repo.add_member(group_id, user.id)
        if not group: return jsonify({"error": "group_not_found"}), 404
            
        return jsonify({"status": "member_added", "member_count": len(group.members)}), 200
    except Exception as e:
        logger.error(f"Add Member Error: {e}")
        return jsonify({"error": str(e)}), 500

# --- BMC ROUTEN ---

# NEU: Diese Route fehlte und verursachte den 405 Fehler!
@api.route('/<group_id>/bmcs', methods=['GET'])
@login_required
def list_group_bmcs(group_id):
    """Listet alle BMCs einer Gruppe auf."""
    group = _repo.get_by_id(group_id)
    if not group:
        return jsonify({"error": "group_not_found"}), 404
    
    # Optional: Prüfen ob User Mitglied ist
    if g.user_id not in group.members and g.user_id != group.owner_id:
        return jsonify({"error": "access_denied"}), 403

    return jsonify(group.bmcs), 200

@api.route('/<group_id>/bmcs', methods=['POST'])
@login_required
def upsert_group_bmc(group_id):
    try:
        data = request.get_json() or {}
        name = data.get('name', 'Untitled')
        bmc_data = data.get('data', {})
        bmc_id = data.get('id')
        
        saved = _repo.upsert_group_bmc(group_id, bmc_id=bmc_id, name=name, data=bmc_data)
        if not saved: return jsonify({"error": "group_not_found"}), 404
            
        return jsonify(saved), 200
    except Exception as e:
        logger.error(f"Upsert BMC Error: {e}")
        return jsonify({"error": str(e)}), 500

@api.route('/<group_id>/bmcs/<bmc_id>', methods=['GET'])
@login_required
def get_group_bmc(group_id, bmc_id):
    bmc = _repo.get_group_bmc(group_id, bmc_id)
    if not bmc: return jsonify({"error": "not_found"}), 404
    return jsonify(bmc), 200