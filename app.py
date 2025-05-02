import os

# 设置环境变量
os.environ["MODELSCOPE_CACHE"] = os.path.expanduser("~/.cache/modelscope")
os.environ["MODELSCOPE_HUB"] = "https://modelscope.oss-cn-beijing.aliyuncs.com"

from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from funasr import AutoModel
from funasr.utils.postprocess_utils import rich_transcription_postprocess
import tempfile

app = FastAPI()

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 初始化语音识别模型
model_dir = "iic/SenseVoiceSmall"
model = AutoModel(
    model=model_dir,
    trust_remote_code=True,
    remote_code="./model.py",
    vad_model="fsmn-vad",
    vad_kwargs={"max_single_segment_time": 30000},
    device="cpu",  # 使用 CPU
)

def asr_with_sensevoice(audio_path: str) -> str:
    """使用SenseVoice进行语音识别"""
    res = model.generate(
        input=audio_path,
        cache={},
        language="auto",
        use_itn=True,
        batch_size_s=60,
        merge_vad=True,
        merge_length_s=15,
    )
    text = rich_transcription_postprocess(res[0]["text"])
    return text

@app.post("/recognize")
async def recognize_audio(file: UploadFile = File(...)):
    """接收音频文件并进行语音识别"""
    try:
        # 创建临时文件
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_file:
            content = await file.read()
            temp_file.write(content)
            temp_file_path = temp_file.name

        # 进行语音识别
        text = asr_with_sensevoice(temp_file_path)
        
        # 删除临时文件
        os.unlink(temp_file_path)
        
        return {"text": text}
    except Exception as e:
        return {"error": str(e)}

@app.get("/health")
async def health_check():
    """健康检查接口"""
    return {"status": "ok"}