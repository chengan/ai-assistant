from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from typing import AsyncGenerator
import logging
import uuid
import json
from ..models.chat import ChatRequest, ChatResponse
from ..core.model_config import ModelMapping
from ..providers.factory import ProviderFactory
from ..utils.redis_helper import redis_client

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

def format_message(content: str, role: str = "user") -> dict:
    """格式化消息"""
    return {
        "role": role,
        "content": content
    }

async def stream_chat_response(provider, messages: list, model_id: str) -> AsyncGenerator[str, None]:
    """流式返回聊天响应"""
    try:
        logger.info(f"Starting stream chat with model: {model_id}")
        logger.info(f"Messages: {json.dumps(messages, ensure_ascii=False, indent=2)}")
        
        async for chunk in provider.stream_chat(messages, model_id):
            if chunk.content:
                response_data = {
                    "content": chunk.content,
                    "done": chunk.done
                }
                logger.info(f"Streaming chunk: {json.dumps(response_data, ensure_ascii=False)}")
                yield f"data: {json.dumps(response_data, ensure_ascii=False)}\n\n"
            else:
                logger.warning("Received empty chunk")
                
    except Exception as e:
        logger.error(f"Error in stream chat: {str(e)}", exc_info=True)
        error_data = {
            "error": str(e),
            "type": type(e).__name__
        }
        yield f"data: {json.dumps(error_data, ensure_ascii=False)}\n\n"
    finally:
        logger.info("Stream completed")
        yield "data: [DONE]\n\n"

@router.post("/chat", response_model=ChatResponse)
async def create_chat(chat_request: ChatRequest):
    request_id = chat_request.request_id or str(uuid.uuid4())
    
    try:
        # 记录请求数据
        logger.info(f"[{request_id}] ====== Chat Request Start ======")
        logger.info(f"[{request_id}] Request data: {json.dumps(chat_request.dict(), ensure_ascii=False, indent=2)}")
        
        # 获取模型信息
        model_info = ModelMapping.get_model_info(chat_request.provider_id)
        logger.info(f"[{request_id}] Model info: {json.dumps(model_info, ensure_ascii=False, indent=2)}")
        
        if not model_info:
            logger.error(f"[{request_id}] Invalid model ID: {chat_request.provider_id}")
            raise HTTPException(status_code=400, detail="Invalid model ID")

        # 创建对应的提供商实例
        provider = ProviderFactory.create(model_info["provider"])
        logger.info(f"[{request_id}] Created provider: {model_info['provider']}")
        
        # 处理对话历史
        messages = []
        
        # 添加系统提示语
        system_prompt = ModelMapping.get_system_prompt(chat_request.provider_id)
        if system_prompt:
            messages.append(format_message(system_prompt, "system"))
            logger.info(f"[{request_id}] Added system prompt: {system_prompt}")

        if chat_request.request_id:
            history = await redis_client.get_chat_history(chat_request.request_id)
            if history:
                messages.extend(history)
                logger.info(f"[{request_id}] Loaded chat history: {json.dumps(history, ensure_ascii=False, indent=2)}")
            else:
                logger.warning(f"[{request_id}] No history found for request_id: {chat_request.request_id}")
        
        # 添加新消息
        messages.append(format_message(chat_request.content))
        logger.info(f"[{request_id}] Final messages to provider: {json.dumps(messages, ensure_ascii=False, indent=2)}")
        
        # 调用AI服务
        logger.info(f"[{request_id}] Calling AI provider with model_id: {model_info['model_id']}")
        response = await provider.chat(messages, model_info["model_id"])
        logger.info(f"[{request_id}] Raw provider response: {json.dumps(response.raw_response, ensure_ascii=False, indent=2)}")
        
        # 保存对话历史
        messages.append(format_message(response.content, "assistant"))
        save_result = await redis_client.save_chat_history(request_id, messages)
        logger.info(f"[{request_id}] Save history result: {save_result}")
        
        # 构造响应
        response_data = ChatResponse(
            code=200,
            response=response.content,
            request_id=request_id
        )
        logger.info(f"[{request_id}] Final response: {json.dumps(response_data.dict(), ensure_ascii=False, indent=2)}")
        logger.info(f"[{request_id}] ====== Chat Request End ======")
        
        return response_data

    except Exception as e:
        logger.error(f"[{request_id}] ====== Error ======")
        logger.error(f"[{request_id}] Error type: {type(e).__name__}")
        logger.error(f"[{request_id}] Error message: {str(e)}")
        logger.error(f"[{request_id}] Stack trace:", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/chat/stream")
async def create_stream_chat(chat_request: ChatRequest):
    """流式聊天接口"""
    request_id = chat_request.request_id or str(uuid.uuid4())
    
    try:
        # 获取模型信息
        model_info = ModelMapping.get_model_info(chat_request.provider_id)
        if not model_info:
            raise HTTPException(status_code=400, detail="Invalid model ID")

        # 创建提供商实例
        provider = ProviderFactory.create(model_info["provider"])
        
        # 构建消息
        messages = []
        system_prompt = ModelMapping.get_system_prompt(chat_request.provider_id)
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})

        if chat_request.request_id:
            history = await redis_client.get_chat_history(chat_request.request_id)
            if history:
                messages.extend(history)

        messages.append({"role": "user", "content": chat_request.content})

        return StreamingResponse(
            stream_chat_response(provider, messages, model_info["model_id"]),
            media_type="text/event-stream"
        )
        
    except Exception as e:
        logger.error(f"[{request_id}] Error in stream chat endpoint: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/models")
async def list_models():
    """列出支持的模型"""
    try:
        models = ModelMapping.list_models()
        logger.info(f"Listing models: {json.dumps(models, ensure_ascii=False)}")
        return {"models": models}
    except Exception as e:
        logger.error(f"Error listing models: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e)) 