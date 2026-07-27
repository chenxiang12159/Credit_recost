"""图片水印模块 - 配置化，可随时修改"""
import logging
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

logger = logging.getLogger(__name__)

# ========== 水印配置（改这里就行） ==========
WATERMARK_CONFIG = {
    "text": "我爱说实话 羊毛版",      # 水印文字
    "font_size_ratio": 0.05,        # 字号 = 图片宽度 × 这个比例
    "opacity": 180,                  # 透明度 0-255（0=全透明，255=不透明）
    "margin": 15,                    # 距右边和下边的距离（像素）
    "position": "top_right",         # 位置：bottom_right / bottom_left / top_right / top_left / center
}
# =============================================

FONT_PATH = "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"


def _get_font(size: int) -> ImageFont.FreeTypeFont:
    try:
        return ImageFont.truetype(FONT_PATH, size)
    except (OSError, IOError):
        for fallback in [
            "/usr/share/fonts/truetype/arphic/uming.ttc",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        ]:
            try:
                return ImageFont.truetype(fallback, size)
            except (OSError, IOError):
                continue
        return ImageFont.load_default()


def _get_position(img_w: int, img_h: int, text_w: int, text_h: int) -> tuple[int, int]:
    pos = WATERMARK_CONFIG["position"]
    m = WATERMARK_CONFIG["margin"]

    if pos == "bottom_right":
        return img_w - text_w - m, img_h - text_h - m
    elif pos == "bottom_left":
        return m, img_h - text_h - m
    elif pos == "top_right":
        return img_w - text_w - m, m
    elif pos == "top_left":
        return m, m
    else:
        return (img_w - text_w) // 2, (img_h - text_h) // 2


def add_watermark(img: Image.Image) -> Image.Image:
    """给图片叠加水印，返回新图片"""
    cfg = WATERMARK_CONFIG
    if not cfg.get("text"):
        return img

    img = img.convert("RGBA")
    overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    font_size = max(12, int(img.width * cfg["font_size_ratio"]))
    font = _get_font(font_size)

    bbox = draw.textbbox((0, 0), cfg["text"], font=font)
    text_w = bbox[2] - bbox[0]
    text_h = bbox[3] - bbox[1]

    x, y = _get_position(img.width, img.height, text_w, text_h)

    draw.text(
        (x, y),
        cfg["text"],
        font=font,
        fill=(0, 0, 0, cfg["opacity"]),
    )

    result = Image.alpha_composite(img, overlay)
    return result.convert("RGB")


def apply_watermark_to_bytes(image_bytes: bytes) -> bytes:
    """接收图片字节，叠加水印后返回字节"""
    from io import BytesIO

    try:
        img = Image.open(BytesIO(image_bytes))
        if img.mode == "P":
            img = img.convert("RGBA")
        result = add_watermark(img)
        buf = BytesIO()
        result.save(buf, format="JPEG", quality=92)
        return buf.getvalue()
    except Exception as e:
        logger.warning(f"水印处理失败，返回原图: {e}")
        return image_bytes
