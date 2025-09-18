#!/bin/bash

# 知识图谱对话系统一键启动脚本
echo "🚀 启动知识图谱对话系统..."

# 检查Python环境
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 未找到，请先安装Python3"
    exit 1
fi

# 检查Node.js环境
if ! command -v npm &> /dev/null; then
    echo "❌ npm 未找到，请先安装Node.js"
    exit 1
fi

# 检查并安装Python依赖
echo "📦 检查Python依赖..."
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt > /dev/null 2>&1
    echo "✅ Python依赖已安装"
fi

# 检查并安装前端依赖
echo "📦 检查前端依赖..."
if [ ! -d "chat-kg/node_modules" ]; then
    echo "正在安装前端依赖..."
    cd chat-kg && npm install && cd ..
fi

# 检查知识图谱数据
if [ ! -f "data/data.json" ]; then
    echo "⚠️  未找到知识图谱数据，将使用默认数据"
fi

# 启动系统
echo "🔥 启动前后端服务..."
echo "📍 前端地址: http://localhost:5174 (如端口占用会自动切换)"
echo "📍 后端API: http://localhost:8000"
echo "📍 AutoDL用户请设置端口映射访问"
echo ""
echo "🧹 将自动清理GPU内存以避免冲突"
echo "按 Ctrl+C 停止服务"

npm run dev