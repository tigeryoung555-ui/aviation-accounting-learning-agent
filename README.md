# 民航运输企业会计学习智能体 v2.0

> 单文件 HTML 应用，零外部依赖，打开即用。题库含 **1219 题**（民航特色 687 + 物流通用 532），覆盖 **19 章**、**162 条知识库**、**3 套组卷规则**。

## 在线访问
https://tigeryoung555-ui.github.io/aviation-accounting-learning-agent/

## 文件说明
- `index.html`：完整单文件应用（含题目、知识库、章节内容、JS/CSS）。
- `questions.json`：合并题库源数据（1219 题）。
- `chapter_content_extra.json` + `kb_extra.json`：旧版物流骨架章节与知识库补充。
- `gen_mvp_v2.py`：生成 `index.html` 的脚本。
- `merge_old_bank.js`：将旧版 1014 题并入 MVP 206 题的脚本。
- `hx_llm_server.py`：可选本地 LLM 代理（OpenAI 兼容）。
- `server_config.json`：LLM 代理配置文件（填入 `api_key` 后启用真实 AI）。
- `questions_mvp206_backup.json` + `index_mvp206_backup.html`：原始 206 题 MVP 备份。

## 本地使用
1. 双击 `index.html` 即可在浏览器打开。
2. 想要接入真实大模型：
   - 在 `server_config.json` 填入你的 API Key（支持 DeepSeek / Ark / 通义千问 / OpenAI 兼容接口）。
   - 命令行运行 `python hx_llm_server.py`。
   - 浏览器打开 `http://localhost:8000`（或继续双击 `index.html`，前端会自动检测 `localhost:8000`）。
3. 未启动代理时，AI 答疑使用增强本地 RAG（知识库+题库解析+FAQ）。

## 重新生成 index.html
```bash
python gen_mvp_v2.py
```

## 数据合并（如再需把旧题库并入）
```bash
node merge_old_bank.js
python gen_mvp_v2.py
```

## 部署
本项目为静态单页，已部署到 GitHub Pages。后续更新可复用 `C:/tmp/deploy_api.sh`（因本机代理限制，`git push` 走 github.com 被拦截，改用 GitHub API 推送）。

## 版权与来源
- 民航专题题目与知识库：基于《民用航空运输企业会计》课程材料整理。
- 物流通用骨架题目：来自原《物流企业会计》单课程融合版题库。
