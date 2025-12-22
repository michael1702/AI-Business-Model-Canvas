from .database import db
import uuid
from datetime import datetime

class UserModel(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    
    # Beziehung: Ein User hat viele BMCs
    # cascade="all, delete-orphan" löscht die BMCs, wenn der User gelöscht wird
    bmcs = db.relationship("BMCModel", backref="user", cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "id": self.id,
            "email": self.email
        }

class BMCModel(db.Model):
    __tablename__ = 'bmcs'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    # Fremdschlüssel zum User
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    name = db.Column(db.String(200), nullable=True)
    # Wir speichern die 9 Felder des BMC als JSON
    data = db.Column(db.JSON, nullable=True) 
    updated = db.Column(db.String(50), default=lambda: datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"))

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "data": self.data,
            "updated": self.updated
        }