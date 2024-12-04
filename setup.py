from setuptools import setup, find_packages

setup(
    name="ai-assistant",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        "fastapi==0.109.0",
        "pydantic==2.6.0",
        "pydantic-settings==2.1.0",
        "httpx==0.26.0",
        "pytest==7.4.4",
        "pytest-asyncio==0.23.4",
    ],
) 