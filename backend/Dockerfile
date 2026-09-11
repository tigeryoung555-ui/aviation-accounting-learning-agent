FROM python:3.11-slim
WORKDIR /app
COPY . .
EXPOSE 8000
# 监听端口由云平台注入的 PORT 环境变量决定
CMD ["python", "hx_llm_server.py"]
