// Cloudflare Worker: minhang-ai-proxy
// RAG AI proxy + user system (D1) + student/teacher role split
// Deploy requirements:
//   - D1 database bound as env.DB
//   - vars: SESSION_SECRET (random string), LLM_API_KEY, optional LLM_MODEL
//   - after deploy, call GET /api/setup once to create tables

const ALLOWED_ORIGIN = "https://tigeryoung555-ui.github.io";
const DEEPSEEK_BASE = "https://api.deepseek.com/v1";
const KB_URL = "https://raw.githubusercontent.com/tigeryoung555-ui/aviation-accounting-learning-agent/main/backend/kb_extra.json";
const QS_URL = "https://raw.githubusercontent.com/tigeryoung555-ui/aviation-accounting-learning-agent/main/backend/questions.json";
const CACHE_TTL_MS = 5 * 60 * 1000;
const TOKEN_TTL_SEC = 60 * 60 * 24 * 7; // 7 days

// In-memory RAG index cache (per isolate)
let ragCache = { kb: null, qs: null, indexes: null, time: 0 };

const SYNONYMS = {
  "飞机": ["航空器", "机型"],
  "租赁": ["融资租赁", "经营租赁", "使用权资产", "租赁负债"],
  "收入": ["确认收入", "营业收入", "主营业务收入"],
  "成本": ["运输成本", "营业成本", "主营业务成本"],
  "折旧": ["累计折旧", "固定资产折旧"],
  "里程": ["常旅客", "奖励里程", "里程兑换"],
  "燃油": ["航油", "油料"],
  "维修": ["修理", "MRO", "维护"]
};

export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    if (request.method === "OPTIONS") return corsPreflight();
    try {
      const p = url.pathname;

      if (p === "/") return txt("minhang-ai-proxy OK", 200);

      if (p === "/api/config") {
        return json({
          available: true,
          model: env.LLM_MODEL || "deepseek-chat",
          backend: "cloudflare-workers",
          auth: !!env.DB
        });
      }

      // one-time schema setup (call manually after deploy)
      if (p === "/api/setup") return await handleSetup(env);

      // auth routes (no role required)
      if (p.startsWith("/api/auth/")) return await handleAuth(p, request, env);

      // protected routes require a valid session token
      if (p.startsWith("/api/teacher/")) {
        return await requireAuth(request, env, "teacher", (u) => handleTeacher(p, request, env, u));
      }
      if (p.startsWith("/api/student/")) {
        return await requireAuth(request, env, "student", (u) => handleStudent(p, request, env, u));
      }

      // AI chat proxy (public, used by the frontend)
      if (p === "/api/chat" && request.method === "POST") return await handleChat(request, env);

      return txt("Not found", 404);
    } catch (e) {
      return json({ error: e.message }, 500);
    }
  }
};

/* ---------------- HTTP helpers ---------------- */

function corsPreflight() {
  return new Response(null, {
    status: 204,
    headers: {
      "Access-Control-Allow-Origin": ALLOWED_ORIGIN,
      "Access-Control-Allow-Methods": "POST, GET, OPTIONS",
      "Access-Control-Allow-Headers": "Content-Type, Authorization"
    }
  });
}

function withCors(response) {
  response.headers.set("Access-Control-Allow-Origin", ALLOWED_ORIGIN);
  return response;
}

function txt(body, status = 200) {
  return withCors(new Response(body, { status, headers: { "Content-Type": "text/plain; charset=utf-8" } }));
}

function json(obj, status = 200) {
  return withCors(new Response(JSON.stringify(obj), {
    status,
    headers: { "Content-Type": "application/json; charset=utf-8" }
  }));
}

async function readJson(request) {
  try { return await request.json(); } catch { return {}; }
}

/* ---------------- Crypto ---------------- */

