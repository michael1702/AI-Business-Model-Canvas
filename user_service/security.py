
# services_common/security.py
import os, time, logging, jwt, hashlib

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
    now = int(time.time())
    payload = {"sub": user_id, "email": email, "iat": now, "exp": now + JWT_EXP_S}
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALG)

def decode_token(token: str) -> dict | None:
    try:
        # leeway helps if clocks skew a little
        return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALG], leeway=10)
    except jwt.ExpiredSignatureError:
        log.warning("JWT expired")
    except jwt.InvalidSignatureError:
        log.warning("JWT invalid signature (check JWT_SECRET)")
    except jwt.DecodeError:
        log.warning("JWT decode error")
    except Exception as ex:
        log.warning("JWT error: %s", ex)
    return None

def log_jwt_config(service_name: str):
    sha = hashlib.sha256(JWT_SECRET.encode("utf-8")).hexdigest()[:12]
    log.info("[JWT/%s] alg=%s exp_s=%s secret_sha256_12=%s",
             service_name, JWT_ALG, JWT_EXP_S, sha)