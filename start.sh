#!/bin/bash

# API数据导出工具启动脚本
echo "🚀 启动 API数据导出工具..."

# 检查依赖是否已安装
if [ ! -d "venv" ]; then
    echo "📦 安装Python依赖..."
    pip install -r requirements.txt
fi

# 创建必要的目录
mkdir -p config templates_config output

# 启动Flask应用
echo "🌐 启动Web服务器..."
echo "📍 访问地址: http://localhost:8080"
echo "⏹️  停止服务: Ctrl+C"
echo ""

python app.py