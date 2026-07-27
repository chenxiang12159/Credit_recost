"use client";

import { useState, useEffect } from "react";
import {
  fetchXhsCandidates,
  generateXhsDraft,
  proxyImage,
  XhsCandidate,
} from "@/lib/api";

export default function XhsPage() {
  const [candidates, setCandidates] = useState<XhsCandidate[]>([]);
  const [loading, setLoading] = useState(true);
  const [draftUuid, setDraftUuid] = useState<string | null>(null);
  const [draft, setDraft] = useState("");
  const [draftImages, setDraftImages] = useState<string[]>([]);
  const [generating, setGenerating] = useState(false);
  const [error, setError] = useState("");

  const load = async () => {
    setLoading(true);
    const data = await fetchXhsCandidates(30);
    setCandidates(data);
    setLoading(false);
  };

  useEffect(() => {
    load();
  }, []);

  const handleGenerate = async (uuid: string) => {
    setGenerating(true);
    setDraftUuid(uuid);
    setError("");
    setDraft("");
    const res = await generateXhsDraft(uuid);
    if (res.success && res.draft) {
      setDraft(res.draft);
      setDraftImages(res.images || []);
    } else {
      setError(res.message || "生成失败");
    }
    setGenerating(false);
  };

  return (
    <div className="max-w-6xl mx-auto px-4 py-8">
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold text-gray-900">📕 小红书草稿助手</h1>
        <button
          onClick={load}
          className="px-4 py-2 bg-primary-600 text-white rounded-lg text-sm font-medium hover:bg-primary-700"
        >
          🔄 重新筛选
        </button>
      </div>

      <p className="text-sm text-gray-500 mb-6">
        筛选规则：时效≤1天免评分；&gt;1天需评分≥5；优先带图。AI 已初筛，你只需验证能否发布。
      </p>

      {loading ? (
        <p className="text-center text-gray-400 py-16">加载中...</p>
      ) : candidates.length === 0 ? (
        <p className="text-center text-gray-400 py-16">暂无符合条件的候选</p>
      ) : (
        <div className="grid lg:grid-cols-2 gap-6">
          {/* 候选列表 */}
          <div className="space-y-3">
            <h2 className="font-semibold text-gray-700">
              候选帖子（{candidates.length}）
            </h2>
            {candidates.map((c) => (
              <div
                key={c.uuid}
                className={`bg-white rounded-xl border p-4 cursor-pointer transition-colors ${
                  draftUuid === c.uuid
                    ? "border-primary-500 ring-1 ring-primary-300"
                    : "border-gray-100 hover:border-gray-300"
                }`}
                onClick={() => handleGenerate(c.uuid)}
              >
                <div className="flex items-start justify-between gap-2">
                  <h3 className="font-medium text-gray-900 text-sm leading-snug">
                    {c.title}
                  </h3>
                  <span className="text-xs text-gray-400 whitespace-nowrap">
                    {c.age_days <= 0 ? "今天" : `${c.age_days}天前`}
                  </span>
                </div>
                <div className="flex flex-wrap gap-2 mt-2">
                  {c.bank && (
                    <span className="text-xs bg-blue-100 text-blue-700 px-2 py-0.5 rounded-full">
                      {c.bank}
                    </span>
                  )}
                  {c.rating > 0 && (
                    <span className="text-xs bg-yellow-100 text-yellow-800 px-2 py-0.5 rounded-full">
                      ⭐{c.rating}
                    </span>
                  )}
                  {c.has_img && (
                    <span className="text-xs bg-green-100 text-green-700 px-2 py-0.5 rounded-full">
                      🖼️带图
                    </span>
                  )}
                </div>
              </div>
            ))}
          </div>

          {/* 草稿预览 */}
          <div className="lg:sticky lg:top-8">
            <div className="bg-white rounded-xl border border-gray-100 p-5 min-h-[400px]">
              <h2 className="font-semibold text-gray-700 mb-3">📝 草稿预览</h2>
              {generating && (
                <p className="text-gray-400 text-sm">AI 生成中...</p>
              )}
              {error && (
                <p className="text-red-500 text-sm">{error}</p>
              )}
              {!generating && draft && (
                <>
                  <pre className="whitespace-pre-wrap text-sm text-gray-800 leading-relaxed font-sans">
                    {draft}
                  </pre>
                  {draftImages.length > 0 && (
                    <div className="mt-4">
                      <p className="text-xs text-gray-500 mb-2">配图：</p>
                      <div className="flex flex-wrap gap-2">
                        {draftImages.slice(0, 4).map((img, i) => (
                          <img
                            key={i}
                            src={proxyImage(img)}
                            alt={`图${i + 1}`}
                            className="w-20 h-20 object-cover rounded-lg border"
                          />
                        ))}
                      </div>
                    </div>
                  )}
                  <button
                    onClick={() => navigator.clipboard.writeText(draft)}
                    className="mt-4 px-3 py-1.5 bg-gray-100 text-gray-700 rounded-lg text-sm hover:bg-gray-200"
                  >
                    📋 复制文案
                  </button>
                </>
              )}
              {!generating && !draft && !error && (
                <p className="text-gray-300 text-sm">← 点击左侧候选生成草稿</p>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
