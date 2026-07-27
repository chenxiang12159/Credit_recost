"""图片缓存代理模块"""
import hashlib
import os
import time
import logging
import httpx
from pathlib import Path
from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import FileResponse

logger = logging.getLogger(__name__)

router = APIRouter()

CACHE_DIR = Path(__file__).parent.parent / "data" / "image_cache"
MAX_CACHE_SIZE = 5 * 1024 * 1024 * 1024  # 5GB

ALLOWED_HOSTS = ["img.zuanke8.cn"]


def _url_to_filename(url: str) -> str:
    """URL → MD5 哈希作为文件名"""
    ext = ".jpg"
    for e in [".png", ".gif", ".webp", ".bmp", ".jpeg"]:
        if e in url.lower():
            ext = e
            break
    return hashlib.md5(url.encode()).hexdigest() + ext


def _ensure_cache_dir():
    CACHE_DIR.mkdir(parents=True, exist_ok=True)


def _cache_size() -> int:
    total = 0
    for f in CACHE_DIR.iterdir():
        if f.is_file():
            total += f.stat().st_size
    return total


def _evict_if_needed():
    """缓存超过5GB时，删除最旧的文件"""
    current = _cache_size()
    if current <= MAX_CACHE_SIZE:
        return

    files = sorted(CACHE_DIR.iterdir(), key=lambda f: f.stat().st_mtime)
    for f in files:
        if current <= MAX_CACHE_SIZE * 0.8:
            break
        if f.is_file():
            size = f.stat().st_size
            f.unlink()
            current -= size
            logger.info(f"缓存清理: 删除 {f.name} ({size} bytes)")


async def fetch_and_cache(url: str) -> Path:
    """下载图片，叠加水印后缓存，返回本地文件路径"""
    _ensure_cache_dir()

    filename = _url_to_filename(url)
    cache_path = CACHE_DIR / filename

    if cache_path.exists():
        return cache_path

    from .watermark import apply_watermark_to_bytes

    async with httpx.AsyncClient(timeout=15, verify=False, follow_redirects=True) as client:
        resp = await client.get(url)
        resp.raise_for_status()

        processed = apply_watermark_to_bytes(resp.content)
        cache_path.write_bytes(processed)
        logger.info(f"图片缓存+水印: {url[:60]}... → {filename} ({len(processed)} bytes)")

        _evict_if_needed()

    return cache_path


@router.get("/api/image-proxy")
async def image_proxy(url: str = Query(..., description="图片原始URL")):
    """图片代理：缓存远程图片并返回本地缓存版本"""
    if not any(h in url for h in ALLOWED_HOSTS):
        raise HTTPException(status_code=400, detail="不支持的图片域名")

    try:
        cache_path = await fetch_and_cache(url)
        return FileResponse(
            path=str(cache_path),
            media_type="image/jpeg",
            headers={"Cache-Control": "public, max-age=2592000"},
        )
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=502, detail=f"原图请求失败: {e.response.status_code}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"图片缓存失败: {str(e)}")
