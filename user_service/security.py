
# services_common/security.py
import hashlib
import os
import jwt
import logging
import datetime
from functools import wraps
from flask import request, jsonify, g

from werkzeug.security import generate_password_hash, check_password_hash

log = logging.getLogger(__name__)

JWT_SECRET = os.getenv("JWT_SECRET", "change-me-in-prod")
JWT_ALG    = "HS256"
JWT_EXP_S  = int(os.getenv("JWT_EXP_S", "2592000"))  # 30 days

def hash_password(plain: str) -> str:
    return generate_password_hash(plain, method="pbkdf2:sha256", salt_length=16)

def verify_password(plain: str, hashed: str) -> bool:
    return check_password_hash(hashed, plain)


def create_access_token(user_id: str, email: str) -> str:
    """Erstellt ein JWT Token für den User."""
    payload = {
        "sub": user_id,
        "email": email,
        "iat": datetime.datetime.utcnow(),
        "exp": datetime.datetime.utcnow() + datetime.timedelta(seconds=JWT_EXP_S)
    }
    return jwt.encode(payload, JWT_SECRET, algorithm="HS256")

def decode_token(token: str):
    """Dekodiert und validiert das Token."""
    try:
        return jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
    except jwt.ExpiredSignatureError:
        print("DEBUG: Token expired")
        return None
    except jwt.InvalidTokenError as e:
        print(f"DEBUG: Invalid token error: {e}")
        return None

def log_jwt_config(service_name: str):
    sha = hashlib.sha256(JWT_SECRET.encode("utf-8")).hexdigest()[:12]
    log.info("[JWT/%s] alg=%s exp_s=%s secret_sha256_12=%s",
             service_name, JWT_ALG, JWT_EXP_S, sha)
    

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get("Authorization")
        
        # DEBUG PRINTS
        if not auth_header:
            print("DEBUG: No Authorization header present")
            return jsonify({"error": "missing_token"}), 401
            
        if not auth_header.startswith("Bearer "):
            print(f"DEBUG: Invalid header format: {auth_header}")
            return jsonify({"error": "invalid_header_format"}), 401
        
        token = auth_header.split(" ")[1]
        payload = decode_token(token)
        
        if not payload:
            print("DEBUG: Payload decode failed")
            return jsonify({"error": "token_invalid"}), 401
        
        # User-Daten setzen
        g.user_id = payload.get("sub")
        g.email = payload.get("email")
        
        print(f"DEBUG: Auth success for user {g.email} ({g.user_id})")
        return f(*args, **kwargs)
    return decorated_function