#!/usr/bin/env python3
"""凌镜摄影社团 - 后端 API 服务

纯 Python 标准库实现（http.server + sqlite3），零第三方依赖。
启动: python3 app.py   （默认 0.0.0.0:8000，可用 PORT 环境变量覆盖）

默认管理员: 用户名 admin / 密码 admin123 （首次启动后请尽快修改）

接口:
  [公共]
  GET  /api/health
  GET  /api/photos            作品列表 (静态 + 审核通过的投稿)
  GET  /api/members
  GET  /api/departments
  GET  /api/diary             日记 (静态 + 审核通过的投稿)
  GET  /api/history
  GET  /api/resources         资源库 (静态 + 审核通过的投稿)
  GET  /api/studio/equipment
  GET  /api/site/:slug        站点固定内容(首页/关于/历史/部门/工作室)，slug in {home,about,history,departments,studio}
  POST /api/auth/register
  POST /api/auth/login
  GET  /api/auth/me           需登录

  [需登录]
  POST /api/submissions                  提交投稿
  GET  /api/submissions/mine             我提交的
  GET  /api/submissions/:id              详情 (本人或admin)

  [需管理员]
  GET    /api/admin/stats                仪表盘统计
  GET    /api/admin/submissions          投稿列表 (支持 board/status 过滤)
  GET    /api/admin/users                用户列表
  POST   /api/admin/submissions/:id/review   {status:'approved'|'rejected', note?}
  DELETE /api/admin/submissions/:id      删除投稿
  POST   /api/admin/users/:id/role       {role:'admin'|'member'}
  DELETE /api/admin/users/:id            删除成员账号(同时级联删除其全部投稿；禁止删除自己)
  PUT    /api/site/:slug                 更新站点固定内容 body: { content: {...} } (slug 同上)
"""
import base64
import binascii
import json
import os
import re
import sys
import time
import uuid
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse, parse_qs

import auth
import db
import data

HOST = os.environ.get("HOST", "0.0.0.0")
PORT = int(os.environ.get("PORT", "8000"))

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)
ALLOWED_EXT = {"jpeg", "jpg", "png", "gif", "webp"}
# 文档类（完整历史讲述等）：Word / PDF
ALLOWED_DOC_EXT = {"doc", "docx", "pdf"}
# 10MB 单图限制
MAX_IMG_BYTES = 10 * 1024 * 1024
# 20MB 单文档限制
MAX_DOC_BYTES = 20 * 1024 * 1024

USERNAME_RE = re.compile(r"^[A-Za-z0-9_\u4e00-\u9fa5]{2,20}$")
EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def _user_public(u):
    if hasattr(u, "keys"):
        u = dict(u)
    return {
        "id": u["id"],
        "username": u["username"],
        "email": u["email"],
        "nickname": u.get("nickname", ""),
        "avatar": u.get("avatar", ""),
        "birthday": u.get("birthday", ""),
        "bio": u.get("bio", ""),
        "role": u.get("role", "member"),
        "created_at": u["created_at"],
    }


def _merge_photos():
    static = [{**p, "uuid": str(p.get("id"))} for p in data.PHOTOS]
    hidden = db.get_hidden_static_ids("photo")
    static = [p for p in static if p.get("id") not in hidden]
    # 审核通过的投稿转成前端需要的格式，按时间新→旧排在前面
    for s in db.list_approved_board("photo"):
        p = s["payload"] or {}
        if not isinstance(p, dict):
            continue
        static.insert(
            0,
            {
                "id": s["id"] + 10000,
                "submission_id": s["id"],
                "uuid": s.get("uuid") or str(s["id"] + 10000),
                "title": p.get("title", "未命名"),
                "author": p.get("author") or s.get("submitter_name") or s.get("submitter_uname") or "社员",
                "likes": int(p.get("likes") or 0),
                "cat": p.get("cat", "投稿"),
                "grad": p.get("grad", "linear-gradient(135deg, #2D5F8A, #4A90D9, #6AADE8)"),
                "image": p.get("image") or None,
                "desc": p.get("desc") or "",
                "from_submission": True,
                "approved_at": s.get("reviewed_at"),
            },
        )
    return static


