from fastapi import FastAPI, UploadFile, File, HTTPException
from paddlespeech.cli.asr.infer import ASRExecutor
from paddlespeech.cli.text.infer import TextExecutor
import os
import tempfile
import subprocess
from typing import Dict, Any, List
import logging
import re

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Speech Recognition API")

# 初始化 ASR 执行器和标点符号预测执行器
asr = ASRExecutor()
text_executor = TextExecutor()

def split_text(text: str, max_length: int = 300) -> List[str]:
    """
    将长文本分割成较短的段落，使用更保守的分段策略
    """
    # 按多种标点符号分割
    segments = re.split(r'([。！？，；：])', text)
    result = []
    current_segment = ""
    
    for segment in segments:
        # 如果当前段加上新段超过最大长度，就保存当前段并开始新段
        if len(current_segment) + len(segment) > max_length:
            if current_segment:
                result.append(current_segment.strip())
            current_segment = segment
        else:
            current_segment += segment
            
        # 如果当前段已经达到最大长度，就保存它
        if len(current_segment) >= max_length:
            result.append(current_segment.strip())
            current_segment = ""
    
    # 添加最后一个段
    if current_segment:
        result.append(current_segment.strip())
    
    # 过滤掉空段
    result = [s for s in result if s]
    
    logger.info(f"Split text into {len(result)} segments")
    for i, seg in enumerate(result):
        logger.info(f"Segment {i+1} length: {len(seg)}")
    
    return result

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

def add_punctuation(text: str) -> str:
    """
    为文本添加标点符号，处理长文本
    """
    if not text.strip():
        return text
        
    # 分割文本
    segments = split_text(text)
    if not segments:
        return text
        
    logger.info(f"Processing {len(segments)} segments")
    
    # 对每段分别添加标点
    punctuated_segments = []
    for i, segment in enumerate(segments):
        try:
            logger.info(f"Processing segment {i+1}/{len(segments)}: {segment[:50]}...")
            punctuated = text_executor(text=segment)
            punctuated_segments.append(punctuated)
            logger.info(f"Successfully processed segment {i+1}")
        except Exception as e:
            logger.error(f"Failed to add punctuation to segment {i+1}: {str(e)}")
            logger.error(f"Segment content: {segment}")
            punctuated_segments.append(segment)  # 如果失败，使用原始文本
    
    # 合并结果
    result = "".join(punctuated_segments)
    logger.info(f"Final text length: {len(result)}")
    return result

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

        # 使用子进程执行语音识别
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