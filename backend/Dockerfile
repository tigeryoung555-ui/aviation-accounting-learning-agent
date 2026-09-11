FROM python:3.11-slim
WORKDIR /app
COPY . .
ENV PORT=7860
EXPOSE 7860
# 监听端口由云平台注入的 PORT 环境变量决定（HF Spaces 固定为 7860）
CMD ["python", "hx_llm_server.py"]