function b64url(buf) {
  return btoa(String.fromCharCode(...new Uint8Array(buf)))
    .replace(/\+/g, "-").replace(/\//g, "_").replace(/=+$/, "");
}
function b64urlDecode(s) {
  s = s.replace(/-/g, "+").replace(/_/g, "/");
  return Uint8Array.from(atob(s), c => c.charCodeAt(0));
}

async function hashPassword(pw, saltB64) {
  const enc = new TextEncoder();
  const key = await crypto.subtle.importKey("raw", enc.encode(pw), "PBKDF2", false, ["deriveBits"]);
  const bits = await crypto.subtle.deriveBits(
    { name: "PBKDF2", salt: b64urlDecode(saltB64), iterations: 100000, hash: "SHA-256" },
    key, 256
  );
  return b64url(bits);
}

async function verifyPassword(pw, saltB64, hashB64) {
  const h = await hashPassword(pw, saltB64);
  return h === hashB64;
}

async function hmac(data, secret) {
  const enc = new TextEncoder();
  const key = await crypto.subtle.importKey("raw", enc.encode(secret), { name: "HMAC", hash: "SHA-256" }, false, ["sign"]);
  const sig = await crypto.subtle.sign("HMAC", key, enc.encode(data));
  return b64url(sig);
}

async function signToken(payload, secret) {
  const data = b64url(new TextEncoder().encode(JSON.stringify(payload)));
  const sig = await hmac(data, secret);
  return data + "." + sig;
}

async function verifyToken(token, secret) {
  if (!token) return null;
  const parts = token.split(".");
  if (parts.length !== 2) return null;
  const [data, sig] = parts;
  const expect = await hmac(data, secret);
  if (expect !== sig) return null;
  try {
    const p = JSON.parse(new TextDecoder().decode(b64urlDecode(data)));
    if (p.exp && p.exp < Math.floor(Date.now() / 1000)) return null;
    return p;
  } catch { return null; }
}

function randomSalt() {
  return b64url(crypto.getRandomValues(new Uint8Array(16)));
}

function randomPwd() {
  const chars = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789";
  let s = "";
  const a = crypto.getRandomValues(new Uint8Array(8));
  for (let i = 0; i < 8; i++) s += chars[a[i] % chars.length];
  return s;
}

/* ---------------- Auth ---------------- */

async function getAuth(request, env) {
  const h = request.headers.get("Authorization") || "";
  const m = h.match(/^Bearer\s+(.+)$/);
  if (!m) return null;
  return await verifyToken(m[1], env.SESSION_SECRET);
}

async function requireAuth(request, env, role, fn) {
  const auth = await getAuth(request, env);
  if (!auth) return json({ error: "unauthorized" }, 401);
  if (role && auth.role !== role) return json({ error: "forbidden" }, 403);
  return await fn(auth);
}

async function handleAuth(path, request, env) {
  if (!env.DB) return json({ error: "database not configured" }, 500);
  const body = await readJson(request);

  // Teacher self-registration
  if (path === "/api/auth/register" && request.method === "POST") {
    const { username, password, role } = body;
    if (!username || !password) return json({ error: "username and password required" }, 400);
    if (role && role !== "teacher") return json({ error: "students are created by teachers" }, 400);
    const exists = await env.DB.prepare("SELECT id FROM users WHERE username=?").bind(username).first();
    if (exists) return json({ error: "username taken" }, 409);
    const salt = randomSalt();
    const hash = await hashPassword(password, salt);
    const info = await env.DB.prepare(
      "INSERT INTO users (username, role, pwd_hash, pwd_salt, created_at) VALUES (?,?,?,?,?)"
    ).bind(username, "teacher", hash, salt, new Date().toISOString()).run();
    const userId = info.meta && info.meta.last_row_id;
    const token = await signToken({ uid: userId, role: "teacher", exp: Math.floor(Date.now() / 1000) + TOKEN_TTL_SEC }, env.SESSION_SECRET);
    return json({ token, role: "teacher", userId });
  }

  // Login (works for both roles)
  if (path === "/api/auth/login" && request.method === "POST") {
    const { username, password } = body;
    const row = await env.DB.prepare("SELECT id, role, pwd_hash, pwd_salt FROM users WHERE username=?").bind(username).first();
    if (!row) return json({ error: "invalid credentials" }, 401);
    const ok = await verifyPassword(password, row.pwd_salt, row.pwd_hash);
    if (!ok) return json({ error: "invalid credentials" }, 401);
    const token = await signToken({ uid: row.id, role: row.role, exp: Math.floor(Date.now() / 1000) + TOKEN_TTL_SEC }, env.SESSION_SECRET);
    return json({ token, role: row.role, userId: row.id });
  }

  // Current user
  if (path === "/api/auth/me" && request.method === "GET") {
    const auth = await getAuth(request, env);
    if (!auth) return json({ error: "unauthorized" }, 401);
    const u = await env.DB.prepare("SELECT id, username, role, class_id FROM users WHERE id=?").bind(auth.uid).first();
    return json({ user: u });
  }

  return json({ error: "unknown auth route" }, 404);
}

/* ---------------- Teacher ---------------- */

async function handleTeacher(path, request, env, auth) {
  const url = new URL(request.url);

  // Create a class
  if (path === "/api/teacher/class" && request.method === "POST") {
    const { name } = await readJson(request);
    const r = await env.DB.prepare("INSERT INTO classes (name, teacher_id) VALUES (?,?)")
      .bind(name || "默认班级", auth.uid).run();
    return json({ classId: r.meta && r.meta.last_row_id });
  }

  // Bulk-create student accounts for a class
  if (path === "/api/teacher/students" && request.method === "POST") {
    const { classId, count, prefix } = await readJson(request);
    const cls = await env.DB.prepare("SELECT id FROM classes WHERE id=? AND teacher_id=?").bind(classId, auth.uid).first();
    if (!cls) return json({ error: "class not found or not yours" }, 404);
    const created = [];
    const n = Math.min(Math.max(count || 10, 1), 200);
    for (let i = 0; i < n; i++) {
      const username = `${prefix || "stu"}${String(i + 1).padStart(3, "0")}`;
      const pwd = randomPwd();
      const salt = randomSalt();
      const hash = await hashPassword(pwd, salt);
      const info = await env.DB.prepare(
        "INSERT OR IGNORE INTO users (username, role, pwd_hash, pwd_salt, class_id, created_at) VALUES (?,?,?,?,?,?)"
      ).bind(username, "student", hash, salt, classId, new Date().toISOString()).run();
      if (info.meta && info.meta.last_row_id) created.push({ username, password: pwd });
    }
    return json({ created });
  }

  // List classes of this teacher
  if (path === "/api/teacher/classes" && request.method === "GET") {
    const rows = await env.DB.prepare("SELECT id, name FROM classes WHERE teacher_id=?").bind(auth.uid).all();
    return json({ classes: rows.results || [] });
  }

  // Student progress stats for a class
  if (path === "/api/teacher/stats" && request.method === "GET") {
    const classId = url.searchParams.get("classId");
    if (!classId) return json({ error: "classId required" }, 400);
    const rows = await env.DB.prepare(`
      SELECT u.id, u.username,
             COUNT(a.id) AS attempts,
             COALESCE(SUM(a.correct),0) AS correct
      FROM users u
      LEFT JOIN attempts a ON a.user_id = u.id
      WHERE u.role='student' AND u.class_id=?
      GROUP BY u.id
    `).bind(classId).all();
    return json({ stats: rows.results || [] });
  }

  // Export CSV report
  if (path === "/api/teacher/export" && request.method === "GET") {
    const classId = url.searchParams.get("classId");
    if (!classId) return json({ error: "classId required" }, 400);
    const rows = await env.DB.prepare(`
      SELECT u.username,
             COUNT(a.id) AS attempts,
             COALESCE(SUM(a.correct),0) AS correct
      FROM users u
      LEFT JOIN attempts a ON a.user_id = u.id
      WHERE u.role='student' AND u.class_id=?
      GROUP BY u.id
    `).bind(classId).all();
    const lines = ["username,attempts,correct,accuracy"];
    for (const r of (rows.results || [])) {
      const att = r.attempts || 0;
      const cor = r.correct || 0;
      const acc = att ? ((cor / att) * 100).toFixed(1) + "%" : "0%";
      lines.push(`${r.username},${att},${cor},${acc}`);
    }
    return new Response(lines.join("\n"), {
      headers: {
        "Content-Type": "text/csv; charset=utf-8",
        "Access-Control-Allow-Origin": ALLOWED_ORIGIN,
        "Content-Disposition": "attachment; filename=report.csv"
      }
    });
  }

  return json({ error: "unknown teacher route" }, 404);
}

/* ---------------- Student ---------------- */

async function handleStudent(path, request, env, auth) {
  // Record an attempt
  if (path === "/api/student/attempt" && request.method === "POST") {
    const { questionId, selected, correct } = await readJson(request);
    if (!questionId) return json({ error: "questionId required" }, 400);
    await env.DB.prepare(
      "INSERT INTO attempts (user_id, question_id, selected, correct, ts) VALUES (?,?,?,?,?)"
    ).bind(auth.uid, String(questionId), JSON.stringify(selected), correct ? 1 : 0, new Date().toISOString()).run();
    return json({ ok: true });
  }

  // My progress
  if (path === "/api/student/progress" && request.method === "GET") {
    const rows = await env.DB.prepare(
      "SELECT question_id, selected, correct, ts FROM attempts WHERE user_id=? ORDER BY ts DESC"
    ).bind(auth.uid).all();
    return json({ progress: rows.results || [] });
  }

  return json({ error: "unknown student route" }, 404);
}

/* ---------------- Setup ---------------- */

async function handleSetup(env) {
  if (!env.DB) return json({ error: "database not configured" }, 500);
  const stmts = [
    `CREATE TABLE IF NOT EXISTS users (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      username TEXT UNIQUE,
      role TEXT,
      pwd_hash TEXT,
      pwd_salt TEXT,
      class_id INTEGER,
      created_at TEXT
    )`,
    `CREATE TABLE IF NOT EXISTS classes (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      name TEXT,
      teacher_id INTEGER
    )`,
    `CREATE TABLE IF NOT EXISTS attempts (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      user_id INTEGER,
      question_id TEXT,
      selected TEXT,
      correct INTEGER,
      ts TEXT
    )`,
    `CREATE TABLE IF NOT EXISTS assignments (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      class_id INTEGER,
      title TEXT,
      question_ids TEXT,
      due_at TEXT
    )`,
    `CREATE TABLE IF NOT EXISTS feedback (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      attempt_id INTEGER,
      teacher_id INTEGER,
      comment TEXT,
      score INTEGER,
      ts TEXT
    )`
  ];
  for (const sql of stmts) {
    await env.DB.prepare(sql).run();
  }
  return json({ ok: true, message: "tables created" });
}

/* ---------------- AI chat proxy (RAG) ---------------- */

async function handleChat(request, env) {
  const data = await readJson(request);
  const message = (data.message || "").toString().trim();
  if (!message) return json({ error: "message is required" }, 400);

  const apiKey = env.LLM_API_KEY;
  if (!apiKey) return json({ error: "LLM_API_KEY not configured" }, 500);

  const { kb, qs, indexes } = await fetchRagCached();
  const { context, sources } = buildContext(message, kb, qs, indexes);

  const systemPrompt = context
    ? `You are an expert in civil aviation transport accounting. Answer the user's question based on the following knowledge base snippets. Cite the relevant sources briefly. If the snippets do not contain enough information, say so clearly.\n\n--- Knowledge base snippets ---\n${context}\n--- End of snippets ---`
    : "You are an expert in civil aviation transport accounting. Answer the user's question concisely and accurately.";

  const body = {
    model: env.LLM_MODEL || "deepseek-chat",
    messages: [
      { role: "system", content: systemPrompt },
      { role: "user", content: message }
    ],
    max_tokens: 800,
    temperature: 0.5
  };

  const dsResp = await fetch(`${DEEPSEEK_BASE}/chat/completions`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "Authorization": `Bearer ${apiKey}`
    },
    body: JSON.stringify(body)
  });

  if (!dsResp.ok) {
    const detail = await dsResp.text().catch(() => "");
    return json({ error: "DeepSeek request failed", status: dsResp.status, detail }, dsResp.status);
  }

  const dsData = await dsResp.json();
  const answer = dsData.choices?.[0]?.message?.content?.trim() || "";
  return json({ answer, sources });
}

