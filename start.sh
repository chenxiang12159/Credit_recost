#!/bin/bash

# 银行活动聚合 - 启动脚本

echo "=========================================="
echo "银行活动聚合 - 启动服务"
echo "=========================================="

# 检查虚拟环境
if [ ! -d "backend/venv" ]; then
    echo "创建虚拟环境..."
    cd backend
    python -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    cd ..
else
    cd backend
    source venv/bin/activate
    cd ..
fi

# 检查配置文件
if [ ! -f "backend/.env" ]; then
    echo "警告：未找到 .env 配置文件"
    echo "请复制 .env.example 为 .env 并填入配置"
    echo "cp backend/.env.example backend/.env"
fi

# 启动服务
echo "启动 API 服务..."
echo "访问地址: http://localhost:8080"
echo "API 文档: http://localhost:8080/docs"
echo "=========================================="

cd backend
uvicorn app.api:app --reload --host 0.0.0.0 --port 8080
