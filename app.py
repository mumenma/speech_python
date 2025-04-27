from fastapi import FastAPI, UploadFile, File, HTTPException
import os
import tempfile
import subprocess
from typing import Dict, Any
import logging
from paddlenlp import Taskflow

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Speech Recognition API")

# 初始化标点符号预测模型
punctuation = Taskflow("punctuation_restoration")

def add_punctuation(text: str) -> str:
    """
    使用 PaddleNLP 添加标点符号
    """
    if not text.strip():
        return text
    
    try:
        # 使用 PaddleNLP 的标点预测
        result = punctuation(text)
        return result[0] if isinstance(result, list) else result
    except Exception as e:
        logger.error(f"Failed to add punctuation: {str(e)}")
        return text

def asr_with_subprocess(audio_path: str) -> str:
    """
    使用子进程调用 PaddleSpeech CLI 进行语音识别
    """
    try:
        result = subprocess.run(
            ["paddlespeech", "asr", "--input", audio_path],
            capture_output=True,
            text=True
        )
        if result.returncode != 0:
            logger.error(f"ASR failed: {result.stderr}")
            raise RuntimeError(f"ASR failed: {result.stderr}")
        return result.stdout.strip()
    except Exception as e:
        logger.error(f"Subprocess error: {str(e)}")
        raise

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
        result = asr_with_subprocess(temp_file_path)
        logger.info(f"Recognition result: {result}")
        
        # 添加标点符号
        logger.info("Adding punctuation")
        punctuated_text = add_punctuation(result)
        logger.info(f"Punctuated text: {punctuated_text}")
        
        return create_response(
            code=200,
            message="Success",
            data={"text": punctuated_text}
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