async function fetchRagCached() {
  const now = Date.now();
  if (ragCache.kb && ragCache.qs && ragCache.indexes && now - ragCache.time < CACHE_TTL_MS) {
    return { kb: ragCache.kb, qs: ragCache.qs, indexes: ragCache.indexes };
  }
  const [kb, qs] = await Promise.all([fetchJson(KB_URL), fetchJson(QS_URL)]);
  const indexes = buildIndexes(kb, qs);
  ragCache = { kb, qs, indexes, time: now };
  return { kb, qs, indexes };
}

async function fetchJson(url) {
  const resp = await fetch(url, { cf: { cacheTtl: 300 } });
  if (!resp.ok) throw new Error(`Failed to fetch ${url}: ${resp.status}`);
  const text = await resp.text();
  return JSON.parse(text);
}

function tokenize(text) {
  return (text || "").toLowerCase()
    .split(/[^\u4e00-\u9fa5a-z0-9]+/)
    .filter(w => w.length >= 2 && w.length <= 20);
}

function buildIndexes(kb, qs) {
  const kbIndex = new Map();
  const qsIndex = new Map();
  if (Array.isArray(kb)) {
    kb.forEach((item, idx) => {
      const text = `${item.title || ""} ${item.keywords || ""} ${item.content || ""}`;
      for (const w of tokenize(text)) {
        if (!kbIndex.has(w)) kbIndex.set(w, new Set());
        kbIndex.get(w).add(idx);
      }
    });
  }
  if (Array.isArray(qs)) {
    qs.forEach((q, idx) => {
      const opts = [q.A, q.B, q.C, q.D].filter(Boolean).join(" ");
      const text = `${q.q || ""} ${opts} ${q.explain || ""} ${q.answer || ""}`;
      for (const w of tokenize(text)) {
        if (!qsIndex.has(w)) qsIndex.set(w, new Set());
        qsIndex.get(w).add(idx);
      }
    });
  }
  return { kbIndex, qsIndex };
}

