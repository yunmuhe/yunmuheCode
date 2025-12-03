# 智能姓名生成系统

一个基于多平台大语言模型的智能姓名生成系统，支持多种API提供商，具有现代化的Web界面。

## 📁 项目结构

本项目采用**前后端分离**架构：

```
名字生成智能体/
├── NameGenerationAgent/          # 后端智能体（Flask API服务）
│   ├── config/                   # 配置文件
│   ├── src/                      # 源代码
│   │   ├── api/                  # API适配器（多平台集成）
│   │   ├── core/                 # 核心业务逻辑
│   │   ├── data/                 # 数据处理
│   │   ├── utils/                # 工具函数
│   │   └── web/                  # Flask应用（测试框架）
│   ├── tests/                    # 测试文件
│   ├── docs/                     # 技术文档
│   ├── main.py                   # 主启动脚本
│   └── requirements.txt          # Python依赖
│
├── 智能姓名生成系统/              # 前端应用（uni-app）
│   ├── pages/                    # 页面目录
│   │   ├── Generate/             # 生成页面
│   │   ├── History/              # 历史记录
│   │   ├── Favorites/            # 收藏夹
│   │   └── Settings/             # 设置
│   ├── common/                   # 公共模块
│   │   ├── api.ts                # API请求封装
│   │   ├── storage.ts            # 本地存储
│   │   └── theme.ts              # 主题管理
│   ├── static/                   # 静态资源
│   ├── App.vue                   # 应用入口
│   ├── main.js                   # 主入口
│   ├── package.json              # 依赖配置
│   └── README.md                 # 前端说明
│
├── Chinese-Names-Corpus-master/  # 中文人名语料库（120万+）
├── docs/                         # 项目文档
│   ├── 使用说明.md
│   ├── Git使用指南.md
│   ├── 项目架构说明.md
│   └── 项目总结与PPT提示词.md
├── venv/                         # Python虚拟环境
├── CLAUDE.md                     # Claude Code指南
├── README.md                     # 项目总览
└── .gitignore                    # Git忽略文件
```

## 🚀 快速开始

### 后端启动

#### 1. 安装依赖

```bash
cd NameGenerationAgent
pip install -r requirements.txt
```

#### 2. 配置API密钥

复制 `env.example` 为 `.env` 并配置至少一个API密钥：

```bash
cp env.example .env
# 编辑.env文件，添加API密钥
```

#### 3. 启动后端服务

```bash
# Windows
quick_start.bat

# 或手动启动
python main.py
```

后端服务运行在 http://localhost:5000

### 前端启动

#### 1. 安装依赖

```bash
cd 智能姓名生成系统
npm install
```

#### 2. 配置API地址（可选）

前端默认使用natapp公网映射地址 `http://nameagent.natapp1.cc`。

如需使用本地地址，编辑 `common/api.ts` 中的 `BASE_URL`：

```typescript
const BASE_URL = 'http://127.0.0.1:5000';  // 本地开发
```

#### 3. 启动前端应用

```bash
# H5开发
npm run dev:h5

# 或使用HBuilderX运行到浏览器/小程序
```

前端服务运行在 http://localhost:5173

### 配置CORS（重要）

在后端 `NameGenerationAgent/.env` 中配置允许的跨域来源：

```env
# 本地开发 + natapp公网访问
ALLOWED_ORIGINS=http://localhost:5173,http://127.0.0.1:5173,http://nameagent.natapp1.cc
```

## 📚 文档说明

- **CLAUDE.md** - Claude Code开发指南，包含架构说明和常用命令
- **NameGenerationAgent/README.md** - 主应用详细说明
- **NameGenerationAgent/docs/** - 技术文档
  - CORPUS_INTEGRATION.md - 语料库集成指南
  - SYSTEM_ARCHITECTURE.md - 系统架构文档
  - PROJECT_STRUCTURE.md - 项目结构说明
- **docs/** - 功能开发文档
  - 使用说明.md - 用户使用指南
  - 历史记录功能说明.md - 历史记录功能
  - 前端修复说明.md - 前端问题修复
  - 新增风格说明.md - 新增命名风格
  - 首页响应式优化说明.md - 响应式设计

## ✨ 主要特性

- 🤖 **多平台API支持** - 支持派欧云、Aistudio、阿里云、百度等多个LLM平台
- 📚 **120万人名语料库** - 集成Chinese-Names-Corpus，包含现代/古代人名、成语词典
- 🎨 **智能生成** - 结合大模型+语料库，生成具有文化内涵和真实性的姓名
- 🌐 **Web界面** - 现代化的Web界面，支持实时生成和API切换
- ⚡ **高性能** - 内置缓存机制，支持并发请求
- 🔄 **容错机制** - 自动故障转移和重试机制

## 🛠️ 开发说明

### 运行测试

```bash
cd NameGenerationAgent
python -m pytest tests/
```

### 代码格式化

```bash
black NameGenerationAgent/src/
isort NameGenerationAgent/src/
```

## 📝 许可证

本项目仅供学习和研究使用。

---

**智能姓名生成系统** - 让AI为您的角色创造完美的姓名！
