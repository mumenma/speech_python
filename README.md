# Speech Recognition API

这是一个基于 PaddleSpeech 的语音识别 API 服务，使用 FastAPI 构建。

## 功能

- 支持 WAV 格式的音频文件识别
- 使用 PaddleSpeech 的 deepspeech2online_wenetspeech 模型
- 提供 RESTful API 接口

## 本地运行

1. 安装依赖：
```bash
pip install -r requirements.txt
```

2. 启动服务：
```bash

python -m uvicorn app:app --reload --host 0.0.0.0 --port 8011


uvicorn app:app --host 0.0.0.0 --port 8011
```

## Docker 运行

1. 构建镜像：
```bash
docker build -t speech-recognition-api .
```

2. 运行容器：
```bash
docker run -p 8011:8011 speech-recognition-api
```

## API 使用

### 语音识别

```bash
curl -X POST "http://localhost:8011/recognize" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "audio=@your_audio.wav"
```

### 健康检查

```bash
curl "http://localhost:8011/health"
```

## Docker 镜像

Docker 镜像可以从 GitHub Container Registry 获取：

```bash
docker pull ghcr.io/your-username/speech-recognition-api:latest
```

## 开发

1. 克隆仓库：
```bash
git clone https://github.com/your-username/speech-recognition-api.git
cd speech-recognition-api
```

2. 安装开发依赖：
```bash
pip install -r requirements.txt
```

3. 运行测试：
```bash
pytest
```

# speech_python
语音相关服务，通过fastapi进行封装

所使用的开源模型：
https://github.com/FunAudioLLM/SenseVoice
