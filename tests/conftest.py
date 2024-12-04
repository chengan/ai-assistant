import os
import sys
import pytest

# 获取项目根目录的绝对路径
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, PROJECT_ROOT)

@pytest.fixture(autouse=True)
def env_setup():
    """设置测试环境变量"""
    os.environ["DASHSCOPE_API_KEY"] = "test_api_key"
    os.environ["SECRET_KEY"] = "test_secret_key" 