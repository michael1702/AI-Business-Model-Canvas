# user_service/adapters/repo.py
from typing import Optional, Dict, List
from dataclasses import dataclass, field
import uuid
from datetime import datetime

@dataclass
class User:
    id: str
    email: str
    password_hash: str
    bmcs: List[dict] = field(default_factory=list)  # each: {id,name,data,updated}

class UserRepo:
    def __init__(self):
        self._by_email: Dict[str, User] = {}
        self._by_id: Dict[str, User] = {}

    def get_by_email(self, email: str) -> Optional[User]:
        return self._by_email.get((email or "").lower())

    def create_user(self, email: str, password_hash: str) -> User:
        email_l = (email or "").lower()
        if self.get_by_email(email_l):
            raise ValueError("email_already_exists")
        u = User(id=str(uuid.uuid4()), email=email_l, password_hash=password_hash)
        self._by_email[email_l] = u
        self._by_id[u.id] = u
        return u

    def get_by_id(self, user_id: str) -> Optional[User]:
        return self._by_id.get(user_id)

    def list_bmcs(self, user_id: str) -> List[dict]:
        u = self.get_by_id(user_id)
        return u.bmcs[:] if u else []

    def upsert_bmc(self, user_id: str, *, bmc_id: Optional[str], name: str, data: dict) -> dict:
        """Create or update a BMC for this user."""
        u = self.get_by_id(user_id)
        if not u:
            raise ValueError("user_not_found")
        now = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        if bmc_id:
            # update existing
            for b in u.bmcs:
                if b["id"] == bmc_id:
                    b["name"] = name
                    b["data"] = data
                    b["updated"] = now
                    return b
        # create new
        new_bmc = {"id": str(uuid.uuid4()), "name": name, "data": data, "updated": now}
        u.bmcs.append(new_bmc)
        return new_bmc

    def get_bmc(self, user_id: str, bmc_id: str) -> Optional[dict]:
        u = self.get_by_id(user_id)
        if not u:
            return None
        for b in u.bmcs:
            if b["id"] == bmc_id:
                return b
        return None
    

    def delete_bmc(self, user_id: str, bmc_id: str) -> bool:
        u = self.get_by_id(user_id)
        if not u:
            return False
        before = len(u.bmcs)
        u.bmcs = [b for b in u.bmcs if b["id"] != bmc_id]
        return len(u.bmcs) != before

