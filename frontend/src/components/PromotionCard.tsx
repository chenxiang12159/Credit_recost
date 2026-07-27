"use client";

import { useState, useEffect, useCallback } from "react";
import { Promotion, proxyImage } from "@/lib/api";

const bankColors: Record<string, string> = {
  "中国农业银行": "bg-green-100 text-green-800",
  "广发银行": "bg-blue-100 text-blue-800",
  "中信银行": "bg-red-100 text-red-800",
  "中国建设银行": "bg-blue-100 text-blue-800",
  "赚客吧": "bg-yellow-100 text-yellow-800",
};

const typeColors: Record<string, string> = {
  返现: "bg-green-100 text-green-700",
  折扣: "bg-orange-100 text-orange-700",
  积分: "bg-purple-100 text-purple-700",
  礼品: "bg-pink-100 text-pink-700",
  其他: "bg-gray-100 text-gray-700",
};

export default function PromotionCard({ promo }: { promo: Promotion }) {
  const [expanded, setExpanded] = useState(false);
  const [selectedImageIdx, setSelectedImageIdx] = useState<number | null>(null);
  const images = promo.images || [];

  const openImage = useCallback((idx: number) => {
    setSelectedImageIdx(idx);
  }, []);

  const closeImage = useCallback(() => {
    setSelectedImageIdx(null);
  }, []);

  const goNext = useCallback(() => {
    if (selectedImageIdx === null || images.length <= 1) return;
    setSelectedImageIdx((selectedImageIdx + 1) % images.length);
  }, [selectedImageIdx, images.length]);

  const goPrev = useCallback(() => {
    if (selectedImageIdx === null || images.length <= 1) return;
    setSelectedImageIdx((selectedImageIdx - 1 + images.length) % images.length);
  }, [selectedImageIdx, images.length]);

  useEffect(() => {
    if (selectedImageIdx === null) return;
    const handler = (e: KeyboardEvent) => {
      if (e.key === "ArrowRight") goNext();
      else if (e.key === "ArrowLeft") goPrev();
      else if (e.key === "Escape") closeImage();
    };
    window.addEventListener("keydown", handler);
    return () => window.removeEventListener("keydown", handler);
  }, [selectedImageIdx, goNext, goPrev, closeImage]);

  const bankClass = bankColors[promo.bank || ""] || "bg-gray-100 text-gray-700";
  const typeClass = typeColors[promo.promo_type || "其他"] || "bg-gray-100 text-gray-700";
  const hasImages = promo.images && promo.images.length > 0;
  const hasContent = promo.content && promo.content.trim().length > 0;

  return (
    <>
      <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-5 hover:shadow-md transition-shadow">
        {/* 标题行 */}
        <div className="flex items-start justify-between gap-3">
          <h3 className="text-base font-semibold text-gray-900 leading-snug flex-1">
            {promo.url ? (
              <a
                href={promo.url}
                target="_blank"
                rel="noopener noreferrer"
                className="hover:text-primary-600 transition-colors"
              >
                {promo.title}
              </a>
            ) : (
              promo.title
            )}
          </h3>
        </div>

        {/* 标签 */}
        <div className="flex flex-wrap gap-2 mt-3">
          {promo.bank && (
            <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${bankClass}`}>
              🏦 {promo.bank}
            </span>
          )}
          {promo.promo_type && (
            <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${typeClass}`}>
              🏷️ {promo.promo_type}
            </span>
          )}
          {promo.source && (
            <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-600">
              📡 {promo.source.replace("_official", "")}
            </span>
          )}
          {promo.author && (
            <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-600">
              👤 {promo.author}
            </span>
          )}
          {promo.rating > 0 && (
            <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
              promo.rating >= 10
                ? "bg-yellow-100 text-yellow-800"
                : "bg-gray-100 text-gray-600"
            }`}>
              ⭐ {promo.rating}分
            </span>
          )}
        </div>

        {/* 时间 */}
        {(promo.start_date || promo.end_date) && (
          <p className="text-sm text-gray-500 mt-3">
            📅 {promo.start_date || "未知"} ~ {promo.end_date || "未知"}
          </p>
        )}

        {/* 内容 */}
        {hasContent && (
          <div className="mt-3">
            <p
              className={`text-sm text-gray-600 whitespace-pre-line ${
                !expanded ? "line-clamp-4" : ""
              }`}
            >
              {promo.content}
            </p>
            {promo.content!.split("\n").length > 4 || promo.content!.length > 200 ? (
              <button
                onClick={() => setExpanded(!expanded)}
                className="text-sm text-primary-600 hover:text-primary-800 mt-1 font-medium"
              >
                {expanded ? "收起" : "展开全部"}
              </button>
            ) : null}
          </div>
        )}

        {/* 图片缩略图 */}
        {hasImages && (
          <div className="flex flex-wrap gap-2 mt-3">
            {promo.images.slice(0, 4).map((img, idx) => (
              <div
                key={idx}
                className="relative w-20 h-20 rounded-lg overflow-hidden cursor-pointer border border-gray-200 hover:border-primary-400 transition-colors"
                onClick={() => openImage(idx)}
              >
                <img
                  src={proxyImage(img)}
                  alt={`图片 ${idx + 1}`}
                  className="w-full h-full object-cover"
                  loading="lazy"
                />
              </div>
            ))}
            {promo.images.length > 4 && (
              <div
                className="w-20 h-20 rounded-lg bg-gray-100 flex items-center justify-center text-xs text-gray-500 cursor-pointer"
                onClick={() => openImage(4)}
              >
                +{promo.images.length - 4}
              </div>
            )}
          </div>
        )}

        {/* 链接 */}
        {promo.url && (
          <div className="mt-3">
            <a
              href={promo.url}
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center text-sm text-primary-600 hover:text-primary-800 font-medium"
            >
              🔗 查看详情 →
            </a>
          </div>
        )}
      </div>

      {/* 图片弹窗 */}
      {selectedImageIdx !== null && images[selectedImageIdx] && (
        <div
          className="fixed inset-0 bg-black/70 z-50 flex items-center justify-center p-4"
          onClick={closeImage}
        >
          <div
            className="relative max-w-4xl max-h-[90vh]"
            onClick={(e) => e.stopPropagation()}
          >
            <img
              src={proxyImage(images[selectedImageIdx])}
              alt={`图片 ${selectedImageIdx + 1}`}
              className="max-w-full max-h-[85vh] object-contain rounded-lg"
            />

            {/* 关闭按钮 */}
            <button
              className="absolute top-2 right-2 w-8 h-8 bg-black/50 text-white rounded-full flex items-center justify-center hover:bg-black/70"
              onClick={closeImage}
            >
              ✕
            </button>

            {/* 图片计数 */}
            {images.length > 1 && (
              <div className="absolute top-2 left-1/2 -translate-x-1/2 px-3 py-1 bg-black/50 text-white text-sm rounded-full">
                {selectedImageIdx + 1} / {images.length}
              </div>
            )}

            {/* 左箭头 */}
            {images.length > 1 && (
              <button
                className="absolute left-2 top-1/2 -translate-y-1/2 w-10 h-10 bg-black/50 text-white rounded-full flex items-center justify-center hover:bg-black/70 text-xl"
                onClick={goPrev}
              >
                ‹
              </button>
            )}

            {/* 右箭头 */}
            {images.length > 1 && (
              <button
                className="absolute right-2 top-1/2 -translate-y-1/2 w-10 h-10 bg-black/50 text-white rounded-full flex items-center justify-center hover:bg-black/70 text-xl"
                onClick={goNext}
              >
                ›
              </button>
            )}
          </div>
        </div>
      )}
    </>
  );
}
