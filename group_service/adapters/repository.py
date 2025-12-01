# group_service/adapters/repository.py
import uuid
from datetime import datetime
from typing import Optional, Dict, List, Set
from dataclasses import dataclass, field

@dataclass
class Group:
    """Dataclass for a Group."""
    id: str
    name: str
    owner_id: str
    members: Set[str] = field(default_factory=set)  # Set of user IDs
    bmcs: List[dict] = field(default_factory=list)  # List of shared BMC objects: {id, name, data, updated}
    created_at: str = field(default_factory=lambda: datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"))

class GroupRepo:
    """In-memory repository for Group objects."""
    def __init__(self):
        self._by_id: Dict[str, Group] = {}

    def get_by_id(self, group_id: str) -> Optional[Group]:
        return self._by_id.get(group_id)

    def create_group(self, name: str, owner_id: str) -> Group:
        group_id = str(uuid.uuid4())
        # The owner is automatically the first member
        g = Group(id=group_id, name=name, owner_id=owner_id, members={owner_id})
        self._by_id[group_id] = g
        return g

    def list_groups_for_user(self, user_id: str) -> List[Group]:
        """Returns all groups the user is a member of."""
        return [g for g in self._by_id.values() if user_id in g.members]

    def add_member(self, group_id: str, user_id: str) -> Optional[Group]:
        """Adds a member to a group."""
        g = self.get_by_id(group_id)
        if g:
            g.members.add(user_id)
        return g
    
    def upsert_group_bmc(self, group_id: str, *, bmc_id: Optional[str], name: str, data: dict) -> Optional[dict]:
        """Create or update a BMC shared with this group."""
        g = self.get_by_id(group_id)
        if not g:
            return None
        now = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        
        if bmc_id:
            # Update existing
            for b in g.bmcs:
                if b["id"] == bmc_id:
                    b["name"] = name
                    b["data"] = data
                    b["updated"] = now
                    return b
        
        # Create new
        new_bmc = {"id": str(uuid.uuid4()), "name": name, "data": data, "updated": now}
        g.bmcs.append(new_bmc)
        return new_bmc

    def get_group_bmc(self, group_id: str, bmc_id: str) -> Optional[dict]:
        """Get a specific shared BMC by ID."""
        g = self.get_by_id(group_id)
        if not g:
            return None
        for b in g.bmcs:
            if b["id"] == bmc_id:
                return b
        return None
    
    def list_group_bmcs(self, group_id: str) -> List[dict]:
        """List all BMCs shared with this group."""
        g = self.get_by_id(group_id)
        return g.bmcs[:] if g else []

# Global instance for shared memory storage
_repo = GroupRepo()