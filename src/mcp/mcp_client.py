"""
MCP服务客户端
"""
from typing import Dict, Any, Optional
from src.models.destination import Location, Recommendation, RouteInfo
from src.services.map_service import MapService
from src.services.decision_service import DecisionService
from src.utils.helpers import parse_location_string


class MCPClient:
    """MCP客户端，用于处理智能体请求"""
    
    def __init__(self):
        self.map_service = MapService()
        self.decision_service = DecisionService()
    
    def process_request(self, user_location_str: str, 
                      store_name: str, 
                      city: str = "杭州",
                      preferred_mode: Optional[str] = None) -> Dict[str, Any]:
        """
        处理用户请求
        
        Args:
            user_location_str: 用户位置（地址或坐标）
            store_name: 连锁店名称
            city: 城市名称
            preferred_mode: 偏好的交通方式
        
        Returns:
            推荐结果字典
        """
        try:
            # 1. 解析用户位置
            user_location = self._get_user_location(user_location_str)
            if not user_location:
                return {
                    "success": False,
                    "error": f"无法解析用户位置: {user_location_str}"
                }
            
            # 2. 搜索门店
            store_locations = self.map_service.search_places(
                keywords=store_name,
                city=city
            )
            
            if not store_locations:
                return {
                    "success": False,
                    "error": f"未找到 {store_name} 在 {city} 的门店"
                }
            
            # 3. 获取推荐
            recommendation = self.decision_service.get_recommendation(
                user_location=user_location,
                store_locations=store_locations,
                preferred_mode=preferred_mode
            )
            
            # 4. 格式化返回结果
            return self._format_response(recommendation, store_locations)
            
        except Exception as e:
            return {
                "success": False,
                "error": f"处理请求时出错: {str(e)}"
            }
    
    def _get_user_location(self, location_str: str) -> Optional[Location]:
        """获取用户位置"""
        # 先尝试地理编码
        location = self.map_service.geocode(location_str)
        if location:
            return location
        
        # 如果失败，尝试解析坐标
        parsed = parse_location_string(location_str)
        if parsed.get("longitude") and parsed.get("latitude"):
            return Location(
                name=parsed["name"],
                longitude=parsed["longitude"],
                latitude=parsed["latitude"],
                address=parsed["address"]
            )
        
        return None
    
    def _format_response(self, recommendation: Recommendation,
                        all_stores: list) -> Dict[str, Any]:
        """格式化响应结果"""
        best = recommendation.best_route
        
        # 格式化详细路线
        route_details = self._format_route_details(best)
        
        response = {
            "success": True,
            "recommendation": {
                "destination": {
                    "name": recommendation.best_destination.name,
                    "address": recommendation.best_destination.address,
                    "coordinates": {
                        "longitude": recommendation.best_destination.longitude,
                        "latitude": recommendation.best_destination.latitude
                    }
                },
                "route": {
                    "traffic_mode": best.traffic_mode,
                    "traffic_mode_cn": self._get_mode_name_cn(best.traffic_mode),
                    "duration_seconds": best.duration,
                    "duration_formatted": self._format_duration(best.duration),
                    "distance_meters": best.distance,
                    "distance_formatted": self._format_distance(best.distance),
                    "cost": best.cost,
                    "details": route_details,
                    "summary": best.route_detail
                },
                "comparison_summary": recommendation.comparison_summary
            },
            "alternatives": [
                {
                    "destination": alt.destination.name,
                    "address": alt.destination.address,
                    "traffic_mode": self._get_mode_name_cn(alt.traffic_mode),
                    "duration": self._format_duration(alt.duration),
                    "distance": self._format_distance(alt.distance)
                }
                for alt in recommendation.alternatives
            ],
            "all_stores_found": len(all_stores),
            "stores_checked": [
                {
                    "name": store.name,
                    "address": store.address
                }
                for store in all_stores
            ]
        }
        
        return response
    
    def _format_route_details(self, route: RouteInfo) -> list:
        """格式化路线详细步骤"""
        if not route.steps:
            return []
        
        details = []
        if route.traffic_mode == "transit":
            # 公共交通路线
            for step in route.steps:
                if isinstance(step, dict):
                    if step.get("walking"):
                        walk = step["walking"]
                        # 确保distance是数字类型（API可能返回字符串）
                        distance = walk.get('distance', 0)
                        try:
                            distance = float(distance) if distance else 0
                        except (ValueError, TypeError):
                            distance = 0
                        details.append({
                            "type": "walking",
                            "instruction": f"步行 {distance/1000:.1f}公里",
                            "distance": distance,
                            "duration": walk.get('duration', 0)
                        })
                    elif step.get("bus"):
                        bus = step["bus"]
                        buslines = bus.get("buslines", [])
                        if buslines:
                            bl = buslines[0]
                            details.append({
                                "type": "bus",
                                "instruction": f"乘坐 {bl.get('name', '公交')}",
                                "departure": bl.get('departure_stop', {}).get('name', ''),
                                "arrival": bl.get('arrival_stop', {}).get('name', ''),
                                "duration": bl.get('duration', 0)
                            })
                    elif step.get("railway"):
                        rail = step["railway"]
                        details.append({
                            "type": "subway",
                            "instruction": f"乘坐 {rail.get('name', '地铁')}",
                            "departure": rail.get('departure_stop', {}).get('name', ''),
                            "arrival": rail.get('arrival_stop', {}).get('name', ''),
                            "duration": rail.get('duration', 0)
                        })
        else:
            # 其他交通方式
            for i, step in enumerate(route.steps[:10], 1):  # 最多显示10步
                if isinstance(step, dict):
                    details.append({
                        "step": i,
                        "instruction": step.get("instruction", "")[:50],
                        "distance": step.get("distance", 0),
                        "duration": step.get("duration", 0)
                    })
        
        return details
    
    def _get_mode_name_cn(self, mode: str) -> str:
        """获取交通方式中文名称"""
        mode_map = {
            "transit": "公共交通（公交/地铁）",
            "driving": "驾车",
            "walking": "步行",
            "riding": "骑行"
        }
        return mode_map.get(mode, mode)
    
    def _format_duration(self, seconds: int) -> str:
        """格式化时间"""
        from src.utils.helpers import format_duration
        return format_duration(seconds)
    
    def _format_distance(self, meters: float) -> str:
        """格式化距离"""
        from src.utils.helpers import format_distance
        return format_distance(meters)

