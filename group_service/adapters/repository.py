
from typing import List, Optional, Set
from datetime import datetime
import uuid

# Import the database and models
from ..database import db
from ..models import GroupModel, MemberModel, SharedBMCModel
from ..domain import Group


class GroupRepo:
    """SQLAlchemy implementation of Group Repository preserving original method names."""

    def get_by_id(self, group_id: str) -> Optional[Group]:
        g_model = db.session.get(GroupModel, group_id)
        return self._to_domain(g_model) if g_model else None

    def create_group(self, name: str, owner_id: str) -> Group:
        group_id = str(uuid.uuid4())
        # Replaces the old create_group logic with SQL
        new_group = GroupModel(id=group_id, name=name, owner_id=owner_id)

        # The owner is implicitly a member (optional, depending on logic,
        # but in the old code, the owner was in the 'members' set)
        member_id = str(uuid.uuid4())
        owner_member = MemberModel(id = member_id, group_id=group_id, user_id=owner_id)

        db.session.add(new_group)
        db.session.add(owner_member)  # Add owner directly as a member
        db.session.commit()

        return self._to_domain(new_group)

    def list_groups_for_user(self, user_id: str) -> List[Group]:
        """Finds all groups for a user (as owner or member)."""
        # 1. Groups where the user is the owner
        owned = db.session.query(GroupModel).filter_by(owner_id=user_id).all()

        # 2. Groups where the user is a member (via join)
        member_groups = db.session.query(GroupModel).join(MemberModel).filter(MemberModel.user_id == user_id).all()

        # Merge and remove duplicates (set)
        all_groups = list(set(owned + member_groups))
        return [self._to_domain(g) for g in all_groups]

    def add_member(self, group_id: str, user_id: str) -> Optional[Group]:
        """Adds a member to the group."""
        # First check if the group exists
        g_model = db.session.get(GroupModel, group_id)
        if not g_model:
            return None

        # Check if already a member
        exists = db.session.query(MemberModel).filter_by(group_id=group_id, user_id=user_id).first()
        if not exists:
            new_member_id = str(uuid.uuid4())
            new_member = MemberModel(id=new_member_id, group_id=group_id, user_id=user_id)
            db.session.add(new_member)
            db.session.commit()

            # WICHTIG: Session refreshen, damit die neue Relation geladen wird
            db.session.refresh(g_model)

        # Return the updated object
        return self._to_domain(g_model)

    def upsert_group_bmc(self, group_id: str, *, bmc_id: Optional[str], name: str, data: dict) -> Optional[dict]:
        """Creates or updates a shared BMC (Business Model Canvas)."""
        # Check if the group exists (due to foreign key)
        g_model = db.session.get(GroupModel, group_id)
        if not g_model:
            return None

        now = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

        if bmc_id:
            # Try to update
            bmc_entry = db.session.query(SharedBMCModel).filter_by(id=bmc_id, group_id=group_id).first()
            if bmc_entry:
                bmc_entry.name = name
                bmc_entry.data = data
                bmc_entry.updated = now
                db.session.commit()
                return bmc_entry.to_dict()

        # Create new
        new_bmc_id = str(uuid.uuid4())
        new_bmc = SharedBMCModel(
            id=new_bmc_id,
            group_id=group_id,
            name=name,
            data=data,
            updated=now
        )
        db.session.add(new_bmc)
        db.session.commit()
        return new_bmc.to_dict()

    def get_group_bmc(self, group_id: str, bmc_id: str) -> Optional[dict]:
        """Retrieves a specific BMC (Business Model Canvas)."""
        bmc_entry = db.session.query(SharedBMCModel).filter_by(id=bmc_id, group_id=group_id).first()
        return bmc_entry.to_dict() if bmc_entry else None

    def _to_domain(self, model: GroupModel) -> Group:
        """Helper method: Converts DB model to domain object."""
        g = Group(id=model.id, name=model.name, owner_id=model.owner_id)
        # Convert members from SQL list to Set[str] (as in the old code)
        if model.members:
            g.members = {m.user_id for m in model.members}
        # Convert BMCs to a list of dicts
        if model.bmcs:
            g.bmcs = [b.to_dict() for b in model.bmcs]
        return g

_repo = GroupRepo()