"use client";

import { useState, useCallback } from "react";
import { Promotion, Pagination as PaginationType } from "@/lib/api";
import PromotionCard from "./PromotionCard";
import SearchBar from "./SearchBar";
import Pagination from "./Pagination";

const PAGE_SIZE = 20;

export default function PromotionList({
  initialPromotions,
  initialPagination,
  onFetch,
  onRefresh,
  isRefreshing,
}: {
  initialPromotions: Promotion[];
  initialPagination: PaginationType;
  onFetch: (params: {
    page: number;
    keyword?: string;
    bank?: string;
    promo_type?: string;
    sort?: string;
  }) => void;
  onRefresh: () => void;
  isRefreshing: boolean;
}) {
  const [keyword, setKeyword] = useState("");
  const [bank, setBank] = useState("");
  const [type, setType] = useState("");
  const [sort, setSort] = useState("comprehensive");

  const handleSearch = useCallback(() => {
    onFetch({ page: 1, keyword, bank, promo_type: type, sort });
  }, [keyword, bank, type, sort, onFetch]);

  const handleKeywordChange = useCallback(
    (v: string) => {
      setKeyword(v);
      if (v === "") onFetch({ page: 1, keyword: "", bank, promo_type: type, sort });
    },
    [bank, type, sort, onFetch]
  );

  const handleBankChange = useCallback(
    (v: string) => {
      setBank(v);
      onFetch({ page: 1, keyword, bank: v, promo_type: type, sort });
    },
    [keyword, type, sort, onFetch]
  );

  const handleTypeChange = useCallback(
    (v: string) => {
      setType(v);
      onFetch({ page: 1, keyword, bank, promo_type: v, sort });
    },
    [keyword, bank, sort, onFetch]
  );

  const handleSortChange = useCallback(
    (v: string) => {
      setSort(v);
      onFetch({ page: 1, keyword, bank, promo_type: type, sort: v });
    },
    [keyword, bank, type, onFetch]
  );

  const handlePageChange = useCallback(
    (page: number) => {
      onFetch({ page, keyword, bank, promo_type: type, sort });
      window.scrollTo({ top: 0, behavior: "smooth" });
    },
    [keyword, bank, type, sort, onFetch]
  );

  return (
    <div>
      <SearchBar
        keyword={keyword}
        onKeywordChange={handleKeywordChange}
        bank={bank}
        onBankChange={handleBankChange}
        type={type}
        onTypeChange={handleTypeChange}
        sort={sort}
        onSortChange={handleSortChange}
        onRefresh={onRefresh}
        isRefreshing={isRefreshing}
      />

      <div className="flex items-center justify-between mb-4">
        <h2 className="text-lg font-semibold text-gray-800">
          最新活动
          <span className="ml-2 text-sm font-normal text-gray-500">
            ({initialPagination.total} 条)
          </span>
        </h2>
      </div>

      {initialPromotions.length === 0 ? (
        <div className="text-center py-16 text-gray-400">
          <p className="text-4xl mb-4">📭</p>
          <p>暂无匹配的活动</p>
        </div>
      ) : (
        <>
          <div className="grid gap-4">
            {initialPromotions.map((promo) => (
              <PromotionCard key={promo.uuid} promo={promo} />
            ))}
          </div>
          <Pagination
            page={initialPagination.page}
            totalPages={initialPagination.total_pages}
            total={initialPagination.total}
            onPageChange={handlePageChange}
          />
        </>
      )}
    </div>
  );
}
