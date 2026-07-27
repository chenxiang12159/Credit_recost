"""CLI 工具 - 手动提交活动"""
import asyncio
import json
from app.database import init_db, SessionLocal
from app.crud import create_promotion, is_duplicate
from app.ai_parser import parser
from app.telegram_push import pusher


def main():
    """主函数"""
    print("=" * 50)
    print("银行活动聚合 - CLI 工具")
    print("=" * 50)
    
    # 初始化数据库
    init_db()
    
    while True:
        print("\n功能菜单：")
        print("1. AI 解析并提交活动")
        print("2. 手动提交活动")
        print("3. 查看最新活动")
        print("4. 退出")
        
        choice = input("\n请选择功能 (1-4): ").strip()
        
        if choice == '1':
            parse_and_submit()
        elif choice == '2':
            manual_submit()
        elif choice == '3':
            list_latest()
        elif choice == '4':
            print("再见！")
            break
        else:
            print("无效选择，请重试")


def parse_and_submit():
    """AI 解析并提交活动"""
    print("\n请粘贴活动内容（输入 END 结束）：")
    lines = []
    while True:
        line = input()
        if line.strip() == 'END':
            break
        lines.append(line)
    
    content = '\n'.join(lines)
    
    if not content.strip():
        print("内容为空，取消操作")
        return
    
    print("\n正在解析内容...")
    promo_data = asyncio.run(parser.extract_promotion(content))
    
    if not promo_data:
        print("解析失败，请检查内容格式")
        return
    
    print("\n解析结果：")
    print(json.dumps(promo_data, ensure_ascii=False, indent=2))
    
    confirm = input("\n确认提交？(y/n): ").strip().lower()
    if confirm != 'y':
        print("取消提交")
        return
    
    # 保存到数据库
    db = SessionLocal()
    try:
        if is_duplicate(db, promo_data):
            print("活动已存在，跳过")
            return
        
        promotion = create_promotion(db, promo_data)
        print(f"活动已保存: {promotion.uuid}")
        
        # 推送到 Telegram
        print("正在推送到 Telegram...")
        push_success = asyncio.run(pusher.send_promotion(promo_data))
        if push_success:
            print("推送成功！")
        else:
            print("推送失败，请检查 Telegram 配置")
    finally:
        db.close()


def manual_submit():
    """手动提交活动"""
    print("\n请输入活动信息：")
    
    title = input("标题: ").strip()
    if not title:
        print("标题不能为空")
        return
    
    bank = input("银行/平台: ").strip()
    promo_type = input("类型 (返现/折扣/积分/礼品): ").strip()
    start_date = input("开始日期 (YYYY-MM-DD): ").strip()
    end_date = input("结束日期 (YYYY-MM-DD): ").strip()
    content = input("活动内容: ").strip()
    url = input("参与链接: ").strip()
    qrcode_url = input("二维码URL (可选): ").strip()
    
    promo_data = {
        "title": title,
        "bank": bank if bank else None,
        "promo_type": promo_type if promo_type else None,
        "start_date": start_date if start_date else None,
        "end_date": end_date if end_date else None,
        "content": content if content else None,
        "url": url if url else None,
        "qrcode_url": qrcode_url if qrcode_url else None,
        "source": "manual"
    }
    
    # 保存到数据库
    db = SessionLocal()
    try:
        if is_duplicate(db, promo_data):
            print("活动已存在，跳过")
            return
        
        promotion = create_promotion(db, promo_data)
        print(f"活动已保存: {promotion.uuid}")
        
        # 推送到 Telegram
        print("正在推送到 Telegram...")
        push_success = asyncio.run(pusher.send_promotion(promo_data))
        if push_success:
            print("推送成功！")
        else:
            print("推送失败，请检查 Telegram 配置")
    finally:
        db.close()


def list_latest():
    """查看最新活动"""
    from app.crud import get_latest_promotions
    
    db = SessionLocal()
    try:
        promotions = get_latest_promotions(db, 10)
        if not promotions:
            print("暂无活动")
            return
        
        print("\n最新活动：")
        print("-" * 50)
        for p in promotions:
            print(f"标题: {p.title}")
            print(f"银行: {p.bank or '未知'}")
            print(f"类型: {p.promo_type or '未知'}")
            print(f"时间: {p.start_date} ~ {p.end_date}")
            print(f"来源: {p.source}")
            print("-" * 50)
    finally:
        db.close()


if __name__ == "__main__":
    main()
