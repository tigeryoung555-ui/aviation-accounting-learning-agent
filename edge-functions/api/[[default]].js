/* ============================================================
 * 民航运输企业会计学习智能体 — EdgeOne Pages Functions backend
 * Route: /api/*  (catch-all via edge-functions/api/[[default]].js)
 *
 * Migrated from Cloudflare Workers + D1 (SQLite) to EdgeOne Pages
 * Edge Functions + KV Storage, because *.workers.dev is blocked
 * on mainland China networks (DNS poisoning).
 *
 * Env vars required (set in EdgeOne console, never in frontend):
 *   SESSION_SECRET  — HMAC key for auth tokens
 *   LLM_API_KEY     — DeepSeek API key
 *   LLM_MODEL       — optional, defaults to deepseek-chat
 * ============================================================ */

import {
  getKV, getUserByUsername, putUser, getUserById, putClass, getClass,
  listClassesByTeacher, addStudentsToClass, listClassStudentIds,
  listUsersByIds, addAttempt, listAttemptsByUser, nextId
} from '../_lib_store.js';

const ALLOWED_ORIGINS = [
  'https://tigeryoung555-ui.github.io',
  'https://tigeryoung555.github.io',
  'http://localhost:8088',
  'http://127.0.0.1:8088'
];
const DEEPSEEK_BASE = 'https://api.deepseek.com/v1';
const KB_URL = 'https://raw.githubusercontent.com/tigeryoung555-ui/aviation-accounting-learning-agent/main/backend/kb_extra.json';
const QS_URL = 'https://raw.githubusercontent.com/tigeryoung555-ui/aviation-accounting-learning-agent/main/backend/questions.json';
const CACHE_TTL_MS = 5 * 60 * 1000;
const TOKEN_TTL_SEC = 60 * 60 * 24 * 7;

let ragCache = { kb: null, qs: null, time: 0 };

const SYNONYMS = {
  '飞机': ['航空器', '机型'],
  '租赁': ['融资租赁', '经营租赁', '使用权资产', '租赁负债'],
  '收入': ['确认收入', '营业收入', '主营业务收入'],
  '成本': ['运输成本', '营业成本', '主营业务成本'],
  '折旧': ['累计折旧', '固定资产折旧'],
  '里程': ['常旅客', '奖励里程', '里程兑换'],
  '燃油': ['航油', '油料'],
  '维修': ['修理', 'MRO', '维护']
};

export async function onRequest(context) {
  const { request, env } = context;
  const url = new URL(request.url);

  if (request.method === 'OPTIONS') return corsPreflight(request);

  try {
    const p = url.pathname;
    const origin = request.headers.get('Origin');

    if (p === '/' || p === '/api') return withCors(txt('minhang-api OK (EdgeOne)'), origin);
    if (p === '/api/config') {
      const secretSet = !!(env && env.SESSION_SECRET);
      const llmSet = !!(env && env.LLM_API_KEY);
      const kv = !!getKV(env);
      // 仅暴露环境变量「键名」，绝不输出值，便于排查配置是否生效。
      const envKeys = env ? Object.keys(env) : [];
      return withCors(json({
        available: true,
        model: (env && env.LLM_MODEL) || 'deepseek-chat',
        backend: 'edgeone-pages-functions',
        auth: secretSet,            // SESSION_SECRET 是否就绪（登录/注册）
        llmKey: llmSet,             // LLM_API_KEY 是否就绪（AI 答疑）
        kv: kv,                     // KV 命名空间是否绑定（班级管理/档案）
        envKeyCount: envKeys.length,
        envKeys: envKeys
      }), origin);
    }
    if (p.startsWith('/api/auth/')) return await handleAuth(p, request, env, origin);
    if (p.startsWith('/api/teacher/')) {
      return await requireAuth(request, env, 'teacher', (u) => handleTeacher(p, request, env, u, origin));
    }
    if (p.startsWith('/api/student/')) {
      return await requireAuth(request, env, 'student', (u) => handleStudent(p, request, env, u, origin));
    }
    if (p === '/api/chat' && request.method === 'POST') return await handleChat(request, env, origin);
    return withCors(txt('Not found', 404), origin);
  } catch (e) {
    return withCors(json({ error: (e && e.message) || String(e) }, 500), request.headers.get('Origin'));
  }
}

/* ---------------- CORS ---------------- */

