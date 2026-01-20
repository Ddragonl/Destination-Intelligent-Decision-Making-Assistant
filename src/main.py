"""
主程序入口 - MCP服务
"""
import json
import sys
from typing import Dict, Any
from src.mcp.mcp_client import MCPClient


def main():
    """主函数"""
    if len(sys.argv) < 3:
        print("用法: python main.py <用户位置> <连锁店名称> [城市] [交通方式]")
        print("示例: python main.py '浙江大学紫金港校区' '联想电脑专卖店' '杭州' 'transit'")
        sys.exit(1)
    
    user_location = sys.argv[1]
    store_name = sys.argv[2]
    city = sys.argv[3] if len(sys.argv) > 3 else "杭州"
    preferred_mode = sys.argv[4] if len(sys.argv) > 4 else None
    
    # 创建MCP客户端
    try:
        client = MCPClient()
        
        # 处理请求
        result = client.process_request(
            user_location_str=user_location,
            store_name=store_name,
            city=city,
            preferred_mode=preferred_mode
        )
        
        # 输出结果
        if result.get("success"):
            print("\n" + "="*60)
            print("目的地自主决策智能体 - 推荐结果")
            print("="*60 + "\n")
            
            rec = result["recommendation"]
            route = rec["route"]
            
            print(f"📍 推荐目的地：{rec['destination']['name']}")
            print(f"   地址：{rec['destination']['address']}")
            print(f"\n🚌 交通方案：{route['traffic_mode_cn']}")
            print(f"   预计时间：{route['duration_formatted']}")
            print(f"   距离：{route['distance_formatted']}")
            if route.get("cost"):
                print(f"   费用：{route['cost']}元")
            
            if route.get("details"):
                print(f"\n📋 详细路线：")
                for i, detail in enumerate(route["details"], 1):
                    if detail.get("type") == "walking":
                        print(f"   {i}. {detail['instruction']}")
                    elif detail.get("type") == "bus":
                        print(f"   {i}. {detail['instruction']}")
                        print(f"      从 {detail['departure']} 到 {detail['arrival']}")
                    elif detail.get("type") == "subway":
                        print(f"   {i}. {detail['instruction']}")
                        print(f"      从 {detail['departure']} 到 {detail['arrival']}")
                    else:
                        print(f"   {i}. {detail.get('instruction', '')}")
            
            if result.get("alternatives"):
                print(f"\n🔄 备选方案：")
                for i, alt in enumerate(result["alternatives"], 1):
                    print(f"   {i}. {alt['destination']} - {alt['traffic_mode']} - {alt['duration']}")
            
            print(f"\n📊 共查询了 {result['all_stores_found']} 家门店")
            print("\n" + "="*60)
            
            # 同时输出JSON格式（用于程序调用）
            print("\nJSON格式结果：")
            print(json.dumps(result, ensure_ascii=False, indent=2))
        else:
            print(f"❌ 错误：{result.get('error', '未知错误')}")
            sys.exit(1)
            
    except Exception as e:
        print(f"❌ 程序错误：{str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

