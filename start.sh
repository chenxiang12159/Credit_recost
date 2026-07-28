#!/bin/bash

# 银行活动聚合平台 - 一键启动脚本
# 用法:
#   ./start.sh         启动前后端 (开发模式 npm run dev)
#   ./start.sh prod    先构建再用生产模式启动前端
#   ./start.sh stop    停止所有服务
#   ./start.sh status  查看运行状态

set -e
cd "$(dirname "$0")"

PYTHON=${PYTHON:-python3.11}
LOG_DIR="logs"
mkdir -p "$LOG_DIR"

BACKEND_PORT=8080
FRONTEND_PORT=3000

stop_services() {
    echo "🛑 停止服务 (端口 $BACKEND_PORT / $FRONTEND_PORT)..."
    fuser -k ${BACKEND_PORT}/tcp 2>/dev/null || true
    fuser -k ${FRONTEND_PORT}/tcp 2>/dev/null || true
    sleep 2
    echo "✅ 已停止"
}

status_services() {
    echo "=== 服务状态 ==="
    if curl -s -o /dev/null -w "%{http_code}" http://localhost:$BACKEND_PORT/api/promotions/latest 2>/dev/null | grep -q 200; then
        echo "后端 (8080): ✅ 运行中"
    else
        echo "后端 (8080): ❌ 未运行"
    fi
    if curl -s -o /dev/null -w "%{http_code}" http://localhost:$FRONTEND_PORT 2>/dev/null | grep -q 200; then
        echo "前端 (3000): ✅ 运行中"
    else
        echo "前端 (3000): ❌ 未运行"
    fi
}

case "$1" in
    stop)
        stop_services
        exit 0
        ;;
    status)
        status_services
        exit 0
        ;;
esac

# 启动前先清理旧进程
echo "🧹 清理旧进程..."
fuser -k ${BACKEND_PORT}/tcp 2>/dev/null || true
fuser -k ${FRONTEND_PORT}/tcp 2>/dev/null || true
sleep 2

echo "=========================================="
echo "  银行活动聚合平台 - 启动中"
echo "=========================================="

# 后端
echo "🚀 启动后端 (port $BACKEND_PORT)..."
cd backend
setsid $PYTHON -m uvicorn app.api:app --reload --host 0.0.0.0 --port $BACKEND_PORT \
    > "../$LOG_DIR/backend.log" 2>&1 &
cd ..

# 前端
if [ "$1" = "prod" ]; then
    echo "🏗  生产模式：构建前端..."
    cd frontend
    npm run build > "../$LOG_DIR/frontend-build.log" 2>&1
    echo "🚀 启动前端 (port $FRONTEND_PORT, 生产模式)..."
    setsid npm run start > "../$LOG_DIR/frontend.log" 2>&1 &
    cd ..
else
    echo "🚀 启动前端 (port $FRONTEND_PORT, 开发模式)..."
    cd frontend
    setsid npm run dev > "../$LOG_DIR/frontend.log" 2>&1 &
    cd ..
fi

# 等待后端就绪
echo "⏳ 等待后端启动..."
for i in $(seq 1 20); do
    if curl -s -o /dev/null http://localhost:$BACKEND_PORT/api/promotions/latest 2>/dev/null; then
        break
    fi
    sleep 1
done

echo ""
echo "✅ 启动完成！"
echo "   前端:  http://localhost:$FRONTEND_PORT"
echo "   后端:  http://localhost:$BACKEND_PORT"
echo "   日志:  $LOG_DIR/backend.log"
echo "          $LOG_DIR/frontend.log"
echo ""
echo "   停止:  ./start.sh stop"
echo "   状态:  ./start.sh status"