function isAllowed(origin) {
  if (!origin) return true;
  return ALLOWED_ORIGINS.indexOf(origin) !== -1;
}

function corsPreflight(request) {
  const origin = request.headers.get('Origin');
  const headers = {
    'Access-Control-Allow-Methods': 'POST, GET, OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type, Authorization',
    'Access-Control-Max-Age': '86400',
    'Vary': 'Origin'
  };
  if (isAllowed(origin) && origin) {
    headers['Access-Control-Allow-Origin'] = origin;
  }
  return new Response(null, { status: 204, headers });
}

function withCors(response, origin) {
  if (isAllowed(origin) && origin) {
    response.headers.set('Access-Control-Allow-Origin', origin);
    response.headers.set('Vary', 'Origin');
  }
  return response;
}

function txt(body, status) {
  return new Response(body, { status: status || 200, headers: { 'Content-Type': 'text/plain; charset=utf-8' } });
}

function json(obj, status) {
  return new Response(JSON.stringify(obj), {
    status: status || 200,
    headers: { 'Content-Type': 'application/json; charset=utf-8' }
  });
}

async function readJson(request) {
  try { return await request.json(); } catch (e) { return {}; }
}

/* ---------------- Crypto ---------------- */

function b64url(buf) {
  let s = '';
  const arr = new Uint8Array(buf);
  for (let i = 0; i < arr.length; i++) s += String.fromCharCode(arr[i]);
  return btoa(s).replace(/\+/g, '-').replace(/\//g, '_').replace(/=+$/, '');
}

function b64urlDecode(s) {
  s = String(s).replace(/-/g, '+').replace(/_/g, '/');
  const bin = atob(s);
  const arr = new Uint8Array(bin.length);
  for (let i = 0; i < bin.length; i++) arr[i] = bin.charCodeAt(i);
  return arr;
}

async function hashPassword(pw, saltB64) {
  const enc = new TextEncoder();
  const key = await crypto.subtle.importKey('raw', enc.encode(pw), 'PBKDF2', false, ['deriveBits']);
  const bits = await crypto.subtle.deriveBits(
    { name: 'PBKDF2', salt: b64urlDecode(saltB64), iterations: 100000, hash: 'SHA-256' },
    key, 256
  );
  return b64url(bits);
}

async function verifyPassword(pw, saltB64, expectedHash) {
  if (!expectedHash) return false;
  return (await hashPassword(pw, saltB64)) === expectedHash;
}

async function hmac(data, secret) {
  const enc = new TextEncoder();
  const key = await crypto.subtle.importKey('raw', enc.encode(secret), { name: 'HMAC', hash: 'SHA-256' }, false, ['sign']);
  const sig = await crypto.subtle.sign('HMAC', key, enc.encode(data));
  return b64url(sig);
}

async function signToken(payload, secret) {
  const data = b64url(new TextEncoder().encode(JSON.stringify(payload)));
  const sig = await hmac(data, secret);
  return data + '.' + sig;
}

async function verifyToken(token, secret) {
  if (!token || !secret) return null;
  const parts = token.split('.');
  if (parts.length !== 2) return null;
  try {
    const expect = await hmac(parts[0], secret);
    if (expect !== parts[1]) return null;
    const p = JSON.parse(new TextDecoder().decode(b64urlDecode(parts[0])));
    if (p.exp && p.exp < Math.floor(Date.now() / 1000)) return null;
    return p;
  } catch (e) { return null; }
}

function randomSalt() {
  return b64url(crypto.getRandomValues(new Uint8Array(16)));
}

function randomPwd() {
  const chars = 'ABCDEFGHJKLMNPQRSTUVWXYZ23456789';
  const a = crypto.getRandomValues(new Uint8Array(8));
  let s = '';
  for (let i = 0; i < 8; i++) s += chars[a[i] % chars.length];
  return s;
}

/* ---------------- Auth ---------------- */

async function getAuth(request, env) {
  const h = request.headers.get('Authorization') || '';
  const m = h.match(/^Bearer\s+(.+)$/);
  if (!m) return null;
  return await verifyToken(m[1], env && env.SESSION_SECRET);
}

async function requireAuth(request, env, role, fn) {
  const auth = await getAuth(request, env);
  if (!auth) return json({ error: 'unauthorized' }, 401);
  if (role && auth.role !== role) return json({ error: 'forbidden' }, 403);
  return await fn(auth);
}

async function handleAuth(path, request, env, origin) {
  const kv = getKV(env);
  if (!kv) return withCors(json({ error: 'KV storage not bound. 请在 EdgeOne 控制台申请并绑定 KV 命名空间' }, 500), origin);
  const secret = (env && env.SESSION_SECRET) || '';
  if (!secret) return withCors(json({ error: 'SESSION_SECRET not configured' }, 500), origin);
  const body = await readJson(request);

  if (path === '/api/auth/register' && request.method === 'POST') {
    const { username, password, role } = body;
    if (!username || !password) return withCors(json({ error: 'username and password required' }, 400), origin);
    if (role && role !== 'teacher') return withCors(json({ error: 'students are created by teachers' }, 400), origin);
    if (await getUserByUsername(kv, username)) return withCors(json({ error: 'username taken' }, 409), origin);
    const id = await nextId(kv, 'user');
    const salt = randomSalt();
    const hash = await hashPassword(password, salt);
    const user = {
      id, username, role: 'teacher', pwd_hash: hash, pwd_salt: salt,
      class_id: null, created_at: new Date().toISOString()
    };
    await putUser(kv, user);
    const token = await signToken({ uid: id, role: 'teacher', exp: Math.floor(Date.now() / 1000) + TOKEN_TTL_SEC }, secret);
    return withCors(json({ token, role: 'teacher', userId: id }), origin);
  }

  if (path === '/api/auth/login' && request.method === 'POST') {
    const { username, password } = body;
    const row = await getUserByUsername(kv, username);
    if (!row) return withCors(json({ error: 'invalid credentials' }, 401), origin);
    const ok = await verifyPassword(password, row.pwd_salt, row.pwd_hash);
    if (!ok) return withCors(json({ error: 'invalid credentials' }, 401), origin);
    const token = await signToken({ uid: row.id, role: row.role, exp: Math.floor(Date.now() / 1000) + TOKEN_TTL_SEC }, secret);
    return withCors(json({ token, role: row.role, userId: row.id }), origin);
  }

  if (path === '/api/auth/me' && request.method === 'GET') {
    const auth = await getAuth(request, env);
    if (!auth) return withCors(json({ error: 'unauthorized' }, 401), origin);
    const stored = await getUserById(kv, auth.uid);
    if (!stored) return withCors(json({ error: 'unauthorized' }, 401), origin);
    return withCors(json({
      user: { id: stored.id, username: stored.username, role: stored.role, class_id: stored.class_id }
    }), origin);
  }

  return withCors(json({ error: 'unknown auth route' }, 404), origin);
}

/* ---------------- Teacher ---------------- */

async function handleTeacher(path, request, env, auth, origin) {
  const kv = getKV(env);

  if (path === '/api/teacher/class' && request.method === 'POST') {
    const { name } = await readJson(request);
    const id = await nextId(kv, 'class');
    const cls = { id, name: name || '默认班级', teacher_id: auth.uid };
    await putClass(kv, cls);
    return withCors(json({ classId: id }), origin);
  }

  if (path === '/api/teacher/students' && request.method === 'POST') {
    const { classId, count, prefix } = await readJson(request);
    const cls = await getClass(kv, classId);
    if (!cls || String(cls.teacher_id) !== String(auth.uid)) {
      return withCors(json({ error: 'class not found or not yours' }, 404), origin);
    }
    const created = [];
    const n = Math.min(Math.max(count || 10, 1), 200);
    const ids = [];
    for (let i = 0; i < n; i++) {
      const username = `${prefix || 'stu'}${String(i + 1).padStart(3, '0')}`;
      const existing = await getUserByUsername(kv, username);
      if (existing) { ids.push(existing.id); continue; }
      const id = await nextId(kv, 'user');
      const pwd = randomPwd();
      const salt = randomSalt();
      const hash = await hashPassword(pwd, salt);
      await putUser(kv, {
        id, username, role: 'student', pwd_hash: hash, pwd_salt: salt,
        class_id: Number(classId), created_at: new Date().toISOString()
      });
      ids.push(id);
      created.push({ username, password: pwd });
    }
    await addStudentsToClass(kv, classId, ids);
    return withCors(json({ created }), origin);
  }

  if (path === '/api/teacher/classes' && request.method === 'GET') {
    const rows = await listClassesByTeacher(kv, auth.uid);
    return withCors(json({ classes: rows.map(c => ({ id: c.id, name: c.name })) }), origin);
  }

  if (path === '/api/teacher/stats' && request.method === 'GET') {
    const classId = new URL(request.url).searchParams.get('classId');
    if (!classId) return withCors(json({ error: 'classId required' }, 400), origin);
    const stats = await collectClassStats(kv, classId);
    return withCors(json({ stats }), origin);
  }

  if (path === '/api/teacher/export' && request.method === 'GET') {
    const classId = new URL(request.url).searchParams.get('classId');
    if (!classId) return withCors(json({ error: 'classId required' }, 400), origin);
    const stats = await collectClassStats(kv, classId);
    const lines = ['username,attempts,correct,accuracy'];
    for (const r of stats) {
      const att = r.attempts || 0;
      const cor = r.correct || 0;
      const acc = att ? ((cor / att) * 100).toFixed(1) + '%' : '0%';
      lines.push(`${r.username},${att},${cor},${acc}`);
    }
    return withCors(new Response(lines.join('\n'), {
      status: 200,
      headers: {
        'Content-Type': 'text/csv; charset=utf-8',
        'Content-Disposition': 'attachment; filename=report.csv'
      }
    }), origin);
  }

  return withCors(json({ error: 'unknown teacher route' }, 404), origin);
}

async function collectClassStats(kv, classId) {
  const ids = await listClassStudentIds(kv, classId);
  const users = await listUsersByIds(kv, ids);
  const out = [];
  for (const u of users) {
    const atts = await listAttemptsByUser(kv, u.id);
    const att = atts.length;
    const cor = atts.filter(a => a.correct).length;
    out.push({ id: u.id, username: u.username, attempts: att, correct: cor });
  }
  return out;
}

/* ---------------- Student ---------------- */

async function handleStudent(path, request, env, auth, origin) {
  const kv = getKV(env);

  if (path === '/api/student/attempt' && request.method === 'POST') {
    const { questionId, selected, correct } = await readJson(request);
    if (!questionId) return withCors(json({ error: 'questionId required' }, 400), origin);
    await addAttempt(kv, auth.uid, {
      user_id: auth.uid,
      question_id: String(questionId),
      selected: JSON.stringify(selected),
      correct: correct ? 1 : 0,
      ts: new Date().toISOString()
    });
    return withCors(json({ ok: true }), origin);
  }

  if (path === '/api/student/progress' && request.method === 'GET') {
    const rows = await listAttemptsByUser(kv, auth.uid);
    return withCors(json({
      progress: rows.map(r => ({ question_id: r.question_id, selected: r.selected, correct: r.correct, ts: r.ts }))
    }), origin);
  }

  return withCors(json({ error: 'unknown student route' }, 404), origin);
}

/* ---------------- RAG + AI chat ---------------- */

// Chinese text has no spaces, so punctuation-only splitting leaves a whole
// sentence as ONE term ("飞机折旧方法有哪些") and never matches anything.
// We therefore also emit CJK bigrams, which is the cheapest reliable
// approximation of word segmentation for retrieval purposes.
function segmentCJK(text) {
  const out = [];
  const re = /[\u4e00-\u9fa5]+/g;
  let m;
  while ((m = re.exec(text)) !== null) {
    const seg = m[0];
    out.push(seg);
    for (let i = 0; i + 2 <= seg.length; i++) out.push(seg.slice(i, i + 2));
  }
  return out;
}

function expandQuery(query) {
  const q = String(query || '');
  const words = q.split(/[\s，。？、！；：.?!;:,.()（）"']+/)
    .filter(w => w.length >= 2)
    .map(w => w.toLowerCase());
  const grams = segmentCJK(q).filter(g => g.length >= 2);
  const extra = [];
  for (const w of words.concat(grams)) {
    if (SYNONYMS[w]) extra.push.apply(extra, SYNONYMS[w]);
  }
  return Array.from(new Set(words.concat(grams, extra)));
}

async function getRagData() {
  if (ragCache.kb && Date.now() - ragCache.time < CACHE_TTL_MS) return ragCache;
  const [kbRes, qsRes] = await Promise.all([fetch(KB_URL), fetch(QS_URL)]);
  const kb = await kbRes.json();
  const qs = await qsRes.json();
  const norm = arr => (arr || []).map(x => {
    if (x && typeof x.keywords === 'string') x.keywords = x.keywords.split(/[,，、;；\s]+/).filter(Boolean);
    return x;
  });
  const kbArr = Array.isArray(kb) ? kb : (kb.data || kb.knowledge || []);
  const qsArr = Array.isArray(qs) ? qs : (qs.data || qs.questions || []);
  ragCache = { kb: norm(kbArr), qs: norm(qsArr), time: Date.now() };
  return ragCache;
}

async function ragSearch(query, kbOverride) {
  const kb = kbOverride || (await getRagData()).kb;
  if (!kb || !kb.length) return { text: '知识库暂不可用。', sources: [] };

  const terms = expandQuery(query);
  const scored = [];
  for (let i = 0; i < kb.length; i++) {
    const k = kb[i];
    const title = String(k.title || '').toLowerCase();
    const chapter = String(k.chapter || '').toLowerCase();
    const content = String(k.content || '').toLowerCase();
    const kws = (k.keywords || []).map(x => String(x).toLowerCase());
    const hay = (chapter + ' ' + title + ' ' + content + ' ' + kws.join(' ')).toLowerCase();
    let score = 0;
    for (const t of terms) {
      const tt = String(t).toLowerCase();
      if (!tt) continue;
      // weight longer terms higher — a 4-char bigram match is stronger evidence
      const lenBonus = Math.min(tt.length, 4);
      if (title.indexOf(tt) !== -1) score += 6 * lenBonus;
      if (kws.indexOf(tt) !== -1) score += 4 * lenBonus;
      if (chapter.indexOf(tt) !== -1) score += 2 * lenBonus;
      if (content.indexOf(tt) !== -1) score += 1 * lenBonus;
      if (hay.indexOf(tt) !== -1) score += 0.5 * lenBonus;
    }
    if (score > 0) scored.push({ k, score });
  }

  if (!scored.length) return { text: '知识库中没有找到与「' + query + '」相关的内容。', sources: [] };

  scored.sort((a, b) => b.score - a.score);
  const top = scored[0];
  // Take the top hit as the answer, plus closely-related follow-ups as sources.
  const sources = scored.slice(0, 3).map(x =>
    ((x.k.chapter || '') + '·' + (x.k.title || '')).replace(/^·/, '')
  );
  let text = top.k.content;
  // Append the runner-up only if it is closely related (avoids noise).
  const second = scored[1];
  if (second && second.score >= top.score * 0.6 && second.k.content !== text) {
    text += '\n\n【相关】' + second.k.title + '：' + String(second.k.content || '').slice(0, 260);
  }
  return { text, sources };
}

async function handleChat(request, env, origin) {
  const { message } = await readJson(request);
  if (!message) return withCors(json({ error: 'message required' }, 400), origin);
  const apiKey = (env && env.LLM_API_KEY) || '';
  if (!apiKey) {
    const r = await ragSearch(message);
    return withCors(json({ answer: r.text, sources: r.sources, mode: 'rag-fallback' }), origin);
  }
  try {
    const { kb } = await getRagData();
    const r = await ragSearch(message, kb);
    const ctx = (kb || []).slice(0, 6).map(k =>
      `【${k.chapter || ''}·${k.title || ''}】${(k.content || '').slice(0, 300)}`
    ).join('\n');
    const prompt =
      '你是民航运输企业会计课程的助教。请依据下面的课程知识库回答问题，' +
      '先给出知识库结论，再补充解释；语言简洁专业，不要编造知识库以外的数据。\n\n' +
      '知识库：\n' + ctx + '\n\n问题：' + message;
    const resp = await fetch(DEEPSEEK_BASE + '/chat/completions', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', Authorization: 'Bearer ' + apiKey },
      body: JSON.stringify({
        model: (env && env.LLM_MODEL) || 'deepseek-chat',
        messages: [{ role: 'user', content: prompt }],
        temperature: 0.3,
        max_tokens: 800
      })
    });
    const j = await resp.json();
    const answer = j && j.choices && j.choices[0] && j.choices[0].message && j.choices[0].message.content;
    if (!answer) throw new Error('empty model response');
    return withCors(json({ answer, sources: r.sources, mode: 'llm' }), origin);
  } catch (e) {
    const r = await ragSearch(message);
    return withCors(json({ answer: r.text, sources: r.sources, mode: 'rag-fallback', error: (e && e.message) || 'llm failed' }), origin);
  }
}