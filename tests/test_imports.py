def test_imports():
    # 测试基本导入
    from src.core.config import settings
    assert settings is not None
    
    # 测试 pydantic 导入
    from pydantic import BaseModel
    assert BaseModel is not None
    
    # 测试 pydantic_settings 导入
    from pydantic_settings import BaseSettings
    assert BaseSettings is not None 