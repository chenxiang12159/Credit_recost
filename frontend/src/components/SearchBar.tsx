"use client";

interface SearchBarProps {
  keyword: string;
  onKeywordChange: (v: string) => void;
  bank: string;
  onBankChange: (v: string) => void;
  type: string;
  onTypeChange: (v: string) => void;
  onRefresh: () => void;
  isRefreshing: boolean;
}

const banks = [
  "全部银行",
  "中国农业银行",
  "中国工商银行",
  "广发银行",
  "中国银行",
  "中信银行",
  "中国建设银行",
  "赚客吧",
];

const types = ["全部类型", "返现", "折扣", "积分", "礼品", "其他"];

export default function SearchBar({
  keyword,
  onKeywordChange,
  bank,
  onBankChange,
  type,
  onTypeChange,
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
    </div>
  );
}
