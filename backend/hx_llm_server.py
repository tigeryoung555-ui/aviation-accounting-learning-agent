#!/usr/bin/env python3
"""
民航会计学习智能体 - 公网 LLM 代理（OpenAI 兼容，零依赖，可直接部署到 Render/Railway/HuggingFace）
用法（本地）：python hx_llm_server.py
前端调用：<API_BASE>/api/config  <API_BASE>/api/chat

配置优先级：环境变量 > server_config.json > 默认值
  环境变量：
    LLM_API_BASE    默认 https://api.deepseek.com/v1
    LLM_MODEL       默认 deepseek-chat
    LLM_API_KEY     （必填，也可叫 DEEPSEEK_API_KEY）
    LLM_TEMPERATURE 默认 0.7
    ALLOWED_ORIGIN  允许跨域的前端域名，默认 https://tigeryoung555-ui.github.io
    PORT            监听端口，默认 8000（云平台自动注入）
"""
import json, os, re, urllib.request, urllib.error, http.server, socketserver

PORT = int(os.environ.get("PORT", "8000"))
ROOT = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(ROOT, "server_config.json")

PAGES_ORIGIN = os.environ.get("ALLOWED_ORIGIN", "https://tigeryoung555-ui.github.io").strip()
ALLOWED_ORIGINS = {PAGES_ORIGIN, "http://localhost:8000", "null", ""}

# 加载题库与知识库
KB = []


def load_data():
    global KB
    try:
        with open(os.path.join(ROOT, "kb_extra.json"), "r", encoding="utf-8") as f:
            extra = json.load(f)
    except Exception:
        extra = []
    for item in extra:
        KB.append({
            "id": item.get("id", ""),
            "chapter": item.get("chapter", ""),
            "title": item.get("title", ""),
            "keywords": (item.get("keywords") or "").split(),
            "content": item.get("content", ""),
        })
    try:
        with open(os.path.join(ROOT, "questions.json"), "r", encoding="utf-8") as f:
            questions = json.load(f)
    except Exception:
        questions = []
    for q in questions:
        if not q.get("explain"):
            continue
        KB.append({
            "id": q.get("id", ""),
            "chapter": q.get("ch", ""),
            "title": "题库解析：" + q.get("q", "")[:40],
            "keywords": (q.get("q", "") + " " + (q.get("explain") or "")).split()[:20],
            "content": "【题目】" + q.get("q", "") + "\n【解析】" + q.get("explain", ""),
        })


def load_config():
    try:
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            cfg = json.load(f)
    except Exception:
        cfg = {}
    env = {
        "api_base": os.environ.get("LLM_API_BASE"),
        "model": os.environ.get("LLM_MODEL"),
        "api_key": os.environ.get("LLM_API_KEY") or os.environ.get("DEEPSEEK_API_KEY"),
        "temperature": os.environ.get("LLM_TEMPERATURE"),
    }
    for k, v in env.items():
        if v is not None:
            cfg[k] = v
    cfg.setdefault("api_base", "https://api.deepseek.com/v1")
    cfg.setdefault("model", "deepseek-chat")
    cfg.setdefault("temperature", 0.7)
    return cfg


def expand_query(query):
    synonyms = {
        "折旧": ["折旧", "折旧方法", "depreciation", "损耗", "年限平均", "直线法", "飞行小时法"],
        "租赁": ["租赁", "融资租赁", "经营租赁", "使用权资产", "租赁负债", "租金"],
        "航油": ["航油", "燃油", "油料", "航空煤油", "燃油成本", "油料成本"],
        "收入": ["收入", "确认收入", "营业收入", "运输收入", "客运收入", "货运收入"],
        "BSP": ["BSP", "开账与结算计划", "票款结算", "代理人结算", "票证结算"],
        "C检": ["C检", "定期检查", "维修", "大修", "资本化", "费用化"],
        "常旅客": ["常旅客", "里程", "奖励里程", "递延收益", "合同负债", "积分"],
        "飞机": ["飞机", "航空器", "机队", "机型", "航空固定资产"],
        "成本": ["成本", "运输成本", "航线成本", "营运成本", "营业成本"],
    }
    words = [w for w in re.split(r"[\s，。？、！；：.?!;:]+", query) if len(w) >= 2]
    expanded = set(words)
    for w in words:
        for k, v in synonyms.items():
            if k in w or w in k:
                expanded.update(v)
    return list(expanded)


