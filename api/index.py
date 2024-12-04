import sys
import os
from pathlib import Path

# 添加项目根目录到 Python 路径
root_path = Path(__file__).resolve().parent.parent
sys.path.append(str(root_path))

from src.main import app

# 导出 FastAPI 应用
export = app 