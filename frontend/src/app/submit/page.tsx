"use client";

import { useState } from "react";
import { parsePromotion, submitPromotion, Promotion } from "@/lib/api";

export default function SubmitPage() {
  const [content, setContent] = useState("");
  const [parsed, setParsed] = useState<Partial<Promotion> | null>(null);
  const [parsing, setParsing] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [message, setMessage] = useState("");

  const handleParse = async () => {
    if (!content.trim()) return;
    setParsing(true);
    setMessage("");
    try {
      const result = await parsePromotion(content);
      if (result.success) {
        setParsed(result.data);
        setMessage("✅ 解析成功");
      } else {
        setMessage("❌ 解析失败: " + (result.detail || "请检查内容格式"));
      }
    } catch {
      setMessage("❌ 无法连接到后端服务");
    } finally {
      setParsing(false);
    }
  };

  const handleSubmit = async () => {
    if (!parsed) return;
    setSubmitting(true);
    setMessage("");
    try {
      const result = await submitPromotion(parsed);
      if (result.success) {
        setMessage("✅ 提交成功！");
        setParsed(null);
        setContent("");
      } else {
        setMessage("❌ " + (result.message || "提交失败"));
      }
    } catch {
      setMessage("❌ 提交失败");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="max-w-3xl mx-auto px-4 py-8">
      <h1 className="text-2xl font-bold text-gray-900 mb-6">📝 提交新活动</h1>

      <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
        <label className="block text-sm font-medium text-gray-700 mb-2">
          请粘贴活动内容
        </label>
        <textarea
          value={content}
          onChange={(e) => setContent(e.target.value)}
          rows={6}
          placeholder="粘贴银行活动文本、链接或截图描述..."
          className="w-full px-4 py-3 border border-gray-200 rounded-lg text-sm resize-none focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
        />

        <button
          onClick={handleParse}
          disabled={parsing || !content.trim()}
          className="mt-4 px-6 py-2.5 bg-primary-600 text-white rounded-lg text-sm font-medium hover:bg-primary-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          {parsing ? "⏳ 解析中..." : "🤖 AI 解析"}
        </button>

        {message && (
          <p className="mt-3 text-sm">{message}</p>
        )}

        {parsed && (
          <div className="mt-6 border-t border-gray-100 pt-6">
            <h2 className="text-lg font-semibold text-gray-800 mb-4">
              解析结果
            </h2>
            <div className="grid gap-4">
              <div>
                <label className="block text-xs text-gray-500 mb-1">标题</label>
                <input
                  value={parsed.title || ""}
                  onChange={(e) => setParsed({ ...parsed, title: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-primary-500"
                />
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs text-gray-500 mb-1">银行</label>
                  <input
                    value={parsed.bank || ""}
                    onChange={(e) => setParsed({ ...parsed, bank: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-primary-500"
                  />
                </div>
                <div>
                  <label className="block text-xs text-gray-500 mb-1">类型</label>
                  <select
                    value={parsed.promo_type || "其他"}
                    onChange={(e) => setParsed({ ...parsed, promo_type: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm bg-white focus:outline-none focus:ring-2 focus:ring-primary-500"
                  >
                    <option value="返现">返现</option>
                    <option value="折扣">折扣</option>
                    <option value="积分">积分</option>
                    <option value="礼品">礼品</option>
                    <option value="其他">其他</option>
                  </select>
                </div>
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs text-gray-500 mb-1">开始日期</label>
                  <input
                    type="date"
                    value={parsed.start_date || ""}
                    onChange={(e) => setParsed({ ...parsed, start_date: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-primary-500"
                  />
                </div>
                <div>
                  <label className="block text-xs text-gray-500 mb-1">结束日期</label>
                  <input
                    type="date"
                    value={parsed.end_date || ""}
                    onChange={(e) => setParsed({ ...parsed, end_date: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-primary-500"
                  />
                </div>
              </div>
              <div>
                <label className="block text-xs text-gray-500 mb-1">链接</label>
                <input
                  value={parsed.url || ""}
                  onChange={(e) => setParsed({ ...parsed, url: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-primary-500"
                />
              </div>
              <div>
                <label className="block text-xs text-gray-500 mb-1">
                  活动内容
                </label>
                <textarea
                  value={parsed.content || ""}
                  onChange={(e) =>
                    setParsed({ ...parsed, content: e.target.value })
                  }
                  rows={3}
                  className="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm resize-none focus:outline-none focus:ring-2 focus:ring-primary-500"
                />
              </div>
            </div>

            <button
              onClick={handleSubmit}
              disabled={submitting}
              className="mt-4 px-6 py-2.5 bg-green-600 text-white rounded-lg text-sm font-medium hover:bg-green-700 disabled:opacity-50 transition-colors"
            >
              {submitting ? "⏳ 提交中..." : "✅ 确认提交"}
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
