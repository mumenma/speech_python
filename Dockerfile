FROM python:3.9-slim

# 设置工作目录
WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    build-essential \
    cmake \
    libsndfile1 \
    wget \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements.txt .

# 升级 pip 并安装依赖
RUN python -m pip install --upgrade pip \
    && python -m pip install -r requirements.txt

# 复制应用代码
COPY . .

# 设置环境变量
ENV PYTHONUNBUFFERED=1
ENV MODELSCOPE_CACHE=/app/.cache/modelscope
ENV MODELSCOPE_HUB=https://modelscope.oss-cn-beijing.aliyuncs.com

# 创建缓存目录
RUN mkdir -p /app/.cache/modelscope

# 创建非 root 用户
RUN useradd -m appuser && chown -R appuser:appuser /app
USER appuser

# 暴露端口
EXPOSE 8011

# 启动应用
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8011"]