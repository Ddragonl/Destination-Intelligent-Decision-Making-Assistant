"""
决策推荐服务
"""
from typing import List, Optional
from src.models.destination import Location, RouteInfo, Recommendation
from src.services.route_service import RouteService
from src.utils.helpers import format_duration, format_distance


class DecisionService:
    """决策推荐服务类"""
    
    def __init__(self):
        self.route_service = RouteService()
    
    def get_recommendation(self, user_location: Location,
                          store_locations: List[Location],
                          preferred_mode: Optional[str] = None) -> Recommendation:
        """
        获取推荐结果
        
        Args:
            user_location: 用户位置
            store_locations: 门店位置列表
            preferred_mode: 偏好的交通方式（可选）
        """
        # 获取所有路线
        all_routes = self.route_service.get_all_routes(
            user_location=user_location,
            store_locations=store_locations
        )
        
        if not all_routes:
            raise ValueError("未找到可用路线")
        
        # 比较路线
        comparison = self.route_service.compare_routes(all_routes)
        
        # 选择最优路线（优先考虑时间）
        best_route = comparison["sorted_routes"][0]
        
        # 如果有偏好交通方式，优先选择该方式的最优路线
        if preferred_mode and preferred_mode in comparison["best_by_mode"]:
            preferred_route = comparison["best_by_mode"][preferred_mode]
            # 如果偏好方式的时间不超过最优路线的1.2倍，则选择偏好方式
            if preferred_route.duration <= best_route.duration * 1.2:
                best_route = preferred_route
        
        # 获取备选方案（排除最优路线，取前3个）
        alternatives = [
            route for route in comparison["sorted_routes"][:4]
            if route.destination.name != best_route.destination.name or 
               route.traffic_mode != best_route.traffic_mode
        ][:3]
        
        # 生成比较摘要
        summary = self._generate_summary(
            best_route=best_route,
            alternatives=alternatives,
            comparison=comparison
        )
        
        return Recommendation(
            best_destination=best_route.destination,
            best_route=best_route,
            alternatives=alternatives,
            comparison_summary=summary
        )
    
    def _generate_summary(self, best_route: RouteInfo,
                         alternatives: List[RouteInfo],
                         comparison: dict) -> str:
        """生成比较摘要"""
        summary_parts = [
            f"推荐目的地：{best_route.destination.name}",
            f"地址：{best_route.destination.address}",
            f"交通方式：{self._get_mode_name(best_route.traffic_mode)}",
            f"预计时间：{format_duration(best_route.duration)}",
            f"距离：{format_distance(best_route.distance)}"
        ]
        
        if best_route.cost:
            summary_parts.append(f"费用：{best_route.cost}元")
        
        if best_route.route_detail:
            summary_parts.append(f"路线：{best_route.route_detail}")
        
        if alternatives:
            summary_parts.append("\n备选方案：")
            for i, alt in enumerate(alternatives, 1):
                summary_parts.append(
                    f"{i}. {alt.destination.name} - "
                    f"{self._get_mode_name(alt.traffic_mode)} - "
                    f"{format_duration(alt.duration)}"
                )
        
        return "\n".join(summary_parts)
    
    def _get_mode_name(self, mode: str) -> str:
        """获取交通方式中文名称"""
        mode_map = {
            "transit": "公共交通",
            "driving": "驾车",
            "walking": "步行",
            "riding": "骑行"
        }
        return mode_map.get(mode, mode)

