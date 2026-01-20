"""
启动Web服务器
"""
import uvicorn
import os
import sys

if __name__ == "__main__":
    # 检查.env文件
    env_file = os.path.join(os.path.dirname(__file__), ".env")
    if not os.path.exists(env_file):
        print("⚠️  警告：未找到.env文件")
        print("请创建.env文件并配置AMAP_API_KEY")
        print("示例：AMAP_API_KEY=你的高德地图API_Key")
        print("\n继续启动服务器...\n")
    
    # 启动服务器
    print("🚀 启动目的地自主决策智能体Web服务...")
    print("📱 访问地址: http://localhost:8000")
    print("按 Ctrl+C 停止服务\n")
    
    uvicorn.run(
        "src.api:app",
        host="0.0.0.0",
        port=8000,
        reload=True,  # 开发模式，代码修改自动重载
        log_level="info"
    )

