/* ============================================================
 * KV storage layer — replaces Cloudflare D1 (SQLite) with
 * EdgeOne Pages KV Storage (key-value, eventually consistent).
 *
 * Design: expose a tiny query API mirroring the subset of D1 we
 * actually used, so the business logic below stays readable.
 *
 * KV is a GLOBAL variable named by the binding (e.g. aviation_kv),
 * NOT reachable via context.env. See kvGet/kvPut wrappers below.
 * ============================================================ */

// Resolve the bound KV namespace. The binding name is configurable;
// we probe a few known names so one project works regardless of
// which name the operator picked in the console.
function getKV(env) {
  const candidates = ['aviation_kv', 'AVIATION_KV', 'kv', 'KV'];
  for (const name of candidates) {
    if (typeof globalThis[name] !== 'undefined' && globalThis[name]) return globalThis[name];
  }
  // Allow explicit override via environment variable holding the name.
  const named = env && env.KV_BINDING_NAME && globalThis[env.KV_BINDING_NAME];
  return named || null;
}

async function kvGetJSON(kv, key) {
  if (!kv) return null;
  try {
    const raw = await kv.get(key);
    if (raw === null || raw === undefined) return null;
    return typeof raw === 'string' ? JSON.parse(raw) : raw;
  } catch (e) {
    return null;
  }
}

async function kvPutJSON(kv, key, value) {
  if (!kv) throw new Error('KV storage not bound');
  await kv.put(key, JSON.stringify(value));
}

/* -------- Collection helpers (list all records under a prefix) -------- */

async function kvListAll(kv, prefix) {
  const out = [];
  if (!kv) return out;
  let cursor;
  do {
    const res = await kv.list({ prefix, limit: 1000, cursor });
    const keys = (res && res.keys) || [];
    for (const k of keys) {
      const name = typeof k === 'string' ? k : (k && (k.name || k.key));
      if (!name) continue;
      const rec = await kvGetJSON(kv, name);
      if (rec) out.push(rec);
    }
    cursor = res && res.complete ? null : (res && res.cursor);
  } while (cursor);
  return out;
}

/* -------- users -------- */

const K_USER_PREFIX = 'u_';
const K_USERNAME_IDX = 'idx_username_';

async function getUserByUsername(kv, username) {
  const id = await kvGetJSON(kv, K_USERNAME_IDX + username.toLowerCase());
  if (!id) return null;
  return await kvGetJSON(kv, K_USER_PREFIX + id);
}

async function putUser(kv, user) {
  await kvPutJSON(kv, K_USER_PREFIX + user.id, user);
  await kvPutJSON(kv, K_USERNAME_IDX + user.username.toLowerCase(), user.id);
  return user;
}

async function getUserById(kv, id) {
  if (id === null || id === undefined) return null;
  return await kvGetJSON(kv, K_USER_PREFIX + id);
}

async function listUsersByIds(kv, ids) {
  const out = [];
  for (const id of (ids || [])) {
    const u = await getUserById(kv, id);
    if (u) out.push(u);
  }
  return out;
}

async function deleteUser(kv, id, username) {
  await kv.delete(K_USER_PREFIX + id);
  await kv.delete(K_USERNAME_IDX + String(username).toLowerCase());
}

/* -------- classes -------- */

const K_CLASS_PREFIX = 'c_';

async function putClass(kv, cls) {
  await kvPutJSON(kv, K_CLASS_PREFIX + cls.id, cls);
  return cls;
}

async function listClassesByTeacher(kv, teacherId) {
  const all = await kvListAll(kv, K_CLASS_PREFIX);
  return all.filter(c => String(c.teacher_id) === String(teacherId));
}

async function getClass(kv, id) {
  return await kvGetJSON(kv, K_CLASS_PREFIX + id);
}

/* -------- students by class (maintained as its own list) -------- */

const K_CLASS_STUDENTS = 'cls_students_';

async function addStudentsToClass(kv, classId, userIds) {
  const key = K_CLASS_STUDENTS + classId;
  const cur = (await kvGetJSON(kv, key)) || [];
  const merged = Array.from(new Set(cur.concat(userIds)));
  await kvPutJSON(kv, key, merged);
  return merged;
}

async function listClassStudentIds(kv, classId) {
  return (await kvGetJSON(kv, K_CLASS_STUDENTS + classId)) || [];
}

/* -------- attempts (append-only, keyed per user) -------- */

const K_ATTEMPT_PREFIX = 'a_';

function attemptKey(userId, ts, seq) {
  // sortable-ish key so list() returns chronological order
  return K_ATTEMPT_PREFIX + String(userId).padStart(8, '0') + '_' + ts.replace(/[^0-9]/g, '') + '_' + seq;
}

async function addAttempt(kv, userId, attempt) {
  const seq = String((await kvGetJSON(kv, 'seq_' + userId)) || 0);
  await kvPutJSON(kv, 'seq_' + userId, String(Number(seq) + 1));
  const key = attemptKey(userId, attempt.ts, seq);
  await kvPutJSON(kv, key, attempt);
  return key;
}

async function listAttemptsByUser(kv, userId) {
  const prefix = K_ATTEMPT_PREFIX + String(userId).padStart(8, '0') + '_';
  const all = await kvListAll(kv, prefix);
  return all.sort((a, b) => String(a.ts).localeCompare(String(b.ts)));
}

/* -------- id sequence -------- */

async function nextId(kv, name) {
  const key = 'seqid_' + name;
  const cur = Number((await kvGetJSON(kv, key)) || 0) + 1;
  await kvPutJSON(kv, key, cur);
  return cur;
}

/* -------- exports -------- */

export {
  getKV,
  getUserByUsername, putUser, getUserById, listUsersByIds, deleteUser,
  putClass, getClass, listClassesByTeacher,
  addStudentsToClass, listClassStudentIds,
  addAttempt, listAttemptsByUser,
  nextId
};