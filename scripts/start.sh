#!/bin/bash
# 生产环境启动脚本

# 激活虚拟环境（如果使用）
# source /path/to/venv/bin/activate

# 启动服务
uvicorn src.main:app --host 0.0.0.0 --port 8000 --workers 4 