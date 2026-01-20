"""
路线查询服务
"""
from typing import List, Dict
from src.models.destination import Location, RouteInfo
from src.services.map_service import MapService


class RouteService:
    """路线查询服务类"""
    
    def __init__(self):
        self.map_service = MapService()
    
    def get_all_routes(self, user_location: Location, 
                      store_locations: List[Location],
                      traffic_modes: List[str] = None) -> List[RouteInfo]:
        """
        批量查询所有路线
        
        Args:
            user_location: 用户位置
            store_locations: 门店位置列表
            traffic_modes: 交通方式列表，默认["transit", "driving", "walking"]
        """
        if traffic_modes is None:
            traffic_modes = ["transit", "driving", "walking"]
        
        all_routes = []
        
        for store in store_locations:
            for mode in traffic_modes:
                route_data = self.map_service.get_route(
                    origin=user_location,
                    destination=store,
                    mode=mode
                )
                
                if route_data:
                    route_info = RouteInfo(
                        destination=store,
                        distance=route_data.get("distance", 0),
                        duration=route_data.get("duration", 0),
                        traffic_mode=mode,
                        route_detail=route_data.get("route_detail"),
                        cost=route_data.get("cost"),
                        steps=route_data.get("steps")
                    )
                    all_routes.append(route_info)
        
        return all_routes
    
    def compare_routes(self, routes: List[RouteInfo]) -> Dict:
        """
        比较路线，返回排序后的结果
        
        Returns:
            {
                "sorted_routes": List[RouteInfo],  # 按时间排序
                "by_destination": Dict,  # 按目的地分组
                "best_by_mode": Dict  # 各交通方式最优
            }
        """
        # 按时间排序
        sorted_routes = sorted(routes, key=lambda x: x.duration)
        
        # 按目的地分组
        by_destination = {}
        for route in routes:
            dest_name = route.destination.name
            if dest_name not in by_destination:
                by_destination[dest_name] = []
            by_destination[dest_name].append(route)
        
        # 各交通方式最优
        best_by_mode = {}
        for route in routes:
            mode = route.traffic_mode
            if mode not in best_by_mode or route.duration < best_by_mode[mode].duration:
                best_by_mode[mode] = route
        
        return {
            "sorted_routes": sorted_routes,
            "by_destination": by_destination,
            "best_by_mode": best_by_mode
        }

