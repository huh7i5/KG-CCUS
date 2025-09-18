#!/bin/bash

# 简单的GPU清理脚本
echo "🧹 清理GPU内存中..."

# 查找并终止可能占用GPU的Python进程
echo "🔍 查找占用GPU的Python进程..."

# 获取所有python3 main.py进程并终止
PIDS=$(pgrep -f "python3 main.py" 2>/dev/null)
if [ ! -z "$PIDS" ]; then
    echo "📋 发现以下进程: $PIDS"
    echo "🔄 正在终止进程..."

    # 优雅终止
    echo "$PIDS" | xargs -r kill -TERM 2>/dev/null
    sleep 2

    # 检查是否还有进程存在，如果有则强制终止
    REMAINING_PIDS=$(pgrep -f "python3 main.py" 2>/dev/null)
    if [ ! -z "$REMAINING_PIDS" ]; then
        echo "⚡ 强制终止剩余进程..."
        echo "$REMAINING_PIDS" | xargs -r kill -KILL 2>/dev/null
        sleep 1
    fi

    echo "✅ Python进程已清理"
else
    echo "✅ 未发现需要清理的Python进程"
fi

# 清理PyTorch缓存（如果可能）
echo "🧹 清理PyTorch GPU缓存..."
python3 -c "
import sys
try:
    import torch
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
        torch.cuda.synchronize()
        print('✅ PyTorch GPU缓存已清理')
    else:
        print('ℹ️  CUDA不可用，跳过缓存清理')
except ImportError:
    print('ℹ️  PyTorch未安装，跳过缓存清理')
except Exception as e:
    print(f'⚠️  缓存清理警告: {e}')
" 2>/dev/null

# 显示GPU状态
echo "📊 当前GPU状态:"
nvidia-smi --query-gpu=memory.used,memory.total --format=csv,noheader,nounits 2>/dev/null | while read line; do
    used=$(echo $line | cut -d',' -f1 | xargs)
    total=$(echo $line | cut -d',' -f2 | xargs)
    echo "  GPU内存: ${used}MB / ${total}MB"
done

echo "🎉 GPU清理完成！"