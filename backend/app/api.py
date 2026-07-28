"""API 接口模块"""
import asyncio
from dotenv import load_dotenv
load_dotenv()
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
from datetime import date
from sqlalchemy.orm import Session

from .database import init_db, get_db
from .crud import create_promotion, is_duplicate, get_latest_promotions, get_db_stats, get_paginated_promotions, get_xhs_candidates, get_promotion_by_uuid
from .ai_parser import parser
from .telegram_push import pusher
from .spiders.spider_manager import spider_manager
from .image_cache import router as image_router

app = FastAPI(title="银行活动聚合 API")

app.include_router(image_router)

# 允许前端跨域访问
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup():
    """启动时初始化数据库"""
    init_db()


class PromotionSubmit(BaseModel):
    """活动提交请求"""
    content: str  # 原始内容（用户手动复制）


class PromotionResponse(BaseModel):
    """活动响应"""
    uuid: str
    title: str
    bank: Optional[str]
    promo_type: Optional[str]
    start_date: Optional[date]
    end_date: Optional[date]
    content: Optional[str]
    url: Optional[str]
    qrcode_url: Optional[str]
    source: str


@app.post("/api/promotions/parse")
async def parse_promotion(submit: PromotionSubmit, db: Session = Depends(get_db)):
    """解析用户提交的内容"""
    # 调用 AI 解析
    promo_data = await parser.extract_promotion(submit.content)
    
    if not promo_data:
        raise HTTPException(status_code=400, detail="内容解析失败，请检查内容格式")
    
    return {
        "success": True,
        "data": promo_data
    }


@app.post("/api/promotions/submit")
async def submit_promotion(promo_data: dict, db: Session = Depends(get_db)):
    """提交活动并推送"""
    # 检查是否重复
    if is_duplicate(db, promo_data):
        return {
            "success": False,
            "message": "活动已存在"
        }
    
    # 保存到数据库
    promotion = create_promotion(db, promo_data)
    
    # 推送到 Telegram
    push_success = await pusher.send_promotion(promo_data)
    
    return {
        "success": True,
        "promotion_id": promotion.uuid,
        "push_status": "success" if push_success else "failed"
    }


@app.get("/api/promotions/latest")
async def list_latest(
    limit: int = 20,
    page: int = 1,
    page_size: int = 20,
    keyword: str = None,
    bank: str = None,
    promo_type: str = None,
    sort: str = "comprehensive",
    db: Session = Depends(get_db),
):
    """获取最新活动列表（支持分页、筛选和排序）"""
    import json

    result = get_paginated_promotions(
        db, page=page, page_size=page_size,
        keyword=keyword, bank=bank, promo_type=promo_type, sort=sort,
    )

    return {
        "success": True,
        "data": [
            {
                "uuid": p.uuid,
                "title": p.title,
                "bank": p.bank,
                "promo_type": p.promo_type,
                "start_date": str(p.start_date) if p.start_date else None,
                "end_date": str(p.end_date) if p.end_date else None,
                "content": p.content,
                "images": json.loads(p.images) if p.images else [],
                "author": p.author,
                "rating": p.rating or 0,
                "url": p.url,
                "qrcode_url": p.qrcode_url,
                "source": p.source,
            }
            for p in result["items"]
        ],
        "pagination": {
            "total": result["total"],
            "page": result["page"],
            "page_size": result["page_size"],
            "total_pages": result["total_pages"],
        },
    }


@app.post("/api/promotions/manual")
async def manual_submit(promo_data: dict, db: Session = Depends(get_db)):
    """手动提交活动（跳过 AI 解析）"""
    # 检查是否重复
    if is_duplicate(db, promo_data):
        return {
            "success": False,
            "message": "活动已存在"
        }
    
    # 设置来源
    promo_data['source'] = 'manual'
    
    # 保存到数据库
    promotion = create_promotion(db, promo_data)
    
    # 推送到 Telegram
    push_success = await pusher.send_promotion(promo_data)
    
    return {
        "success": True,
        "promotion_id": promotion.uuid,
        "push_status": "success" if push_success else "failed"
    }


