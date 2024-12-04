import sys
import os
from pathlib import Path
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    # 添加项目根目录到 Python 路径
    root_path = Path(__file__).resolve().parent.parent
    sys.path.append(str(root_path))
    logger.info(f"Python path: {sys.path}")
    
    from src.main import app
    logger.info("Successfully imported FastAPI app")
    
except Exception as e:
    logger.error(f"Error during import: {str(e)}", exc_info=True)
    raise

# 导出 FastAPI 应用
export = app 