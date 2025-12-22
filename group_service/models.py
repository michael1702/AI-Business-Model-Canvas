from .database import db
import uuid
from datetime import datetime

class GroupModel(db.Model):
    __tablename__ = 'groups'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(100), nullable=False)
    owner_id = db.Column(db.String(36), nullable=False)
    
    members = db.relationship("MemberModel", backref="group", cascade="all, delete-orphan")
    bmcs = db.relationship("SharedBMCModel", backref="group", cascade="all, delete-orphan")

class MemberModel(db.Model):
    __tablename__ = 'group_members'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    group_id = db.Column(db.String(36), db.ForeignKey('groups.id'), nullable=False)
    user_id = db.Column(db.String(36), nullable=False)
    joined_at = db.Column(db.String(50), default=lambda: datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"))

class SharedBMCModel(db.Model):
    __tablename__ = 'shared_bmcs'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    group_id = db.Column(db.String(36), db.ForeignKey('groups.id'), nullable=False)
    name = db.Column(db.String(200), nullable=True)
    data = db.Column(db.JSON, nullable=True)
    updated = db.Column(db.String(50), default=lambda: datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"))

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "data": self.data,
            "updated": self.updated
        }