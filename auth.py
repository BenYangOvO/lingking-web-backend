"""密码哈希 + HMAC 签名 token（纯标准库，零依赖）"""
import base64
import hashlib
import hmac
import json
import os
import secrets
import time

SECRET_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", ".secret")
TOKEN_TTL = 7 * 24 * 3600  # token 有效期 7 天


def _load_secret() -> str:
    """优先读环境变量，否则落盘持久化一个随机密钥"""
    env = os.environ.get("LINGKING_TOKEN_SECRET")
    if env:
        return env
    os.makedirs(os.path.dirname(SECRET_FILE), exist_ok=True)
    if os.path.exists(SECRET_FILE):
        return open(SECRET_FILE).read().strip()
    secret = secrets.token_hex(32)
    with open(SECRET_FILE, "w") as f:
        f.write(secret)
    os.chmod(SECRET_FILE, 0o600)
    return secret


TOKEN_SECRET = _load_secret()
PBKDF2_ITERATIONS = 200_000


def hash_password(password: str) -> str:
    """格式: pbkdf2_sha256$迭代次数$盐$摘要"""
    salt = secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac(
        "sha256", password.encode(), salt.encode(), PBKDF2_ITERATIONS
    ).hex()
    return f"pbkdf2_sha256${PBKDF2_ITERATIONS}${salt}${digest}"


def verify_password(password: str, stored: str) -> bool:
    try:
        algo, iters, salt, digest = stored.split("$")
        if algo != "pbkdf2_sha256":
            return False
        calc = hashlib.pbkdf2_hmac(
            "sha256", password.encode(), salt.encode(), int(iters)
        ).hex()
        return hmac.compare_digest(calc, digest)
    except Exception:
        return False


def _b64e(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).decode().rstrip("=")


def _b64d(data: str) -> bytes:
    return base64.urlsafe_b64decode(data + "=" * (-len(data) % 4))


def make_token(uid: int) -> str:
    """签发 token：payload(uid, exp).signature"""
    payload = _b64e(
        json.dumps({"uid": uid, "exp": int(time.time()) + TOKEN_TTL}).encode()
    )
    sig = hmac.new(TOKEN_SECRET.encode(), payload.encode(), hashlib.sha256).hexdigest()
    return f"{payload}.{sig}"


def verify_token(token: str):
    """校验 token，返回 uid 或 None"""
    try:
        payload, sig = token.split(".")
        expected = hmac.new(
            TOKEN_SECRET.encode(), payload.encode(), hashlib.sha256
        ).hexdigest()
        if not hmac.compare_digest(sig, expected):
            return None
        data = json.loads(_b64d(payload))
        if data["exp"] < time.time():
            return None
        return data["uid"]
    except Exception:
        return None
