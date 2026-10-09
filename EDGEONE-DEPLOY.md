# 民航运输企业会计学习智能体 — 部署到腾讯云 EdgeOne Pages

后端已从 **Cloudflare Workers + D1** 迁移到 **EdgeOne Pages Functions + KV Storage**。

## 为什么迁移

`*.workers.dev` 域名在中国大陆被封锁（GreatFire 记录：自 2022-05-10 起持续屏蔽，DNS 污染 + 丢包，2026-09-21 最新测试仍"已屏蔽"）。`*.pages.dev` 同等级被墙，因此 Cloudflare 自家方案在国内均不可用。EdgeOne 为腾讯云产品，境内 3200+ 节点，实测可达。

## 费用与额度

免费版永久提供，**无需绑定信用卡**：

| 项目 | 免费额度 |
|---|---|
| Edge Functions 请求 | 300 万次/月 |
| Edge Functions CPU | 300 万次/月 |
| KV 存储 | 1 GB |
| 构建次数 | 500 次/月 |

官方承诺超出额度也不中断服务。

## 部署步骤（首次配置，约 10 分钟）

### 1. 注册腾讯云

打开 https://cloud.tencent.com/ ，**微信扫码注册**并完成实名认证（教师身份即可，无需绑卡）。

### 2. 创建 Pages 项目

1. 进入 EdgeOne Pages 控制台：https://pages.edgeone.ai/
2. 用 **GitHub 账号登录并授权**
3. 选择 `tigeryoung555-ui/aviation-accounting-learning-agent` 仓库
4. 选择 **Root** 目录（仓库根目录）
5. 构建命令留空，输出目录填 `/`（静态文件直接在根）
6. 点击部署，等待完成

### 3. 开通 KV 存储（关键步骤，不可跳过）

1. EdgeOne Pages 控制台 → 左侧 **KV 存储**
2. 点击 **立即申请**（免费 1GB），等待通过
3. 点击 **创建命名空间**，命名空间名称填：`aviation_kv`
4. 进入项目详情 → **KV 存储** → **绑定命名空间** → 选择 `aviation_kv`
5. **变量名必须填 `aviation_kv`**（代码通过全局变量 `aviation_kv` 访问，名字不一致会读不到数据）

### 4. 配置环境变量

项目详情 → **环境变量** → 添加：

| 变量名 | 值 | 说明 |
|---|---|---|
| `SESSION_SECRET` | 32 位随机字符串 | 登录 token 的 HMAC 签名密钥，**必须设置** |
| `LLM_API_KEY` | `sk-...`（DeepSeek key） | AI 答疑用；不填则自动降级为本地知识库检索 |
| `LLM_MODEL` | `deepseek-chat` | 可选，默认即此 |

> `SESSION_SECRET` 生成方法：随便输入一串足够长的随机字符，例如 `a97dceceef305b05709452bd072fe579685a5912ca`。

⚠️ **密钥只放环境变量，绝不能写进前端代码或提交到 GitHub。**

### 5. 绑定自定义域名（可选）

项目详情 → **自定义域名** → 添加。绑域名后访问更快更稳定。

### 6. 切换前端 API 地址

部署成功后会得到 `https://<项目名>.edgeone.app` 或 `xxx.edgeone.cool` 地址。

打开仓库里的 `config.js`，把地址改成：

```js
window.APP_API_BASE = "https://你的项目.edgeone.app";
```

同时把 `gen_mvp_v2.py` 第 175 行的内联兜底地址一并改成同一个值，然后重新生成 `index.html` 并推送。

### 7. 允许你的站点来源（CORS）

代码内 `ALLOWED_ORIGINS` 白名单目前是：
- `https://tigeryoung555-ui.github.io`（GitHub Pages 站点）
- `http://localhost:8088`（本地开发）

如果你的前端部署在别的域名，需在 `edge-functions/api/[[default]].js` 的 `ALLOWED_ORIGINS` 数组里加上。

## 本地开发

```bash
npm install -g edgeone
edgeone pages link     # 关联项目，同步 KV 与环境变量
edgeone pages dev      # 本地起服务，默认 http://localhost:8088
```

## 目录结构

```
├── edge-functions/
│   ├── _lib_store.js              # KV 存储层（替代原 D1）
│   └── api/
│       └── [[default]].js         # catch-all，对应 /api/*
├── index.html                     # 前端（静态）
├── config.js                      # API 地址配置
├── package.json                   # 需含 "type": "module"
└── gen_mvp_v2.py                  # 前端生成器
```

## 验证

部署完成后依次验证：

1. 浏览器打开 `https://<你的域名>/api/config` → 应返回 JSON，含 `"backend":"edgeone-pages-functions"`
2. 前端注册教师账号 → 成功进入教师端
3. 创建班级 → 批量生成学生账号
4. 学生账号登录 → 做题 → 教师端刷新统计能看到记录

## 常见问题

| 现象 | 原因 |
|---|---|
| 提示 `KV storage not bound` | 没绑 KV 命名空间，或变量名不是 `aviation_kv` |
| 提示 `SESSION_SECRET not configured` | 环境变量没配或没保存生效 |
| 数据写入后读不到 | KV 是**最终一致性**，全球同步约需 60 秒 |
| AI 答疑显示"本地知识库检索模式" | `LLM_API_KEY` 未配置或调用失败，会自动降级，不影响使用 |
| 前端报 `Failed to fetch` | 检查 `config.js` 地址是否为 EdgeOne 域名，且已强刷（Ctrl+Shift+R） |