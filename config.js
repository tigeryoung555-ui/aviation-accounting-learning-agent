// 公网 LLM 代理地址（由后端 hx_llm_server.py 提供）
// 部署后端（Render / Railway / HuggingFace）后，把下面改成你的后端地址，例如：
//   window.APP_API_BASE = "https://minhang-ai-proxy.onrender.com";
// 留空或含 REPLACE 占位符时，前端自动回退到本机 http://localhost:8000（本地 RAG 模式）
window.APP_API_BASE = "REPLACE_WITH_RENDER_URL";
