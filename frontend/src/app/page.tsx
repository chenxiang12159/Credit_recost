"use client";

import { useState, useEffect, useCallback } from "react";
import {
  fetchPromotions,
  triggerCrawl,
  Promotion,
  Pagination,
} from "@/lib/api";
import PromotionList from "@/components/PromotionList";
import Toast from "@/components/Toast";

const AUTO_REFRESH_INTERVAL = 5 * 60 * 1000;

export default function Home() {
  const [promotions, setPromotions] = useState<Promotion[]>([]);
  const [pagination, setPagination] = useState<Pagination>({
    total: 0,
    page: 1,
    page_size: 20,
    total_pages: 1,
  });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [toast, setToast] = useState({
    show: false,
    message: "",
    type: "info" as "success" | "info" | "error",
  });

  const [fetchParams, setFetchParams] = useState<{
    page: number;
    keyword?: string;
    bank?: string;
    promo_type?: string;
  }>({ page: 1 });

  const loadPromotions = useCallback(
    async (params?: typeof fetchParams) => {
      const p = params || fetchParams;
      try {
        const res = await fetchPromotions({ ...p, page_size: 20 });
        if (res.success) {
          setPromotions(res.data);
          setPagination(res.pagination);
          setError("");
        }
      } catch {
        setError("无法连接到后端服务，请确保后端已启动 (localhost:8080)");
      }
    },
    [fetchParams]
  );

  useEffect(() => {
    async function init() {
      await loadPromotions({ page: 1 });
      setLoading(false);
    }
    init();
  }, []);

  const showToast = useCallback(
    (message: string, type: "success" | "info" | "error") => {
      setToast({ show: true, message, type });
    },
    []
  );

  const handleToastDone = useCallback(() => {
    setToast((prev) => ({ ...prev, show: false }));
  }, []);

  const doCrawl = useCallback(
    async (silent = false) => {
      if (!silent) setIsRefreshing(true);
      try {
        const result = await triggerCrawl();
        if (result.has_new) {
          await loadPromotions({ page: 1 });
          if (!silent) {
            showToast(`✅ 已更新 ${result.saved_count} 条新活动`, "success");
          } else {
            showToast(`🔄 自动更新 ${result.saved_count} 条新活动`, "success");
          }
        } else if (!silent) {
          showToast("ℹ️ 已是最新的消息", "info");
        }
      } catch {
        if (!silent) {
          showToast("❌ 爬取失败，请检查后端服务", "error");
        }
      } finally {
        if (!silent) setIsRefreshing(false);
      }
    },
    [loadPromotions, showToast]
  );

  useEffect(() => {
    const timer = setInterval(() => doCrawl(true), AUTO_REFRESH_INTERVAL);
    return () => clearInterval(timer);
  }, [doCrawl]);

  const handleRefresh = () => {
    if (!isRefreshing) doCrawl(false);
  };

  const handleFetch = useCallback(
    (params: typeof fetchParams) => {
      setFetchParams(params);
      loadPromotions(params);
    },
    [loadPromotions]
  );

  return (
    <div className="max-w-6xl mx-auto px-4 py-8">
      <Toast
        show={toast.show}
        message={toast.message}
        type={toast.type}
        onDone={handleToastDone}
      />

      {loading ? (
        <div className="text-center py-16">
          <p className="text-4xl mb-4 animate-spin inline-block">⏳</p>
          <p className="text-gray-500">加载中...</p>
        </div>
      ) : error ? (
        <div className="text-center py-16">
          <p className="text-4xl mb-4">⚠️</p>
          <p className="text-red-500">{error}</p>
          <p className="text-sm text-gray-400 mt-2">
            运行命令: cd backend &amp;&amp; uvicorn app.api:app --reload --port
            8080
          </p>
        </div>
      ) : (
        <PromotionList
          initialPromotions={promotions}
          initialPagination={pagination}
          onFetch={handleFetch}
          onRefresh={handleRefresh}
          isRefreshing={isRefreshing}
        />
      )}
    </div>
  );
}
