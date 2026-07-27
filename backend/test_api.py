"""API 测试脚本"""
import httpx
import json

BASE_URL = "http://localhost:8000"


def test_health():
    """测试健康检查"""
    print("测试健康检查...")
    # 这个接口可以自己添加


def test_parse():
    """测试解析接口"""
    print("\n测试解析接口...")
    
    test_content = """
    中国农业银行信用卡活动：
    活动时间：2024年1月1日 - 2024年12月31日
    活动内容：使用农行信用卡在指定商户消费，满100返现20元
    每日限前1000名，先到先得
    参与链接：https://abc.example.com/activity
    """
    
    try:
        response = httpx.post(
            f"{BASE_URL}/api/promotions/parse",
            json={"content": test_content}
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ 解析成功")
            print(json.dumps(result, ensure_ascii=False, indent=2))
        else:
            print(f"❌ 解析失败: {response.status_code}")
            print(response.text)
    except Exception as e:
        print(f"❌ 请求异常: {e}")


def test_list_latest():
    """测试获取最新活动"""
    print("\n测试获取最新活动...")
    
    try:
        response = httpx.get(
            f"{BASE_URL}/api/promotions/latest",
            params={"limit": 5}
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ 获取成功")
            print(f"共 {len(result.get('data', []))} 条活动")
        else:
            print(f"❌ 获取失败: {response.status_code}")
    except Exception as e:
        print(f"❌ 请求异常: {e}")


if __name__ == "__main__":
    print("=" * 50)
    print("银行活动聚合 - API 测试")
    print("=" * 50)
    
    test_parse()
    test_list_latest()
    
    print("\n测试完成！")
