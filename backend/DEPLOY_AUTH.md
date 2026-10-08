# 部署带登录的 Cloudflare 后端（D1 数据库）

本后端在原有 AI 代理基础上，新增了**用户系统（教师/学生分角色登录）+ D1 数据库**。
前端改完后，任何人访问站点都需登录：学生练题、教师看统计，数据存在云端。

## 前置
- 你已在 Cloudflare 创建了 Worker `minhang-ai-proxy`（之前部署过 AI 代理）。
- 已把最新的 `cf-worker.js` 粘贴部署到该 Worker（内含 D1 相关代码）。

## 步骤

### 1. 创建 D1 数据库
1. 打开 https://dash.cloudflare.com/ → 左侧 **Storage & Databases → D1 SQL Database**。
2. 点 **Create database**。
3. 名称填 `minhang-ai-db`，地区任选，**Create**。
4. 记下数据库名（后面绑定要用）。

### 2. 把数据库绑定到 Worker
1. 进 **Workers & Pages → 你的 Worker `minhang-ai-proxy` → Settings → Variables and Bindings**（或 "Bindings" 标签）。
2. 点 **Add binding → D1 Database**（老界面可能是 "Add variable" 里选 D1）。
3. Variable name（绑定名）必须填：**`DB`**（代码里读的就是 `env.DB`）。
4. 选择刚才建的 `minhang-ai-db`。
5. 保存。

### 3. 设置环境变量
在同一 **Variables and Bindings** 页面，添加两条：

| 类型 | 名称 | 值 |
|---|---|---|
| Secret | `SESSION_SECRET` | 一串足够长的随机字符，例如 `a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6`（自己编 32 位以上） |
| Secret | `LLM_API_KEY` | 你已有的 DeepSeek key（`sk-...`，之前就有的） |

> `SESSION_SECRET` 只是用来给登录 token 签名，自己随便编个长串即可，无需真实密钥。
> 老版本可能还有 `LLM_MODEL`，不用填（默认 deepseek-chat）。

### 4. 重新部署 Worker
绑定和变量改了之后，要重新部署一次让配置生效：
- Worker 编辑页 → **Save and deploy**（或 Deploy 按钮）。
- 因为改了 binding，Cloudflare 会要求 redeploy。

### 5. 建表（只需一次）
浏览器打开：
```
https://minhang-ai-proxy.<你的子域名>.workers.dev/api/setup
```
返回 `{"ok":true,"message":"tables created"}` 即成功。
（这一步会创建 users / classes / attempts / assignments / feedback 五张表。）

### 6. 验证
打开：
```
https://minhang-ai-proxy.<你的子域名>.workers.dev/api/config
```
应看到 `"auth":true`（之前没数据库时是 false / 不显示）。

## 账号体系
- **教师**：自己注册。调用 `POST /api/auth/register`（前端会有注册页），首次注册即教师身份。
- **学生**：由教师在后台批量生成。调用 `POST /api/teacher/students`，会返回一批 `用户名 + 初始密码`，发给学生登录，学生登录后可改密码。
- **学生不自注册**（避免外人乱进），符合学校场景。

## 前端配合
前端（GitHub Pages 站点）需同步改造：加登录/注册页，登录后按角色分流学生端/教师端。
详见前端任务。改完前端后，把站点重新部署即可。

## 安全
- 密码用 PBKDF2 加盐哈希，不存明文。
- 登录后发 HMAC 签名 token，存前端 localStorage。
- 教师/学生接口都校验 token + 角色，越权返回 403。
- CORS 仍只放行你的 Pages 域名（不改）。
