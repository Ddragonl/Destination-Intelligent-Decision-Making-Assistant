"""
地图API服务封装（高德地图）
"""
import requests
from typing import List, Optional, Dict
from src.config import settings
from src.models.destination import Location


class MapService:
    """地图服务类"""
    
    def __init__(self):
        self.api_key = settings.amap_api_key
        self.base_url = settings.amap_base_url
        
        if not self.api_key:
            raise ValueError("请配置高德地图API Key（在.env文件中设置AMAP_API_KEY）")
    
    def geocode(self, address: str) -> Optional[Location]:
        """
        地理编码：将地址转换为坐标
        """
        url = f"{self.base_url}/geocode/geo"
        params = {
            "key": self.api_key,
            "address": address,
            "output": "json"
        }
        
        try:
            response = requests.get(url, params=params, timeout=10)
            data = response.json()
            
            if data.get("status") == "1" and data.get("geocodes"):
                geocode = data["geocodes"][0]
                location_str = geocode.get("location", "")
                if location_str:
                    lon, lat = map(float, location_str.split(","))
                    return Location(
                        name=address,
                        longitude=lon,
                        latitude=lat,
                        address=geocode.get("formatted_address", address)
                    )
        except Exception as e:
            print(f"地理编码错误: {e}")
        
        return None
    
    def search_places(self, keywords: str, city: str = "杭州", 
                     types: Optional[str] = None) -> List[Location]:
        """
        搜索地点（POI搜索）
        
        Args:
            keywords: 关键词（如"联想电脑专卖店"）
            city: 城市名称
            types: POI类型（可选）
        """
        url = f"{self.base_url}/place/text"
        params = {
            "key": self.api_key,
            "keywords": keywords,
            "city": city,
            "output": "json",
            "offset": 20,  # 返回结果数量
            "page": 1
        }
        
        if types:
            params["types"] = types
        
        locations = []
        
        try:
            response = requests.get(url, params=params, timeout=10)
            data = response.json()
            
            if data.get("status") == "1" and data.get("pois"):
                for poi in data["pois"]:
                    location_str = poi.get("location", "")
                    if location_str:
                        lon, lat = map(float, location_str.split(","))
                        locations.append(Location(
                            name=poi.get("name", ""),
                            longitude=lon,
                            latitude=lat,
                            address=poi.get("address", "") or poi.get("pname", "") + 
                                   poi.get("cityname", "") + poi.get("adname", "")
                        ))
        except Exception as e:
            print(f"搜索地点错误: {e}")
        
        return locations
    
    def get_route(self, origin: Location, destination: Location, 
                  mode: str = "transit") -> Optional[Dict]:
        """
        获取路线规划
        
        Args:
            origin: 起点
            destination: 终点
            mode: 交通方式
                - driving: 驾车
                - walking: 步行
                - transit: 公交/地铁
                - riding: 骑行
        """
        origin_str = f"{origin.longitude},{origin.latitude}"
        dest_str = f"{destination.longitude},{destination.latitude}"
        
        # 根据交通方式选择不同的API端点
        if mode == "transit":
            url = f"{self.base_url}/direction/transit/integrated"
        elif mode == "driving":
            url = f"{self.base_url}/direction/driving"
        elif mode == "walking":
            url = f"{self.base_url}/direction/walking"
        elif mode == "riding":
            url = f"{self.base_url}/direction/bicycling"
        else:
            url = f"{self.base_url}/direction/transit/integrated"
        
        params = {
            "key": self.api_key,
            "origin": origin_str,
            "destination": dest_str,
            "output": "json",
            "city": "杭州"
        }
        
        if mode == "transit":
            params["cityd"] = "杭州"  # 目标城市
        
        try:
            response = requests.get(url, params=params, timeout=10)
            data = response.json()
            
            if data.get("status") == "1":
                if mode == "transit":
                    routes = data.get("route", {}).get("transits", [])
                    if routes:
                        route = routes[0]  # 取第一条路线
                        return {
                            "distance": int(route.get("distance", 0)),
                            "duration": int(route.get("duration", 0)),
                            "cost": float(route.get("cost", 0)) if route.get("cost") else None,
                            "steps": route.get("segments", []),
                            "route_detail": self._format_transit_route(route)
                        }
                else:
                    routes = data.get("route", {}).get("paths", [])
                    if routes:
                        route = routes[0]
                        return {
                            "distance": int(route.get("distance", 0)),
                            "duration": int(route.get("duration", 0)),
                            "steps": route.get("steps", []),
                            "route_detail": self._format_route(route, mode)
                        }
        except Exception as e:
            print(f"路线规划错误: {e}")
        
        return None
    
    def _format_transit_route(self, route: Dict) -> str:
        """格式化公交路线详情"""
        segments = route.get("segments", [])
        details = []
        
        for segment in segments:
            if segment.get("walking"):
                walk = segment["walking"]
                # 确保distance是数字类型（API可能返回字符串）
                distance = walk.get('distance', 0)
                try:
                    distance = float(distance) if distance else 0
                except (ValueError, TypeError):
                    distance = 0
                details.append(f"步行 {distance/1000:.1f}公里")
            elif segment.get("bus"):
                bus = segment["bus"]
                buslines = bus.get("buslines", [])
                if buslines:
                    busline = buslines[0]
                    details.append(
                        f"乘坐{busline.get('name', '公交')} "
                        f"({busline.get('departure_stop', {}).get('name', '')} → "
                        f"{busline.get('arrival_stop', {}).get('name', '')})"
                    )
            elif segment.get("railway"):
                railway = segment["railway"]
                details.append(
                    f"乘坐{railway.get('name', '地铁')} "
                    f"({railway.get('departure_stop', {}).get('name', '')} → "
                    f"{railway.get('arrival_stop', {}).get('name', '')})"
                )
        
        return " → ".join(details) if details else "路线详情"
    
    def _format_route(self, route: Dict, mode: str) -> str:
        """格式化路线详情"""
        steps = route.get("steps", [])
        if not steps:
            return f"{mode}路线"
        
        # 简化显示前几个关键步骤
        key_steps = steps[:3] if len(steps) > 3 else steps
        details = [step.get("instruction", "")[:20] for step in key_steps]
        return " → ".join(details)

