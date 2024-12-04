from typing import Dict, Optional

class ModelMapping:
    # 内部模型ID到实际模型信息的映射
    MODEL_MAP = {
        "model_001": {
            "provider": "tongyi",
            "model_id": "qwen-plus",
            "name": "通义千问Plus",
            "description": "通义千问大模型"
        },
        "model_002": {
            "provider": "tongyi",
            "model_id": "qwen-max",
            "name": "通义千问Max",
            "description": "通义千问大模型"
        },
        "model_003": {
            "provider": "baichuan",
            "model_id": "Baichuan2-53B",
            "name": "百川大模型",
            "description": "百川智能开发的大语言模型"
        },
        "model_004": {
            "provider": "baichuan",
            "model_id": "Baichuan2-Turbo",
            "name": "百川Turbo",
            "description": "百川智能开发的对话模型"
        }
    }

    @classmethod
    def get_model_info(cls, internal_id: str) -> Optional[Dict]:
        """获取模型信息"""
        return cls.MODEL_MAP.get(internal_id)

    @classmethod
    def get_system_prompt(cls, internal_id: str) -> Optional[str]:
        """获取模型特定的系统提示语"""
        prompts = {
            "model_001": "你是通义千问助手，一个强大的AI助手。请用简洁、专业的方式回答问题。",
            "model_002": "你是通义千问Max助手，一个更强大的AI助手。请用详细、专业的方式回答问题。",
            "model_003": "你是百川大模型助手，一个强大的AI助手。请用专业的方式回答问题。",
            "model_004": "你是百川Turbo助手，一个高效的AI助手。请用简洁的方式回答问题。",
        }
        return prompts.get(internal_id)

    @classmethod
    def list_models(cls) -> list:
        """获取模型列表"""
        return [
            {
                "id": model_id,
                "name": info["name"],
                "provider": info["provider"]
            }
            for model_id, info in cls.MODEL_MAP.items()
        ] 