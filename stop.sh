#!/bin/bash

# 停止银行活动聚合平台所有服务
cd "$(dirname "$0")"

echo "🛑 停止银行活动聚合平台..."
fuser -k 8080/tcp 2>/dev/null || true
fuser -k 3000/tcp 2>/dev/null || true
sleep 2
echo "✅ 已停止所有服务"
