import re
from moviepy.editor import VideoFileClip
from temp_file_handler import TempFileHandler
from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from funasr import AutoModel
from funasr.utils.postprocess_utils import rich_transcription_postprocess

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

def clean_text(text: str) -> str:
    """清理文本中的表情符号和重复标点"""
    # 移除表情符号
    text = re.sub(r'[\U00010000-\U0010ffff]', '', text)
    # 处理重复的标点符号
    text = re.sub(r'。{2,}', '。', text)
    text = re.sub(r'，{2,}', '，', text)
    text = re.sub(r'！{2,}', '！', text)
    text = re.sub(r'？{2,}', '？', text)
    # 移除多余的空格
    text = ' '.join(text.split())
    return text.strip()

def asr_with_sensevoice(audio_path: str) -> str:
    """使用SenseVoice进行语音识别"""
    res = model.generate(
        input=audio_path,
        cache={},
        language="auto",
        use_itn=True,
        batch_size_s=60,
        merge_vad=True,
        merge_length_s=15
    )
    text = rich_transcription_postprocess(res[0]["text"])
    return clean_text(text)

def convert_mp4_to_wav(mp4_path: str) -> str:
    """将MP4文件转换为WAV格式"""
    wav_path = mp4_path.replace('.mp4', '.wav')
    video = VideoFileClip(mp4_path)
    video.audio.write_audiofile(wav_path)
    video.close()
    return wav_path

# 修改 /recognize 接口
@app.post("/recognize")
async def recognize_audio(file: UploadFile = File(...)):
    """接收音频文件并进行语音识别"""
    handler = TempFileHandler()
    try:
        # 创建临时文件
        with handler.create_temp_file(suffix=file.filename.split('.')[-1]) as temp_file_path:
            content = await file.read()
            with open(temp_file_path, 'wb') as f:
                f.write(content)

            # 如果是MP4文件，先转换为WAV
            if file.filename.lower().endswith('.mp4'):
                temp_file_path = convert_mp4_to_wav(temp_file_path)

            # 进行语音识别
            text = asr_with_sensevoice(temp_file_path)

            # 删除临时文件
            handler.delete_file(temp_file_path)
        
        return JSONResponse(
            status_code=200,
            content={
                "code": 0,
                "message": "success",
                "data": {
                    "text": text
                }
            }
        )
        
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "code": 1,
                "message": str(e),
                "data": None
            }
        )

# 修改 /recognize_mp4 接口
@app.post("/recognize_mp4")
async def recognize_mp4(file: UploadFile = File(...)):
    """接收MP4视频文件并进行语音识别"""
    if not file.filename.lower().endswith('.mp4'):
        return JSONResponse(
            status_code=400,
            content={
                "code": 1,
                "message": "Only MP4 files are supported",
                "data": None
            }
        )
    
    handler = TempFileHandler()
    try:
        # 创建临时文件
        with handler.create_temp_file(suffix='.mp4') as temp_file_path:
            content = await file.read()
            with open(temp_file_path, 'wb') as f:
                f.write(content)

            # 转换为WAV格式
            wav_path = convert_mp4_to_wav(temp_file_path)
            handler.temp_files.append(wav_path)  # 将wav_path添加到缓存列表
            
            # 进行语音识别
            text = asr_with_sensevoice(wav_path)

            # 删除临时文件
            handler.delete_file(temp_file_path)
            handler.delete_file(wav_path)
        
        return JSONResponse(
            status_code=200,
            content={
                "code": 0,
                "message": "success",
                "data": {
                    "text": text
                }
            }
        )
        
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "code": 1,
                "message": str(e),
                "data": None
            }
        )
@app.get("/health")
async def health_check():
    """健康检查接口"""
    return {"status": "ok"}