"""
数据模型定义
"""
from pydantic import BaseModel
from typing import List, Optional


class Location(BaseModel):
    """位置信息"""
    name: str  # 位置名称
    longitude: float  # 经度
    latitude: float  # 纬度
    address: Optional[str] = None  # 详细地址


class RouteInfo(BaseModel):
    """路线信息"""
    destination: Location  # 目的地
    distance: float  # 距离（米）
    duration: int  # 时间（秒）
    traffic_mode: str  # 交通方式：driving/walking/transit/riding
    route_detail: Optional[str] = None  # 路线详情
    cost: Optional[float] = None  # 费用（元）
    steps: Optional[List[dict]] = None  # 详细步骤


class Recommendation(BaseModel):
    """推荐结果"""
    best_destination: Location  # 最优目的地
    best_route: RouteInfo  # 最优路线
    alternatives: List[RouteInfo] = []  # 备选方案
    comparison_summary: Optional[str] = None  # 比较摘要

