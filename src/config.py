"""
配置文件管理
"""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """应用配置"""
    # 高德地图API配置
    amap_api_key: str = ""
    amap_base_url: str = "https://restapi.amap.com/v3"
    
    # MCP服务配置
    mcp_server_url: Optional[str] = None
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


# 全局配置实例
settings = Settings()

