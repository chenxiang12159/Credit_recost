"use client";

interface SearchBarProps {
  keyword: string;
  onKeywordChange: (v: string) => void;
  bank: string;
  onBankChange: (v: string) => void;
  type: string;
  onTypeChange: (v: string) => void;
  sort: string;
  onSortChange: (v: string) => void;
  onRefresh: () => void;
  isRefreshing: boolean;
}

const banks = [
  "全部银行",
  "中国农业银行",
  "广发银行",
  "中信银行",
  "中国建设银行",
  "赚客吧",
];

const types = ["全部类型", "返现", "折扣", "积分", "礼品", "其他"];

const sorts = [
  { value: "comprehensive", label: "综合排序", icon: "📊" },
  { value: "rating", label: "评分优先", icon: "⭐" },
  { value: "time", label: "时间优先", icon: "🕐" },
];

export default function SearchBar({
  keyword,
  onKeywordChange,
  bank,
  onBankChange,
  type,
  onTypeChange,
  sort,
  onSortChange,
  onRefresh,
  isRefreshing,
}: SearchBarProps) {
  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-4 mb-6">
      <div className="flex flex-col sm:flex-row gap-3">
        <input
          type="text"
          placeholder="🔍 搜索活动..."
          value={keyword}
          onChange={(e) => onKeywordChange(e.target.value)}
          className="flex-1 px-4 py-2 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
        />
        <select
          value={bank}
          onChange={(e) => onBankChange(e.target.value)}
          className="px-3 py-2 border border-gray-200 rounded-lg text-sm bg-white focus:outline-none focus:ring-2 focus:ring-primary-500"
        >
          {banks.map((b) => (
            <option key={b} value={b === "全部银行" ? "" : b}>
              {b}
            </option>
          ))}
        </select>
        <select
          value={type}
          onChange={(e) => onTypeChange(e.target.value)}
          className="px-3 py-2 border border-gray-200 rounded-lg text-sm bg-white focus:outline-none focus:ring-2 focus:ring-primary-500"
        >
          {types.map((t) => (
            <option key={t} value={t === "全部类型" ? "" : t}>
              {t}
            </option>
          ))}
        </select>
        <button
          onClick={onRefresh}
          disabled={isRefreshing}
          className="px-4 py-2 bg-primary-600 text-white rounded-lg text-sm font-medium hover:bg-primary-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors whitespace-nowrap"
        >
          {isRefreshing ? "⏳ 爬取中..." : "🔄 刷新"}
        </button>
      </div>

      {/* 排序按钮 */}
      <div className="flex gap-2 mt-3">
        {sorts.map((s) => (
          <button
            key={s.value}
            onClick={() => onSortChange(s.value)}
            className={`px-3 py-1.5 rounded-full text-xs font-medium transition-colors ${
              sort === s.value
                ? "bg-primary-600 text-white"
                : "bg-gray-100 text-gray-600 hover:bg-gray-200"
            }`}
          >
            {s.icon} {s.label}
          </button>
        ))}
      </div>
    </div>
  );
}
