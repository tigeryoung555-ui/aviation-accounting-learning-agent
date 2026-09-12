// 公网 LLM 代理地址（由 Cloudflare Worker 提供，无需信用卡、免费）
// 部署后端后把下面改成你的 Worker 地址即可；留空或含 REPLACE 占位符时，前端自动回退本机 http://localhost:8000（本地 RAG 模式）
window.APP_API_BASE = "https://minhang-ai-proxy.tigeryoung555.workers.dev";
