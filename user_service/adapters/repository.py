import uuid
from datetime import datetime
from typing import Optional, List
from dataclasses import dataclass
from sqlalchemy.exc import IntegrityError

# Import der DB und Modelle
from ..database import db
from ..models import UserModel, BMCModel

@dataclass
class User:
    """Domain object (bleibt schlank)"""
    id: str
    email: str
    password_hash: str

class UserRepo:
    """Repository implementation using SQLAlchemy."""

    # --- User Methoden (bereits bekannt) ---
    def get_by_email(self, email: str) -> Optional[User]:
        model = db.session.query(UserModel).filter_by(email=email).first()
        return self._to_domain(model) if model else None

    def create_user(self, email: str, password_hash: str) -> Optional[User]:
            # WICHTIG: Hier muss UserModel stehen, nicht User!
            new_user = UserModel(email=email, password_hash=password_hash)
            
            db.session.add(new_user)
            try:
                db.session.commit()
                # Wir wandeln das DB-Modell in das Domain-Objekt um
                return self._to_domain(new_user)
            except IntegrityError:
                db.session.rollback()
                return None
            except Exception as e:
                db.session.rollback()
                raise e

    def get_by_id(self, user_id: str) -> Optional[User]:
        model = db.session.get(UserModel, user_id)
        return self._to_domain(model) if model else None

    def _to_domain(self, model: UserModel) -> User:
        return User(id=model.id, email=model.email, password_hash=model.password_hash)

    # --- BMC Methoden (NEU für SQL) ---

    def list_bmcs(self, user_id: str) -> List[dict]:
        """Liest alle BMCs eines Users aus der DB."""
        # SQL: SELECT * FROM bmcs WHERE user_id = ...
        bmcs = db.session.query(BMCModel).filter_by(user_id=user_id).all()
        return [b.to_dict() for b in bmcs]

    def upsert_bmc(self, user_id: str, *, bmc_id: Optional[str], name: str, data: dict) -> dict:
        """Erstellt oder aktualisiert einen BMC in der DB."""
        now = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        
        # Prüfen, ob User existiert (wegen Foreign Key Constraint wichtig)
        if not self.get_by_id(user_id):
             raise ValueError("user_not_found")

        if bmc_id:
            # Versuch, existierenden BMC zu laden
            # SQL: SELECT * FROM bmcs WHERE id = ... AND user_id = ...
            bmc_entry = db.session.query(BMCModel).filter_by(id=bmc_id, user_id=user_id).first()
            if bmc_entry:
                # Update
                bmc_entry.name = name
                bmc_entry.data = data
                bmc_entry.updated = now
                db.session.commit()
                return bmc_entry.to_dict()
        
        # Create New
        new_bmc = BMCModel(
            user_id=user_id,
            name=name,
            data=data,
            updated=now
        )
        db.session.add(new_bmc)
        db.session.commit()
        return new_bmc.to_dict()

    def get_bmc(self, user_id: str, bmc_id: str) -> Optional[dict]:
        """Holt einen spezifischen BMC aus der DB."""
        bmc_entry = db.session.query(BMCModel).filter_by(id=bmc_id, user_id=user_id).first()
        return bmc_entry.to_dict() if bmc_entry else None

    def delete_bmc(self, user_id: str, bmc_id: str) -> bool:
        """Löscht einen BMC aus der DB."""
        bmc_entry = db.session.query(BMCModel).filter_by(id=bmc_id, user_id=user_id).first()
        if not bmc_entry:
            return False
        
        db.session.delete(bmc_entry)
        db.session.commit()
        return True
    
_repo = UserRepo()