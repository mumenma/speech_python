from fastapi import FastAPI, UploadFile, File, HTTPException
from paddlespeech.cli.asr.infer import ASRExecutor
import os
import tempfile
from typing import Dict, Any

app = FastAPI(title="Speech Recognition API")

# 初始化 ASR 执行器
asr = ASRExecutor()

def create_response(code: int, message: str, data: Any = None) -> Dict:
    """
    创建统一的响应格式
    """
    return {
        "code": code,
        "message": message,
        "data": data
    }

@app.post("/recognize")
async def recognize_speech(audio: UploadFile = File(...)):
    """
    接收音频文件并返回识别结果
    """
    if not audio.filename.endswith('.wav'):
        raise HTTPException(
            status_code=400,
            detail=create_response(
                code=400,
                message="Invalid file format. Only WAV files are supported.",
                data=None
            )
        )

    # 创建临时文件
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_file:
        # 保存上传的文件
        content = await audio.read()
        temp_file.write(content)
        temp_file_path = temp_file.name

    try:
        # 执行语音识别，使用 conformer_aishell 模型
        result = asr(audio_file=temp_file_path, model="conformer_aishell")
        return create_response(
            code=200,
            message="Success",
            data={"text": result}
        )
    except Exception as e:
        return create_response(
            code=500,
            message=f"Speech recognition failed: {str(e)}",
            data=None
        )
    finally:
        # 清理临时文件
        os.unlink(temp_file_path)

@app.get("/health")
async def health_check():
    """
    健康检查接口
    """
    return create_response(
        code=200,
        message="Service is healthy",
        data={"status": "healthy"}
    ) 