def _merge_resources():
    static = [{**r, "uuid": str(r.get("id"))} for r in data.RESOURCES]
    hidden = db.get_hidden_static_ids("resource")
    static = [r for r in static if r.get("id") not in hidden]
    for s in db.list_approved_board("resource"):
        p = s["payload"] or {}
        if not isinstance(p, dict):
            continue
        static.insert(
            0,
            {
                "id": s["id"] + 10000,
                "submission_id": s["id"],
                "uuid": s.get("uuid") or str(s["id"] + 10000),
                "title": p.get("title", "未命名干货"),
                "cat": p.get("cat", "投稿"),
                "summary": p.get("summary", p.get("full_desc", "")[:60]),
                "fullDesc": p.get("fullDesc") or p.get("full_desc") or "",
                "views": int(p.get("views") or 0),
                "downloads": int(p.get("downloads") or 0),
                "author": p.get("author") or s.get("submitter_name") or s.get("submitter_uname") or "社员",
                "color": p.get("color", "#2D5F8A"),
                "coverGrad": p.get("coverGrad") or p.get("cover_grad") or "linear-gradient(135deg, #667EEA, #764BA2)",
                "from_submission": True,
            },
        )
    return static


def _merge_diary():
    static = [{**d, "uuid": str(d.get("id"))} for d in data.DIARY_ENTRIES]
    hidden = db.get_hidden_static_ids("diary")
    static = [d for d in static if d.get("id") not in hidden]
    for s in db.list_approved_board("diary"):
        p = s["payload"] or {}
        if not isinstance(p, dict):
            continue
        static.insert(
            0,
            {
                "id": s["id"] + 10000,
                "submission_id": s["id"],
                "uuid": s.get("uuid") or str(s["id"] + 10000),
                "date": p.get("date", ""),
                "title": p.get("title", "无标题"),
                "content": p.get("content", ""),
                "mood": p.get("mood", "happy"),
                "author": p.get("author") or s.get("submitter_name") or s.get("submitter_uname") or "社员",
                "from_submission": True,
            },
        )
    return static


