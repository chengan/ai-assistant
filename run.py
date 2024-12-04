import os
import uvicorn
from typing import Optional

def load_env_file(env: str) -> None:
    """加载环境配置文件"""
    env_file = f".env.{env}"
    if os.path.exists(env_file):
        print(f"Loading environment from {env_file}")
        from dotenv import load_dotenv
        load_dotenv(env_file)
    else:
        print(f"Warning: {env_file} not found")

def main(env: Optional[str] = None):
    """启动服务"""
    # 如果指定了环境，加载对应的配置
    if env:
        load_env_file(env)
    
    uvicorn.run(
        "src.main:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
        log_level="info"
    )

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--env",
        choices=["local", "development", "production", "vercel"],
        default="local",
        help="指定运行环境"
    )
    args = parser.parse_args()
    main(args.env) 