def retrieve_context(query, top_n=3):
    qlower = query.lower()
    qwords = expand_query(query)
    scored = []
    for item in KB:
        score = 0
        text = (item.get("chapter", "") + " " + item.get("title", "") + " " + item.get("content", "") + " ").lower()
        for kw in item.get("keywords", []):
            if qlower in kw.lower() or kw.lower() in qlower:
                score += 3
        for w in qwords:
            w = w.lower()
            if item.get("title", "").lower().find(w) >= 0:
                score += 4
            if text.find(w) >= 0:
                score += 2
        if score > 0:
            scored.append((score, item))
    scored.sort(key=lambda x: x[0], reverse=True)
    return [item for _, item in scored[:top_n]]


def build_prompt(query, ctx_items):
    system = (
        "你是一位民航运输企业会计教学专家，熟悉《民用航空运输企业会计》课程。"
        "请基于下面提供的教材知识库和题库解析，用中文简洁、专业地回答学生问题。"
        "回答前先给出核心结论，再分点说明要点，必要时举例。若知识库未覆盖，请明确告知并给出学习建议。\n\n"
        "【参考知识库】\n"
    )
    for i, item in enumerate(ctx_items, 1):
        system += f"{i}. {item.get('chapter','')} · {item.get('title','')}\n{item.get('content','')}\n\n"
    return [
        {"role": "system", "content": system},
        {"role": "user", "content": query},
    ]


def call_llm(cfg, messages):
    api_base = (cfg.get("api_base") or "").rstrip("/")
    model = cfg.get("model", "deepseek-chat")
    api_key = cfg.get("api_key", "")
    temperature = float(cfg.get("temperature", 0.7))
    if not api_base or not api_key:
        raise RuntimeError("LLM 未配置")
    url = api_base + "/chat/completions"
    payload = {
        "model": model,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": 1024,
    }
    data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data,
        headers={
            "Content-Type": "application/json",
            "Authorization": "Bearer " + api_key,
        },
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=40) as resp:
        result = json.loads(resp.read().decode("utf-8"))
    return result["choices"][0]["message"]["content"].strip()


def cors_origin(handler):
    o = handler.headers.get("Origin")
    if o in ALLOWED_ORIGINS:
        return o if o else PAGES_ORIGIN
    return PAGES_ORIGIN


class Handler(http.server.BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        print(fmt % args)

    def send_json(self, code, body):
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Access-Control-Allow-Origin", cors_origin(self))
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()
        self.wfile.write(json.dumps(body, ensure_ascii=False).encode("utf-8"))

    def do_OPTIONS(self):
        self.send_json(200, {})

    def do_GET(self):
        if self.path == "/" or self.path == "/health":
            self.send_json(200, {"status": "ok"})
            return
        if self.path == "/api/config":
            cfg = load_config()
            configured = bool(cfg.get("api_base") and cfg.get("api_key"))
            self.send_json(200, {"configured": configured, "model": cfg.get("model", "")})
            return
        self.send_json(404, {"error": "not found"})

    def do_POST(self):
        if self.path == "/api/chat":
            try:
                length = int(self.headers.get("Content-Length", 0))
                body = self.rfile.read(length).decode("utf-8")
                data = json.loads(body)
                query = (data.get("message") or "").strip()
                if not query:
                    self.send_json(400, {"error": "message is empty"})
                    return
                cfg = load_config()
                if not (cfg.get("api_base") and cfg.get("api_key")):
                    self.send_json(200, {"answer": "LLM 代理尚未配置 API Key，已启用本地 RAG 模式。请在服务端配置 LLM_API_KEY 后重启。", "sources": ["本地代理"]})
                    return
                ctx = retrieve_context(query)
                messages = build_prompt(query, ctx)
                answer = call_llm(cfg, messages)
                sources = [f"{item.get('chapter','')}·{item.get('title','')}" for item in ctx]
                if not sources:
                    sources = ["LLM生成"]
                self.send_json(200, {"answer": answer, "sources": sources})
            except urllib.error.HTTPError as e:
                err = e.read().decode("utf-8", errors="ignore")
                self.send_json(502, {"error": "LLM API 错误", "detail": err})
            except Exception as e:
                self.send_json(500, {"error": str(e)})
            return
        self.send_json(404, {"error": "not found"})


if __name__ == "__main__":
    load_data()
    cfg = load_config()
    print(f"[hx_llm_server] 加载知识库 {len(KB)} 条")
    print(f"[hx_llm_server] LLM 配置状态: {'已配置' if cfg.get('api_key') else '未配置'}")
    print(f"[hx_llm_server] 允许前端域名: {PAGES_ORIGIN}")
    print(f"[hx_llm_server] 服务启动: http://0.0.0.0:{PORT}")
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        httpd.serve_forever()
