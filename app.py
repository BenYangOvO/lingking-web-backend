#!/usr/bin/env python3
"""凌镜摄影社团 - 后端 API 服务

纯 Python 标准库实现（http.server + sqlite3），零第三方依赖。
启动: python3 app.py   （默认 0.0.0.0:8000，可用 PORT 环境变量覆盖）

接口:
  GET  /api/health             健康检查
  POST /api/auth/register     注册 {username, email, password}
  POST /api/auth/login        登录 {identifier, password}  -> {token, user}
  GET  /api/auth/me           当前用户（Authorization: Bearer <token>）
  GET  /api/photos            作品列表（支持 ?cat= 筛选）
  GET  /api/members            成员列表
  GET  /api/departments       部门列表
  GET  /api/diary             日记列表
  GET  /api/history           历史事件
  GET  /api/resources          资源列表
  GET  /api/studio/equipment   工作室设备
"""
import json
import os
import re
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse, parse_qs

import auth
import db
import data

HOST = os.environ.get("HOST", "0.0.0.0")
PORT = int(os.environ.get("PORT", "8000"))

USERNAME_RE = re.compile(r"^[A-Za-z0-9_\u4e00-\u9fa5]{2,20}$")
EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def _user_public(u):
    """对外暴露的用户信息（绝不包含 password_hash）"""
    return {
        "id": u["id"],
        "username": u["username"],
        "email": u["email"],
        "nickname": u["nickname"],
        "avatar": u["avatar"],
        "role": u["role"],
        "created_at": u["created_at"],
    }


class Handler(BaseHTTPRequestHandler):
    server_version = "LingKing/0.1"

    # ---- 基础工具 ----

    def _send_json(self, code, obj):
        body = json.dumps(obj, ensure_ascii=False).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(body)

    def _read_json(self):
        length = int(self.headers.get("Content-Length", 0) or 0)
        if length <= 0:
            return {}
        try:
            return json.loads(self.rfile.read(length).decode("utf-8"))
        except Exception:
            return None

    def _current_uid(self):
        h = self.headers.get("Authorization", "")
        if h.startswith("Bearer "):
            return auth.verify_token(h[7:].strip())
        return None

    def _require_auth(self):
        uid = self._current_uid()
        if not uid:
            self._send_json(401, {"error": "未登录或登录已过期"})
            return None
        user = db.find_by_id(uid)
        if not user:
            self._send_json(401, {"error": "用户不存在"})
            return None
        return user

    # ---- HTTP 方法 ----

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
        self.end_headers()

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path
        query = parse_qs(parsed.query)

        if path == "/api/health":
            self._send_json(200, {"ok": True, "service": "lingking-backend"})
        elif path == "/api/auth/me":
            user = self._require_auth()
            if user is not None:
                self._send_json(200, {"user": _user_public(user)})
        elif path == "/api/photos":
            cat = query.get("cat", [None])[0]
            photos = data.PHOTOS
            if cat:
                photos = [p for p in photos if p["cat"] == cat]
            self._send_json(200, {"photos": photos})
        elif path == "/api/members":
            dept = query.get("dept", [None])[0]
            members = data.MEMBERS
            if dept:
                members = [m for m in members if m["dept"] == dept]
            self._send_json(200, {"members": members})
        elif path == "/api/departments":
            self._send_json(200, {"departments": data.DEPARTMENTS})
        elif path == "/api/diary":
            self._send_json(200, {"entries": data.DIARY_ENTRIES})
        elif path == "/api/history":
            self._send_json(200, {"events": data.HISTORY_EVENTS})
        elif path == "/api/resources":
            self._send_json(200, {"resources": data.RESOURCES})
        elif path == "/api/studio/equipment":
            self._send_json(200, {"equipment": data.STUDIO_EQUIPMENT})
        else:
            self._send_json(404, {"error": "Not Found"})

    def do_POST(self):
        path = urlparse(self.path).path
        body = self._read_json()
        if body is None:
            return self._send_json(400, {"error": "请求体不是合法 JSON"})

        if path == "/api/auth/register":
            self._handle_register(body)
        elif path == "/api/auth/login":
            self._handle_login(body)
        else:
            self._send_json(404, {"error": "Not Found"})

    # ---- 业务逻辑 ----

    def _handle_register(self, data):
        username = str(data.get("username", "")).strip()
        email = str(data.get("email", "")).strip().lower()
        password = str(data.get("password", ""))

        if not USERNAME_RE.match(username):
            return self._send_json(400, {"error": "用户名需为 2-20 位字母/数字/下划线/中文"})
        if not EMAIL_RE.match(email):
            return self._send_json(400, {"error": "邮箱格式不正确"})
        if len(password) < 6:
            return self._send_json(400, {"error": "密码至少 6 位"})
        if db.find_by_identifier(username) or db.find_by_identifier(email):
            return self._send_json(409, {"error": "用户名或邮箱已被占用"})

        uid = db.create_user(username, email, auth.hash_password(password))
        token = auth.make_token(uid)
        user = db.find_by_id(uid)
        self._send_json(201, {"token": token, "user": _user_public(user)})

    def _handle_login(self, data):
        identifier = str(data.get("identifier", "")).strip()
        password = str(data.get("password", ""))

        if not identifier or not password:
            return self._send_json(400, {"error": "请输入用户名/邮箱和密码"})

        user = db.find_by_identifier(identifier)
        if not user or not auth.verify_password(password, user["password_hash"]):
            return self._send_json(401, {"error": "用户名/邮箱或密码错误"})

        token = auth.make_token(user["id"])
        self._send_json(200, {"token": token, "user": _user_public(user)})

    def log_message(self, fmt, *args):
        sys.stderr.write("[%s] %s\n" % (self.log_date_time_string(), fmt % args))


if __name__ == "__main__":
    db.init_db()
    server = ThreadingHTTPServer((HOST, PORT), Handler)
    print(f"凌镜后端已启动: http://{HOST}:{PORT}  (python3 app.py)")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        server.shutdown()