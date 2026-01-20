"""
工具函数
"""
import re


def parse_location_string(location_str: str) -> dict:
    """
    解析位置字符串，提取坐标或地址
    返回: {"name": str, "longitude": float, "latitude": float, "address": str}
    """
    # 如果是坐标格式 "经度,纬度"
    coord_pattern = r'(\d+\.?\d*),(\d+\.?\d*)'
    match = re.search(coord_pattern, location_str)
    if match:
        return {
            "longitude": float(match.group(1)),
            "latitude": float(match.group(2)),
            "name": location_str,
            "address": location_str
        }
    
    # 否则作为地址名称处理
    return {
        "name": location_str,
        "address": location_str,
        "longitude": None,
        "latitude": None
    }


def format_duration(seconds: int) -> str:
    """格式化时间显示"""
    if seconds < 60:
        return f"{seconds}秒"
    elif seconds < 3600:
        minutes = seconds // 60
        return f"{minutes}分钟"
    else:
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        if minutes > 0:
            return f"{hours}小时{minutes}分钟"
        return f"{hours}小时"


def format_distance(meters: float) -> str:
    """格式化距离显示"""
    if meters < 1000:
        return f"{int(meters)}米"
    else:
        km = meters / 1000
        return f"{km:.1f}公里"

