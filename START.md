# 🚀 知识图谱对话系统 - 快速启动指南

## 一键启动前后端

### 🎯 本地开发启动
```bash
# 在项目根目录下
npm run dev
```

### 🌐 远程服务器启动（AutoDL等）
```bash
# 允许外部访问的启动方式
npm run dev-remote
```

这将同时启动：
- Flask后端服务器 (端口 8000)
- Vue.js前端开发服务器 (端口 5174，允许外部访问)

### 🎯 方法二：分别启动

#### 启动后端
```bash
cd server
python3 main.py
```

#### 启动前端
```bash
cd chat-kg
npm run dev
```

## 📱 访问地址

### 本地开发
- **前端界面**: http://localhost:5174
- **后端API**: http://localhost:8000

### 远程服务器（AutoDL等）
- **前端界面**: http://你的公网IP:映射端口
- **后端API**: http://你的公网IP:映射端口

#### AutoDL端口映射设置
1. 在AutoDL控制台设置端口映射
2. 前端端口: 5174 → 自定义公网端口
3. 后端端口: 8000 → 自定义公网端口

## 🛠️ 其他有用命令

### 项目初始化
```bash
# 安装所有依赖
npm run install-all

# 构建知识图谱
npm run build-kg

# 完整设置（依赖+知识图谱）
npm run setup
```

### 前端相关
```bash
# 仅启动前端
npm run frontend

# 前端+允许外部访问
npm run frontend-server

# 构建前端生产版本
npm run build-frontend
```

### 后端相关
```bash
# 仅启动后端
npm run backend

# 构建知识图谱（指定项目）
python3 main.py --project project_v1

# 从检查点恢复
python3 main.py --project project_v1 --resume data/project_v1/iter_v0.json
```

## 🎨 功能介绍

1. **聊天对话**: 与知识图谱进行智能问答
2. **图谱可视化**: 交互式知识图谱展示
3. **实体关系**: 舰艇损管技术相关知识
4. **热重载**: 前端代码修改自动刷新

## 🔧 开发提示

- 前端代码在 `chat-kg/src/` 目录
- 后端API在 `server/app/views/` 目录
- 知识图谱数据在 `data/project_v1/` 目录
- 原始文本数据在 `data/raw_data.txt`

## ❓ 常见问题

### 端口被占用
```bash
# 查看端口占用
netstat -tulpn | grep :5173
netstat -tulpn | grep :8000

# 修改端口（在vite.config.js中修改前端端口）
```

### 依赖安装失败
```bash
# 清除npm缓存
npm cache clean --force

# 重新安装
rm -rf node_modules package-lock.json
npm install
```

### 知识图谱为空
```bash
# 重新构建知识图谱
npm run build-kg
```