class Handler(BaseHTTPRequestHandler):
    server_version = "LingKing/0.2"

    # ---- 基础工具 ----

    def _send_json(self, code, obj):
        body = json.dumps(obj, ensure_ascii=False).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS")
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

    def _require_admin(self):
        user = self._require_auth()
        if user is None:
            return None
        if user["role"] != "admin":
            self._send_json(403, {"error": "需要管理员权限"})
            return None
        return user

    # ---- HTTP 方法分发 ----

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
        self.end_headers()

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path.rstrip("/")
        query = parse_qs(parsed.query)

        # --- 公共 ---
        if path == "/api/health":
            self._send_json(200, {"ok": True, "service": "lingking-backend"})
            return
        if path == "/api/auth/me":
            user = self._require_auth()
            if user is not None:
                self._send_json(200, {"user": _user_public(user)})
            return
        if path == "/api/photos":
            cat = query.get("cat", [None])[0]
            photos = _merge_photos()
            if cat:
                photos = [p for p in photos if p.get("cat") == cat]
            self._send_json(200, {"photos": photos})
            return
        if path == "/api/members":
            # 成员展示与网站账号信息同步：返回真实注册用户
            users = db.list_users(limit=10000)
            members = [
                {
                    "id": u["id"],
                    "name": u["nickname"] or u["username"],
                    "username": u["username"],
                    "nickname": u["nickname"] or "",
                    "avatar": u["avatar"] or "",
                    "bio": u["bio"] or "",
                    "role": u["role"],
                }
                for u in users
            ]
            self._send_json(200, {"members": members})
            return
        if path == "/api/departments":
            self._send_json(200, {"departments": data.DEPARTMENTS})
            return
        if path == "/api/diary":
            self._send_json(200, {"entries": _merge_diary()})
            return
        if path == "/api/history":
            self._send_json(200, {"events": data.HISTORY_EVENTS})
            return
        if path == "/api/resources":
            self._send_json(200, {"resources": _merge_resources()})
            return
        if path == "/api/studio/equipment":
            self._send_json(200, {"equipment": data.STUDIO_EQUIPMENT})
            return

        # 站点固定内容（公共读）
        m = re.match(r"^/api/site/([a-z_]+)$", path)
        if m:
            slug = m.group(1)
            if slug not in db.VALID_SITE_SLUGS:
                self._send_json(400, {"error": f"slug 必须为 {sorted(db.VALID_SITE_SLUGS)} 之一"})
                return
            saved = db.get_site_content(slug)
            self._send_json(
                200,
                {
                    "slug": slug,
                    "content": saved["content"] if saved else None,
                    "updated_at": saved["updated_at"] if saved else None,
                    "updated_by": saved["updated_by"] if saved else None,
                    "saved": bool(saved),
                },
            )
            return

        # --- 登录用户 ---
        if path == "/api/submissions/mine":
            user = self._require_auth()
            if user is None:
                return
            items = db.list_submissions(submitter_id=user["id"])
            self._send_json(200, {"submissions": items})
            return

        # 管理员路由前缀
        if path.startswith("/api/admin/"):
            admin = self._require_admin()
            if admin is None:
                return
            if path == "/api/admin/stats":
                self._send_json(
                    200,
                    {
                        "total_users": db.count_submissions(),  # alias 保持兼容
                        "users_count": len(db.list_users(limit=10000)),
                        "submissions_count": db.count_submissions(),
                        "pending_count": db.count_submissions(status="pending"),
                        "approved_count": db.count_submissions(status="approved"),
                        "rejected_count": db.count_submissions(status="rejected"),
                        "by_board": {
                            "photo": db.count_submissions(board="photo"),
                            "resource": db.count_submissions(board="resource"),
                            "diary": db.count_submissions(board="diary"),
                        },
                    },
                )
                return
            if path == "/api/admin/submissions":
                board = query.get("board", [None])[0]
                status = query.get("status", [None])[0]
                items = db.list_submissions(board=board, status=status)
                self._send_json(200, {"submissions": items})
                return
            if path == "/api/admin/users":
                self._send_json(200, {"users": db.list_users(limit=1000)})
                return
            if path == "/api/admin/content":
                ctype = query.get("type", [None])[0]
                if ctype == "photo":
                    self._send_json(200, {"items": _merge_photos()})
                elif ctype == "resource":
                    self._send_json(200, {"items": _merge_resources()})
                elif ctype == "diary":
                    self._send_json(200, {"items": _merge_diary()})
                else:
                    self._send_json(400, {"error": "type 必须为 photo / resource / diary"})
                return
            # 带 id 的: /api/admin/submissions/<id> 在 DELETE 里处理
            self._send_json(404, {"error": "Not Found"})
            return

        # /api/submissions/<id> 详情 (本人或admin)
        m = re.match(r"^/api/submissions/(\d+)$", path)
        if m:
            sid = int(m.group(1))
            user = self._require_auth()
            if user is None:
                return
            s = db.get_submission(sid)
            if not s:
                self._send_json(404, {"error": "投稿不存在"})
                return
            if s["submitter_id"] != user["id"] and user["role"] != "admin":
                self._send_json(403, {"error": "无权查看"})
                return
            self._send_json(200, {"submission": s})
            return

        # /api/posts/<uuid> 单篇内容详情（供前端与SEO爬虫按 uuid 访问）
        m = re.match(r"^/api/posts/([A-Za-z0-9_\-]+)$", path)
        if m:
            item_uuid = m.group(1)
            # 1. 查找数据库投稿
            s = db.get_submission_by_uuid(item_uuid)
            if s:
                if s["status"] != "approved":
                    user = self._require_auth()
                    if not user or (s["submitter_id"] != user["id"] and user["role"] != "admin"):
                        self._send_json(403, {"error": "该帖子暂未公开或处于审核中"})
                        return
                self._send_json(200, {"ok": True, "post": s, "board": s["board"]})
                return

            # 2. 查找静态预设作品/日记/资源
            p_match = next((p for p in _merge_photos() if str(p.get("uuid")) == item_uuid or str(p.get("id")) == item_uuid), None)
            if p_match:
                self._send_json(200, {"ok": True, "post": p_match, "board": "photo"})
                return
            d_match = next((d for d in _merge_diary() if str(d.get("uuid")) == item_uuid or str(d.get("id")) == item_uuid), None)
            if d_match:
                self._send_json(200, {"ok": True, "post": d_match, "board": "diary"})
                return
            r_match = next((r for r in _merge_resources() if str(r.get("uuid")) == item_uuid or str(r.get("id")) == item_uuid), None)
            if r_match:
                self._send_json(200, {"ok": True, "post": r_match, "board": "resource"})
                return

            self._send_json(404, {"error": "未找到对应内容"})
            return

        self._send_json(404, {"error": "Not Found"})

    def do_POST(self):
        parsed = urlparse(self.path)
        path = parsed.path.rstrip("/")
        body = self._read_json()
        if body is None:
            return self._send_json(400, {"error": "请求体不是合法 JSON"})

        # 公共
        if path == "/api/auth/register":
            return self._handle_register(body)
        if path == "/api/auth/login":
            return self._handle_login(body)

        # 需登录
        if path == "/api/upload":
            user = self._require_auth()
            if user is None:
                return
            return self._handle_upload(user, body)
        if path == "/api/submissions":
            user = self._require_auth()
            if user is None:
                return
            return self._handle_create_submission(user, body)

        if path == "/api/auth/profile":
            user = self._require_auth()
            if user is None:
                return
            return self._handle_update_profile(user, body)

        if path == "/api/auth/password":
            user = self._require_auth()
            if user is None:
                return
            return self._handle_change_password(user, body)

        # 管理员
        if path.startswith("/api/admin/"):
            admin = self._require_admin()
            if admin is None:
                return
            m = re.match(r"^/api/admin/submissions/(\d+)/review$", path)
            if m:
                return self._handle_review(admin, int(m.group(1)), body)
            m = re.match(r"^/api/admin/users/(\d+)/role$", path)
            if m:
                uid = int(m.group(1))
                role = str(body.get("role") or "member")
                db.set_user_role(uid, role)
                return self._send_json(200, {"ok": True, "role": "admin" if role == "admin" else "member"})
            return self._send_json(404, {"error": "Not Found"})

        self._send_json(404, {"error": "Not Found"})

    def do_DELETE(self):
        parsed = urlparse(self.path)
        path = parsed.path.rstrip("/")
        query = parse_qs(parsed.query)

        # DELETE /api/admin/content?type=photo&id=1
        if path == "/api/admin/content":
            admin = self._require_admin()
            if admin is None:
                return
            ctype = query.get("type", [None])[0]
            item_id = query.get("id", [None])[0]
            if not ctype or not item_id:
                return self._send_json(400, {"error": "缺少 type 或 id 参数"})
            try:
                item_id_int = int(item_id)
            except ValueError:
                return self._send_json(400, {"error": "id 必须为数字"})

            if ctype in ("photo", "resource", "diary"):
                board_map = {"photo": "photo", "resource": "resource", "diary": "diary"}
                board = board_map[ctype]
                if item_id_int >= 10000:
                    # 投稿内容 → 删除投稿记录
                    sid = item_id_int - 10000
                    if not db.get_submission(sid):
                        return self._send_json(404, {"error": "投稿不存在"})
                    db.delete_submission(sid)
                    return self._send_json(200, {"ok": True, "deleted_submission": sid})
                else:
                    # 静态内容 → 加入隐藏表
                    db.hide_static(board, item_id_int)
                    return self._send_json(200, {"ok": True, "hidden_static": item_id_int, "board": board})
            else:
                return self._send_json(400, {"error": "type 必须为 photo / resource / diary"})

        # DELETE /api/admin/submissions/<id>
        m = re.match(r"^/api/admin/submissions/(\d+)$", path)
        if m:
            admin = self._require_admin()
            if admin is None:
                return
            sid = int(m.group(1))
            if not db.get_submission(sid):
                return self._send_json(404, {"error": "投稿不存在"})
            db.delete_submission(sid)
            return self._send_json(200, {"ok": True, "deleted": sid})

        # DELETE /api/admin/users/<id>  删除成员（禁止删除自己）
        m = re.match(r"^/api/admin/users/(\d+)$", path)
        if m:
            admin = self._require_admin()
            if admin is None:
                return
            uid = int(m.group(1))
            if not db.find_by_id(uid):
                return self._send_json(404, {"error": "用户不存在"})
            try:
                ok = db.delete_user(uid, operator_id=admin["id"])
            except PermissionError as e:
                return self._send_json(400, {"error": str(e)})
            return self._send_json(200, {"ok": True, "deleted_user": uid if ok else False})

        self._send_json(404, {"error": "Not Found"})

    def do_PUT(self):
        parsed = urlparse(self.path)
        path = parsed.path.rstrip("/")
        body = self._read_json()
        if body is None and int(self.headers.get("Content-Length", 0) or 0) > 0:
            return self._send_json(400, {"error": "请求体不是合法 JSON"})
        body = body or {}

        # PUT /api/site/<slug>  管理员：更新站点固定内容
        m = re.match(r"^/api/site/([a-z_]+)$", path)
        if m:
            admin = self._require_admin()
            if admin is None:
                return
            slug = m.group(1)
            if slug not in db.VALID_SITE_SLUGS:
                return self._send_json(400, {"error": f"slug 必须为 {sorted(db.VALID_SITE_SLUGS)} 之一"})
            content = body.get("content")
            if content is None:
                return self._send_json(400, {"error": "缺少 content 字段（必须传 dict / list）"})
            if not isinstance(content, dict):
                return self._send_json(400, {"error": "content 必须是对象 {}"})
            saved = db.set_site_content(slug, content, updated_by=admin["id"])
            return self._send_json(200, {"ok": True, "data": saved})

        self._send_json(404, {"error": "Not Found"})

    # ---- 业务处理 ----

    def _handle_register(self, payload):
        username = str(payload.get("username", "")).strip()
        email = str(payload.get("email", "")).strip().lower()
        password = str(payload.get("password", ""))
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

    def _handle_login(self, payload):
        identifier = str(payload.get("identifier", "")).strip()
        password = str(payload.get("password", ""))
        if not identifier or not password:
            return self._send_json(400, {"error": "请输入用户名/邮箱和密码"})
        user = db.find_by_identifier(identifier)
        if not user or not auth.verify_password(password, user["password_hash"]):
            return self._send_json(401, {"error": "用户名/邮箱或密码错误"})
        token = auth.make_token(user["id"])
        self._send_json(200, {"token": token, "user": _user_public(user)})

    # ---------- 投稿 ---------- #

    def _validate_photo_payload(self, p):
        errs = []
        if not str(p.get("title", "")).strip():
            errs.append("作品名不能为空")
        return errs

    def _validate_resource_payload(self, p):
        errs = []
        if not str(p.get("title", "")).strip():
            errs.append("标题不能为空")
        if not str(p.get("summary", "")).strip() and not str(p.get("full_desc", "")).strip() and not str(p.get("fullDesc", "")).strip():
            errs.append("请填写内容简介或正文")
        return errs

    def _validate_diary_payload(self, p):
        errs = []
        if not str(p.get("title", "")).strip():
            errs.append("日记标题不能为空")
        if not str(p.get("content", "")).strip():
            errs.append("日记内容不能为空")
        return errs

    def _handle_create_submission(self, user, payload):
        board = str(payload.get("board", "")).strip()
        p = payload.get("payload") or {}
        if not isinstance(p, dict):
            return self._send_json(400, {"error": "payload 必须是对象"})
        if board == "photo":
            errs = self._validate_photo_payload(p)
        elif board == "resource":
            errs = self._validate_resource_payload(p)
        elif board == "diary":
            errs = self._validate_diary_payload(p)
        else:
            return self._send_json(400, {"error": "不支持的板块: photo / resource / diary"})
        if errs:
            return self._send_json(400, {"error": errs[0]})

        # normalize: 作者署名优先 payload.author，否则用用户昵称 / 用户名
        author_name = str(p.get("author", "")).strip()
        if not author_name:
            author_name = user["nickname"] or user["username"]
        if isinstance(p, dict) and "author" not in p:
            p["author"] = author_name
        else:
            p["author"] = author_name

        try:
            sid, item_uuid = db.create_submission(
                board=board,
                payload=p,
                submitter_id=user["id"],
                submitter_name=user["nickname"] or user["username"],
            )
        except ValueError as e:
            return self._send_json(400, {"error": str(e)})
        self._send_json(201, {"ok": True, "id": sid, "uuid": item_uuid, "status": "pending"})

    def _handle_review(self, admin, sid, payload):
        s = db.get_submission(sid)
        if not s:
            return self._send_json(404, {"error": "投稿不存在"})
        new_status = str(payload.get("status", "")).strip()
        note = str(payload.get("note") or "").strip() or None
        if new_status not in ("approved", "rejected"):
            return self._send_json(400, {"error": "status 必须为 approved 或 rejected"})
        db.review_submission(sid, new_status, admin["id"], note)
        self._send_json(200, {"ok": True, "id": sid, "status": new_status})

    def _handle_update_profile(self, user, payload):
        username = payload.get("username")
        nickname = payload.get("nickname")
        avatar = payload.get("avatar")
        birthday = payload.get("birthday")
        bio = payload.get("bio")

        if username is not None:
            username = str(username).strip()
            if not USERNAME_RE.match(username):
                return self._send_json(400, {"error": "用户名需为 2-20 位字母/数字/下划线/中文"})
            existing = db.find_by_identifier(username)
            if existing and existing["id"] != user["id"]:
                return self._send_json(409, {"error": "用户名已被占用"})

        if nickname is not None:
            nickname = str(nickname).strip()[:50]
        if avatar is not None:
            avatar = str(avatar).strip()[:500]
        if birthday is not None:
            birthday = str(birthday).strip()[:20]
            # YYYY-MM-DD 格式校验（允许空）
            import re as _re
            if birthday and not _re.match(r"^\d{4}-\d{2}-\d{2}$", birthday):
                return self._send_json(400, {"error": "生日格式应为 YYYY-MM-DD"})
        if bio is not None:
            bio = str(bio).strip()[:1000]

        db.update_user_profile(user["id"], username=username, nickname=nickname, avatar=avatar, birthday=birthday, bio=bio)
        updated = db.find_by_id(user["id"])
        self._send_json(200, {"ok": True, "user": _user_public(updated)})

    def _handle_change_password(self, user, payload):
        old_password = str(payload.get("old_password", ""))
        new_password = str(payload.get("new_password", ""))
        if not old_password or not new_password:
            return self._send_json(400, {"error": "请填写旧密码和新密码"})
        if len(new_password) < 6:
            return self._send_json(400, {"error": "新密码至少 6 位"})
        if not auth.verify_password(old_password, user["password_hash"]):
            return self._send_json(401, {"error": "旧密码不正确"})
        db.update_user_password(user["id"], auth.hash_password(new_password))
        self._send_json(200, {"ok": True})

    # --- 文件上传（图片 + 文档） ---
    def _handle_upload(self, user, payload):
        """POST /api/upload  {image_b64: 'data:...;base64,XXXX' 或纯 base64, ext?: 'jpg'|'docx'|'pdf'...}"""
        image_b64 = payload.get("image_b64") or payload.get("image") or payload.get("data")
        if not image_b64 or not isinstance(image_b64, str):
            return self._send_json(400, {"error": "缺少 image_b64 字段"})

        ext = (payload.get("ext") or "").lower().replace(".", "")
        pure_b64 = image_b64
        # data:<mime>;base64,xxxxxx 格式解析
        if image_b64.startswith("data:") and ";base64," in image_b64:
            head, pure_b64 = image_b64.split(";base64,", 1)
            mime = head.split(":", 1)[1]
            if not ext:
                ext = mime.split("/")[1].split(";")[0].lower()
                if ext == "jpeg":
                    ext = "jpg"

        ext = ext.lower() if ext else "jpg"
        if ext in ALLOWED_DOC_EXT:
            max_bytes = MAX_DOC_BYTES
        elif ext in ALLOWED_EXT:
            max_bytes = MAX_IMG_BYTES
        else:
            return self._send_json(400, {"error": f"不支持的格式: {ext}，仅允许 jpg/jpeg/png/gif/webp 图片及 doc/docx/pdf 文档"})

        try:
            raw = base64.b64decode(pure_b64.split(",")[-1], validate=True)
        except (binascii.Error, ValueError):
            return self._send_json(400, {"error": "文件 base64 解码失败，请检查上传数据"})

        if len(raw) > max_bytes:
            return self._send_json(400, {"error": f"文件过大，限制 {max_bytes//1024//1024}MB 以内"})
        if len(raw) < 32:
            return self._send_json(400, {"error": "文件内容过小或损坏"})

        now = int(time.time())
        sub_dir = time.strftime("%Y/%m", time.localtime(now))
        save_dir = os.path.join(UPLOAD_DIR, sub_dir)
        os.makedirs(save_dir, exist_ok=True)
        fname = f"{uuid.uuid4().hex}.{ext}"
        fpath = os.path.join(save_dir, fname)
        with open(fpath, "wb") as f:
            f.write(raw)

        public_url = f"/uploads/{sub_dir}/{fname}"
        return self._send_json(200, {
            "ok": True,
            "url": public_url,
            "size": len(raw),
            "ext": ext,
        })

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
