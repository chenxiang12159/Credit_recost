export default function AboutPage() {
  const sources = [
    { name: "赚客吧", desc: "信用卡羊毛活动分享社区（Cookie 登录抓取）" },
    { name: "广发银行", desc: "信用卡优惠活动频道" },
    { name: "中信银行", desc: "信用卡优惠专区" },
    { name: "民生银行", desc: "信用卡精彩优惠" },
    { name: "邮储银行", desc: "信用卡优惠活动" },
    { name: "农业/建设/浦发/中行/招行", desc: "渠道优化中（待审核上线）" },
  ];

  const changelog = [
    { v: "v1.1", d: "评分排序、图片缓存+水印、小红书草稿页、综合/时间排序" },
    { v: "v1.0", d: "基础爬取、本地前端、Telegram推送、自动刷新" },
  ];

  return (
    <div className="max-w-3xl mx-auto px-4 py-8">
      <h1 className="text-2xl font-bold text-gray-900 mb-6">📖 使用说明</h1>

      <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6 mb-6">
        <h2 className="text-lg font-semibold text-gray-800 mb-3">🚀 怎么用</h2>
        <ol className="list-decimal list-inside space-y-2 text-gray-600 text-sm">
          <li><b>首页</b>：自动加载最新活动，每5分钟自动刷新</li>
          <li><b>筛选</b>：按银行 / 类型 / 关键词搜索；按综合 / 评分 / 时间排序</li>
          <li><b>图片</b>：点击缩略图放大，← → 切换多图</li>
          <li><b>已读</b>：点卡片右上角 👁 标记已读（变灰），刷新后仍保留</li>
          <li><b>小红书草稿</b>：左侧候选 → 点一条 → AI 生成文案 → 复制去发</li>
          <li><b>提交</b>：粘贴活动文字 → AI 解析 → 存库 + 推送</li>
          <li><b>刷新按钮</b>：手动触发爬取，有新内容弹 Toast</li>
        </ol>
      </div>

      <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6 mb-6">
        <h2 className="text-lg font-semibold text-gray-800 mb-4">📊 数据来源</h2>
        <div className="grid gap-3">
          {sources.map((s) => (
            <div key={s.name} className="py-2 border-b border-gray-50 last:border-0">
              <span className="font-medium text-gray-800">🏦 {s.name}</span>
              <span className="text-sm text-gray-500 ml-2">— {s.desc}</span>
            </div>
          ))}
        </div>
        <p className="text-xs text-gray-400 mt-3">
          ⚠️ 银行官方活动页为 JS 渲染，部分渠道仍在优化；赚客吧为社区搬运，时效性强。
        </p>
      </div>

      <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6 mb-6">
        <h2 className="text-lg font-semibold text-gray-800 mb-4">🔧 技术栈</h2>
        <div className="grid grid-cols-2 gap-4 text-sm">
          <div><span className="font-medium text-gray-700">前端:</span> <span className="text-gray-500">Next.js + TailwindCSS</span></div>
          <div><span className="font-medium text-gray-700">后端:</span> <span className="text-gray-500">FastAPI + SQLite</span></div>
          <div><span className="font-medium text-gray-700">AI:</span> <span className="text-gray-500">DeepSeek v4-flash</span></div>
          <div><span className="font-medium text-gray-700">爬虫:</span> <span className="text-gray-500">httpx + BeautifulSoup</span></div>
          <div><span className="font-medium text-gray-700">推送:</span> <span className="text-gray-500">Telegram Bot</span></div>
          <div><span className="font-medium text-gray-700">调度:</span> <span className="text-gray-500">GitHub Actions</span></div>
        </div>
      </div>

      <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
        <h2 className="text-lg font-semibold text-gray-800 mb-4">📝 更新日志</h2>
        <div className="space-y-2 text-sm">
          {changelog.map((c) => (
            <div key={c.v} className="flex gap-3">
              <span className="font-mono text-primary-600 font-medium">{c.v}</span>
              <span className="text-gray-600">{c.d}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
