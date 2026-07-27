export default function AboutPage() {
  const sources = [
    { name: "赚客吧", url: "https://www.zuanke8.com", desc: "信用卡优惠活动分享社区" },
    { name: "中国农业银行", url: "https://www.abchina.com", desc: "信用卡刷卡优惠" },
    { name: "中国工商银行", url: "https://www.icbc.com.cn", desc: "信用卡优惠活动" },
    { name: "广发银行", url: "https://www.cgbchina.com.cn", desc: "信用卡优惠活动" },
    { name: "中国银行", url: "https://www.bankofchina.com", desc: "信用卡优惠活动" },
    { name: "中信银行", url: "https://www.citicbank.com", desc: "信用卡优惠活动" },
    { name: "中国建设银行", url: "https://www.ccb.com", desc: "信用卡优惠活动" },
  ];

  return (
    <div className="max-w-3xl mx-auto px-4 py-8">
      <h1 className="text-2xl font-bold text-gray-900 mb-6">📖 关于项目</h1>

      <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6 mb-6">
        <p className="text-gray-600 leading-relaxed">
          银行活动聚合平台是一个自动化工具，每日抓取各大银行信用卡优惠活动，
          并通过 AI 智能解析提取关键信息。支持 Telegram 实时推送，让您不错过任何优惠。
        </p>
      </div>

      <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6 mb-6">
        <h2 className="text-lg font-semibold text-gray-800 mb-4">📊 数据来源</h2>
        <div className="grid gap-3">
          {sources.map((s) => (
            <div key={s.name} className="flex items-center justify-between py-2 border-b border-gray-50 last:border-0">
              <div>
                <span className="font-medium text-gray-800">🏦 {s.name}</span>
                <span className="text-sm text-gray-500 ml-2">— {s.desc}</span>
              </div>
              <a
                href={s.url}
                target="_blank"
                rel="noopener noreferrer"
                className="text-sm text-primary-600 hover:text-primary-800"
              >
                访问 ↗
              </a>
            </div>
          ))}
        </div>
      </div>

      <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
        <h2 className="text-lg font-semibold text-gray-800 mb-4">🔧 技术栈</h2>
        <div className="grid grid-cols-2 gap-4 text-sm">
          <div className="py-2">
            <span className="font-medium text-gray-700">前端:</span>{" "}
            <span className="text-gray-500">Next.js + TailwindCSS</span>
          </div>
          <div className="py-2">
            <span className="font-medium text-gray-700">后端:</span>{" "}
            <span className="text-gray-500">FastAPI + SQLite</span>
          </div>
          <div className="py-2">
            <span className="font-medium text-gray-700">AI:</span>{" "}
            <span className="text-gray-500">DeepSeek API</span>
          </div>
          <div className="py-2">
            <span className="font-medium text-gray-700">爬虫:</span>{" "}
            <span className="text-gray-500">httpx + BeautifulSoup</span>
          </div>
          <div className="py-2">
            <span className="font-medium text-gray-700">推送:</span>{" "}
            <span className="text-gray-500">Telegram Bot</span>
          </div>
          <div className="py-2">
            <span className="font-medium text-gray-700">调度:</span>{" "}
            <span className="text-gray-500">GitHub Actions</span>
          </div>
        </div>
      </div>
    </div>
  );
}
