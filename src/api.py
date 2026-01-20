"""
FastAPI后端API接口
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Optional
from src.mcp.mcp_client import MCPClient
import os

app = FastAPI(title="目的地自主决策智能体", version="1.0.0")

# 配置CORS，允许前端跨域访问
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应该设置具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 静态文件服务（用于提供前端页面）
static_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "static")
if not os.path.exists(static_dir):
    os.makedirs(static_dir, exist_ok=True)
app.mount("/static", StaticFiles(directory=static_dir), name="static")


# 请求模型
class QueryRequest(BaseModel):
    """查询请求模型"""
    user_location: str  # 用户位置
    store_name: str  # 连锁店名称
    city: str = "杭州"  # 城市
    preferred_mode: Optional[str] = None  # 偏好交通方式：transit/driving/walking/riding


# 响应模型
class QueryResponse(BaseModel):
    """查询响应模型"""
    success: bool
    recommendation: Optional[dict] = None
    alternatives: Optional[list] = None
    all_stores_found: Optional[int] = None
    stores_checked: Optional[list] = None
    error: Optional[str] = None


# 初始化MCP客户端
mcp_client = MCPClient()


@app.get("/")
async def index():
    """返回前端页面"""
    html_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "static", "index.html")
    if os.path.exists(html_path):
        return FileResponse(html_path)
    else:
        return {"message": "前端页面未找到，请确保static/index.html存在"}


@app.post("/api/query", response_model=QueryResponse)
async def query_destination(request: QueryRequest):
    """
    查询目的地推荐
    
    Args:
        request: 查询请求，包含用户位置、门店名称等
    
    Returns:
        推荐结果，包含最优目的地、路线、备选方案等
    """
    try:
        result = mcp_client.process_request(
            user_location_str=request.user_location,
            store_name=request.store_name,
            city=request.city,
            preferred_mode=request.preferred_mode
        )
        
        if result.get("success"):
            return QueryResponse(
                success=True,
                recommendation=result.get("recommendation"),
                alternatives=result.get("alternatives", []),
                all_stores_found=result.get("all_stores_found", 0),
                stores_checked=result.get("stores_checked", [])
            )
        else:
            return QueryResponse(
                success=False,
                error=result.get("error", "未知错误")
            )
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"服务器错误: {str(e)}")


@app.get("/api/health")
async def health_check():
    """健康检查"""
    return {"status": "ok", "message": "服务运行正常"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

