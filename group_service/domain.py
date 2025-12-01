# group_service/domain.py
from .adapters.repository import GroupRepo, Group
from typing import Optional

def create_new_group(name: str, owner_id: str, repo: GroupRepo) -> Group:
    """Creates a new group with the given user as owner and first member."""
    if not name or len(name.strip()) < 3:
        raise ValueError("Group name must be at least 3 characters long.")
    return repo.create_group(name=name, owner_id=owner_id)

def add_member_to_group(group_id: str, new_member_id: str, admin_id: str, repo: GroupRepo) -> Group:
    """Adds a member to a group if the inviter is the owner."""
    group = repo.get_by_id(group_id)
    if not group:
        raise ValueError("group_not_found")
    
    if admin_id != group.owner_id:
        raise PermissionError("only_owner_can_add_members")
    
    # Check if member already exists (optional, repo.add_member is idempotent)
    if new_member_id in group.members:
        raise ValueError("member_already_exists")
        
    repo.add_member(group_id, new_member_id)
    return group