function expandQuery(raw) {
  const words = new Set();
  const lower = raw.toLowerCase();
  for (const w of tokenize(lower)) words.add(w);
  for (const [base, list] of Object.entries(SYNONYMS)) {
    if (lower.includes(base)) list.forEach(s => words.add(s.toLowerCase()));
    for (const s of list) if (lower.includes(s)) words.add(base.toLowerCase());
  }
  return Array.from(words);
}

function countMatches(text, words) {
  if (!text || words.length === 0) return 0;
  const t = text.toLowerCase();
  let count = 0;
  for (const w of words) if (t.includes(w)) count += 1;
  return count;
}

function buildContext(query, kb, qs, indexes) {
  const words = expandQuery(query);
  if (words.length === 0) return { context: "", sources: [] };

  const candidateKb = new Map();
  const candidateQs = new Map();
  for (const w of words) {
    const kbHits = indexes.kbIndex.get(w);
    if (kbHits) for (const idx of kbHits) candidateKb.set(idx, (candidateKb.get(idx) || 0) + 1);
    const qsHits = indexes.qsIndex.get(w);
    if (qsHits) for (const idx of qsHits) candidateQs.set(idx, (candidateQs.get(idx) || 0) + 1);
  }

  const hits = [];
  for (const [idx, hitScore] of candidateKb) {
    const item = kb[idx];
    if (!item) continue;
    const score = countMatches(item.title, words) * 4
      + countMatches(item.keywords, words) * 5
      + countMatches(item.content, words) * 2
      + hitScore;
    if (score > 0) {
      const text = `[${item.chapter || ""}] ${item.title}\n${item.content || ""}`.trim();
      hits.push({ score, text, source: item.title || item.id });
    }
  }
  for (const [idx, hitScore] of candidateQs) {
    const q = qs[idx];
    if (!q) continue;
    const opts = [q.A, q.B, q.C, q.D].filter(Boolean).join(" ");
    const qText = `${q.q || ""} ${opts}`;
    const score = countMatches(qText, words) * 3
      + countMatches(q.explain, words) * 2
      + countMatches(q.answer, words) * 1
      + hitScore;
    if (score > 0) {
      const text = `[${q.ch || ""}] ${q.q || ""}\n答案：${q.answer || ""}\n解析：${q.explain || ""}`.trim();
      hits.push({ score, text, source: q.ch || q.id });
    }
  }

  hits.sort((a, b) => b.score - a.score);
  const topHits = hits.slice(0, 6);
  let budget = 1800;
  const chosen = [];
  const sources = [];
  for (const h of topHits) {
    if (budget <= 0) break;
    const chunk = h.text.length > 500 ? h.text.slice(0, 500) + "..." : h.text;
    if (chunk.length + 2 > budget) break;
    chosen.push(chunk);
    sources.push(h.source);
    budget -= chunk.length + 2;
  }
  return { context: chosen.join("\n\n"), sources };
}
