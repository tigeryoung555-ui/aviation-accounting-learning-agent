# 民航会计学习智能体 · 公网 LLM 代理（后端）

为前端 GitHub Pages 站点提供「真实大模型答疑」能力的后端服务。基于 Python 标准库实现，零第三方依赖，可直接部署到 Render / Railway / HuggingFace Spaces / 任意支持 Python 的云平台。

## 功能
- `GET  /api/config` 返回后端是否配置好 LLM（`{configured, model}`）
- `POST /api/chat` 接收 `{message}`，先做民航知识库 RAG 检索，再把上下文交给 DeepSeek 生成专业回答，返回 `{answer, sources}`
- CORS 仅允许指定的前端域名（默认 `https://tigeryoung555-ui.github.io`），不暴露任何源码/数据文件

## 配置（优先级：环境变量 > server_config.json > 默认值）
| 变量 | 说明 | 默认 |
|------|------|------|
| `LLM_API_BASE` | OpenAI 兼容接口地址 | `https://api.deepseek.com/v1` |
| `LLM_MODEL` | 模型名 | `deepseek-chat` |
| `LLM_API_KEY` | API Key（也可叫 `DEEPSEEK_API_KEY`） | 空 |
| `LLM_TEMPERATURE` | 温度 | `0.7` |
| `ALLOWED_ORIGIN` | 允许跨域的前端域名 | `https://tigeryoung555-ui.github.io` |
| `PORT` | 监听端口（云平台自动注入） | `8000` |

> 安全：请勿把含真实 Key 的 `server_config.json` 提交到公开仓库；生产环境一律用环境变量注入 Key。

## 一键部署
- **Render**：连接本仓库，Root Directory 填 `backend`，Build `pip install -r requirements.txt`，Start `python hx_llm_server.py`；或在控制台导入 `render.yaml`。部署后在 Environment 填写 `LLM_API_KEY`。
- **Railway**：连接仓库，`railway.json` 已配置；在 Variables 填 `LLM_API_KEY`。
- **HuggingFace Spaces**：选 Docker SDK，把本目录内容上传，在 Settings→Variables 填 `LLM_API_KEY` 与 `ALLOWED_ORIGIN`。

## 本地运行
```bash
cd backend
python hx_llm_server.py
# 或填好 server_config.json 后运行
curl http://localhost:8000/api/config
curl -X POST http://localhost:8000/api/chat -H 'Content-Type: application/json' -d '{"message":"飞机折旧采用什么方法？"}'
```

## 前端对接
前端通过 `config.js` 中的 `window.APP_API_BASE` 指定本服务地址（如 `https://minhang-ai-proxy.onrender.com`）。未配置或后端不可达时，前端自动回退到内置本地 RAG。
