# 目的地自主决策智能体

一个基于MCP服务和地图API的智能目的地推荐系统，能够根据用户位置和连锁店名称，自动查询所有门店的路程时间，比较后推荐最优目的地和交通方案。

## 功能特点

- 🔍 **自动搜索**：根据连锁店名称自动搜索所有门店
- 🗺️ **多种交通方式**：支持公交/地铁、驾车、步行、骑行
- ⏱️ **精确计算**：精确计算路程和时间
- 🎯 **智能推荐**：综合考虑时间、距离等因素推荐最优方案
- 📋 **详细指引**：提供完整的路线指引和换乘步骤
- 🖥️ **Web界面**：美观的现代化Web界面，实时地图显示
- 📱 **响应式设计**：支持桌面和移动设备

## 技术栈

- **后端**：Python 3.8+, FastAPI, Uvicorn
- **前端**：HTML5, CSS3, JavaScript (ES6+)
- **地图服务**：高德地图 API
- **数据验证**：Pydantic
- **HTTP请求**：Requests

## 项目结构

```
目的地自主决策智能体/
├── src/                    # 后端代码
│   ├── main.py            # 命令行主程序入口
│   ├── api.py             # FastAPI Web服务器
│   ├── config.py          # 配置管理
│   ├── models/             # 数据模型
│   │   └── destination.py
│   ├── services/           # 业务逻辑层
│   │   ├── map_service.py      # 地图API服务
│   │   ├── route_service.py    # 路线规划服务
│   │   └── decision_service.py # 决策推荐服务
│   ├── mcp/               # MCP服务集成
│   │   └── mcp_client.py
│   └── utils/             # 工具函数
│       └── helpers.py
├── static/                # 前端静态文件
│   ├── index.html         # Web界面
│   └── config.js          # 前端配置
├── requirements.txt        # Python依赖
├── start_server.py        # Web服务器启动脚本
└── README.md              # 本文档
```

## 核心功能

### 1. 智能门店搜索
系统根据用户输入的连锁店名称，自动搜索该城市内所有相关门店，无需手动查找。

### 2. 多交通方式路线规划
支持多种交通方式的路线规划：
- 公共交通（公交/地铁）
- 驾车
- 步行
- 骑行

### 3. 智能推荐算法
综合考虑以下因素推荐最优方案：
- 时间最短（主要因素）
- 距离最短（次要因素）
- 交通方式便利性
- 费用（可选）

### 4. 详细路线指引
提供完整的路线信息：
- 起点和终点位置
- 详细换乘步骤
- 预计时间和距离
- 费用信息（如有）

### 5. Web界面
- 实时地图显示路线
- 直观的查询表单
- 清晰的结果展示
- 响应式设计，支持移动设备

## API说明

### Web API接口

#### POST /api/query

查询目的地推荐

**请求体**：
```json
{
    "user_location": "浙江大学紫金港校区",
    "store_name": "联想电脑专卖店",
    "city": "杭州",
    "preferred_mode": "transit"
}
```

**响应**：
```json
{
    "success": true,
    "recommendation": {
        "destination": {
            "name": "联想3C服务中心",
            "address": "杭州市...",
            "coordinates": {
                "longitude": 120.xxx,
                "latitude": 30.xxx
            }
        },
        "route": {
            "traffic_mode": "transit",
            "traffic_mode_cn": "公共交通（公交/地铁）",
            "duration_formatted": "45分钟",
            "distance_formatted": "12.5公里",
            "cost": 5.0,
            "details": [...],
            "summary": "路线详情"
        }
    },
    "alternatives": [...],
    "all_stores_found": 5
}
```

### Python API

#### MCPClient.process_request()

处理用户请求并返回推荐结果。

**参数**：
- `user_location_str`: 用户位置（地址字符串或坐标）
- `store_name`: 连锁店名称
- `city`: 城市名称（默认"杭州"）
- `preferred_mode`: 偏好交通方式（可选：transit/driving/walking/riding）

**返回**：
```python
{
    "success": True,
    "recommendation": {
        "destination": {...},
        "route": {...},
        "comparison_summary": "..."
    },
    "alternatives": [...],
    "all_stores_found": 5,
    "stores_checked": [...]
}
```

## 使用方式

### Web界面使用
启动服务器后，在浏览器中使用图形界面，支持实时地图显示。

### 命令行使用
通过命令行工具快速查询，适合脚本调用。

### Python代码调用
作为Python模块导入使用，方便集成到其他项目。

### HTTP API调用
通过RESTful API调用，支持跨语言集成。

## 注意事项

1. **API配额限制**：高德地图API有调用频率限制，请合理使用
2. **坐标系统**：使用GCJ-02坐标系（高德地图标准）
3. **网络要求**：需要稳定的网络连接访问地图API
4. **Python版本**：推荐使用Python 3.8或更高版本
5. **浏览器兼容**：推荐使用Chrome、Firefox、Edge等现代浏览器

## 开发建议

如果需要自定义功能：

1. **修改样式**：编辑 `static/index.html` 中的CSS
2. **修改逻辑**：编辑 `static/index.html` 中的JavaScript
3. **修改API**：编辑 `src/api.py` 中的接口
4. **修改算法**：编辑 `src/services/` 中的服务模块

## 许可证

MIT License