@app.post("/api/crawl-and-refresh")
async def crawl_and_refresh(db: Session = Depends(get_db)):
    """执行爬虫并对比差异，返回结果"""
    # 1. 爬取前快照
    before = get_db_stats(db)
    
    # 2. 执行所有爬虫
    try:
        activities = await spider_manager.crawl_all()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"爬取失败: {str(e)}")
    
    # 3. 保存新数据
    saved_count = 0
    for act in activities:
        if not is_duplicate(db, act):
            create_promotion(db, act)
            saved_count += 1
    
    # 4. 爬取后快照
    after = get_db_stats(db)
    
    # 5. 对比差异
    has_new = after["count"] > before["count"] or after["latest"] != before["latest"]
    
    return {
        "success": True,
        "has_new": has_new,
        "saved_count": saved_count,
        "total_count": after["count"],
        "message": f"新增 {saved_count} 条活动" if saved_count > 0 else "已是最新的消息"
    }


@app.get("/api/xhs/candidates")
async def xhs_candidates(limit: int = 20, db: Session = Depends(get_db)):
    """小红书草稿候选列表（按时效+评分+带图规则筛选）"""
    import json
    cands = get_xhs_candidates(db, limit=limit)
    return {
        "success": True,
        "data": [
            {
                "uuid": c["promo"].uuid,
                "title": c["promo"].title,
                "bank": c["promo"].bank,
                "rating": c["promo"].rating or 0,
                "age_days": c["age_days"],
                "has_img": c["has_img"],
                "images": json.loads(c["promo"].images) if c["promo"].images else [],
                "content": c["promo"].content,
                "url": c["promo"].url,
                "author": c["promo"].author,
            }
            for c in cands
        ],
    }


class DraftRequest(BaseModel):
    uuid: str


@app.post("/api/xhs/draft")
async def xhs_draft(req: DraftRequest, db: Session = Depends(get_db)):
    """根据帖子生成小红书草稿文案"""
    promo = get_promotion_by_uuid(db, req.uuid)
    if not promo:
        raise HTTPException(status_code=404, detail="帖子不存在")

    import json
    images = json.loads(promo.images) if promo.images else []

    prompt = f"""你是一个小红书优惠羊毛博主。请把下面的银行/平台优惠活动，改写成一篇**原创的小红书推文草稿**。

【风格要求——参考真实羊毛博主习惯，但必须原创，禁止抄袭任何已有文案】
1. 标题结构：「银行/平台名 + 具体金额/优惠 + 品类 + 钩子词」
   - 例：「工行1.88立减金」「中行10元话费，人人有」「7月乘车优惠合集」
   - 用「人人有」强调无门槛；用「合集/一篇汇总/查漏补缺」做汇总类；带月份/日期强调时效
   - 不超过22字，可加1个emoji
2. 正文结构：「路径式操作步骤 + 短句碎片化」
   - 写清在哪领：如「打开XX银行APP → 我的 → 任务中心 → 每月福利」
   - 口语化、直接、像朋友安利，不写长文案
   - 强调时效（X月/X日截止）
3. 标签：6-8个，如 #信用卡优惠 #羊毛 #银行活动 #立减金 #话费优惠 #建行生活
4. 配图建议：说明用哪张图（若有）
5. 原创声明：基于下面「原始信息」的事实生成，不复制任何他人文案

原始信息：
标题：{promo.title}
银行/平台：{promo.bank}
评分：{promo.rating or 0}
内容：{promo.content or '无'}
参与链接：{promo.url or '无'}

请直接输出可复制的小红书草稿（标题/正文/标签/配图建议分开）。"""

    try:
        async with __import__("httpx").AsyncClient(timeout=60.0) as client:
            resp = await client.post(
                parser.api_url,
                headers={"Authorization": f"Bearer {parser.api_key}", "Content-Type": "application/json"},
                json={
                    "model": parser.model,
                    "messages": [
                        {"role": "system", "content": "你是小红书爆款文案专家，输出直接可用的草稿。"},
                        {"role": "user", "content": prompt},
                    ],
                    "temperature": 0.7,
                },
            )
            if resp.status_code == 200:
                draft = resp.json()["choices"][0]["message"]["content"]
                return {"success": True, "draft": draft, "images": images}
            else:
                return {"success": False, "message": f"AI调用失败: {resp.status_code}"}
    except Exception as e:
        return {"success": False, "message": f"异常: {str(e)}"}
