# user_service/domain.py
from .adapters.repository import UserRepo, User
from .security import hash_password, verify_password

def register_user(email: str, password: str, repo: UserRepo) -> User:
    if not email or "@" not in email:
        raise ValueError("invalid_email")
    if not password or len(password) < 6:
        raise ValueError("weak_password")
    return repo.create_user(email=email, password_hash=hash_password(password))

def authenticate_user(email: str, password: str, repo: UserRepo) -> User:
    u = repo.get_by_email(email)
    if not u or not verify_password(password or "", u.password_hash):
        raise ValueError("invalid_credentials")
    return u
