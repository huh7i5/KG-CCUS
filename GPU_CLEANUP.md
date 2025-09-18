# 🧹 GPU内存自动清理功能

## 功能说明

现在系统启动时会自动清理GPU内存，避免因为之前的进程占用显存导致模型加载失败。

## 启动命令对比

### 🆕 带自动清理的启动命令（推荐）

```bash
# 本地开发（自动清理GPU + 启动）
npm run dev

# 远程服务器（自动清理GPU + 启动，允许外部访问）
npm run dev-remote

# 使用./start.sh也会自动清理
./start.sh
```

### 🔧 其他可用命令

```bash
# 仅清理GPU内存（不启动服务）
npm run cleanup-gpu          # 简单清理
npm run cleanup-gpu-advanced # 高级清理（更智能）

# 直接启动（不清理GPU）
npm run dev-direct           # 本地开发
npm run dev-remote-direct    # 远程服务器

# 安全启动（先清理再启动，与dev相同）
npm run dev-safe
npm run dev-remote-safe
```

## 清理功能详情

### 简单清理 (`scripts/simple_cleanup.sh`)
- ✅ 终止所有 `python3 main.py` 进程
- ✅ 清理PyTorch GPU缓存
- ✅ 显示GPU内存状态
- ⚡ 快速执行，适合日常使用

### 高级清理 (`scripts/cleanup_gpu.py`)
- ✅ 智能识别GPU进程
- ✅ 安全性检查，避免误杀系统进程
- ✅ 优雅终止 → 强制终止的二级处理
- ✅ 详细的进程分析和内存统计
- 🎯 更精确，适合复杂环境

## 影响分析

### ✅ 正面影响

1. **避免启动失败**：自动清理防止"CUDA out of memory"错误
2. **提升可靠性**：每次启动都是干净的GPU环境
3. **节省时间**：无需手动检查和清理GPU进程
4. **智能保护**：只清理相关进程，保护系统稳定

### ⚠️ 需要注意的情况

1. **Jupyter Notebook**：如果在用Jupyter，会被终止（通常可以重启）
2. **其他ML项目**：同时运行的其他机器学习项目可能受影响
3. **长时间训练**：正在进行的长时间训练任务会被中断

### 🛡️ 安全机制

- **进程识别**：只终止明确的Python ML相关进程
- **系统保护**：不会终止系统关键进程
- **优雅退出**：先尝试正常终止，再强制终止
- **错误处理**：清理失败不会影响后续启动

## 使用建议

### 推荐场景
- ✅ 开发调试阶段
- ✅ 重启项目时
- ✅ GPU内存不足时
- ✅ 多人共享GPU服务器

### 谨慎场景
- ⚠️  有重要训练任务在后台运行
- ⚠️  多个项目同时开发
- ⚠️  生产环境部署

### 最佳实践

```bash
# 开发时推荐使用（自动清理）
npm run dev

# 如果有重要后台任务，使用直接启动
npm run dev-direct

# 服务器部署时，建议先检查
npm run cleanup-gpu-advanced  # 查看会清理什么
npm run dev-direct            # 然后直接启动
```

## 自定义配置

如果需要修改清理行为，可以编辑：
- `scripts/simple_cleanup.sh` - 简单清理逻辑
- `scripts/cleanup_gpu.py` - 高级清理逻辑

## 故障排除

### 清理失败
```bash
# 手动清理
./scripts/simple_cleanup.sh

# 查看GPU状态
nvidia-smi

# 手动终止特定进程
kill -9 <PID>
```

### 清理过度
```bash
# 使用直接启动避免清理
npm run dev-direct
```

---

💡 **提示**：首次使用建议先用 `npm run cleanup-gpu-advanced` 查看会清理哪些进程，确认安全后再使用 `npm run dev`。