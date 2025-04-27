from fastapi import FastAPI, UploadFile, File, HTTPException
from paddlespeech.cli.asr.infer import ASRExecutor
import os
import tempfile
from typing import Dict, Any
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
    logger.info(f"Received audio file: {audio.filename}")
    
    if not audio.filename.endswith('.wav'):
        logger.error(f"Invalid file format: {audio.filename}")
        raise HTTPException(
            status_code=400,
            detail=create_response(
                code=400,
                message="Invalid file format. Only WAV files are supported.",
                data=None
            )
        )

    # 创建临时文件
    temp_file_path = None
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_file:
            # 保存上传的文件
            content = await audio.read()
            if not content:
                logger.error("Empty file content")
                raise HTTPException(
                    status_code=400,
                    detail=create_response(
                        code=400,
                        message="Empty file content",
                        data=None
                    )
                )
            temp_file.write(content)
            temp_file_path = temp_file.name
            logger.info(f"Saved temporary file: {temp_file_path}")

        # 检查文件大小
        file_size = os.path.getsize(temp_file_path)
        if file_size == 0:
            logger.error("File size is 0")
            raise HTTPException(
                status_code=400,
                detail=create_response(
                    code=400,
                    message="File size is 0",
                    data=None
                )
            )

        # 执行语音识别
        logger.info("Starting speech recognition")
        result = asr(audio_file=temp_file_path)
        logger.info(f"Recognition result: {result}")
        
        return create_response(
            code=200,
            message="Success",
            data={"text": result}
        )
    except Exception as e:
        logger.error(f"Speech recognition failed: {str(e)}", exc_info=True)
        return create_response(
            code=500,
            message=f"Speech recognition failed: {str(e)}",
            data=None
        )
    finally:
        # 清理临时文件
        if temp_file_path and os.path.exists(temp_file_path):
            try:
                os.unlink(temp_file_path)
                logger.info(f"Cleaned up temporary file: {temp_file_path}")
            except Exception as e:
                logger.error(f"Failed to clean up temporary file: {str(e)}")

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