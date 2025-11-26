# 智能姓名生成系统

一个基于多平台大语言模型的智能姓名生成系统，支持多种API提供商，具有现代化的Web界面。

## 📁 项目结构

```
名字生成智能体/
├── NameGenerationAgent/          # 主应用目录
│   ├── config/                   # 配置文件
│   ├── src/                      # 源代码
│   │   ├── api/                  # API适配器
│   │   ├── core/                 # 核心业务逻辑
│   │   ├── data/                 # 数据处理
│   │   ├── utils/                # 工具函数
│   │   └── web/                  # Web应用
│   ├── tests/                    # 测试文件
│   ├── docs/                     # 项目文档
│   │   ├── CORPUS_INTEGRATION.md
│   │   ├── SYSTEM_ARCHITECTURE.md
│   │   └── PROJECT_STRUCTURE.md
│   ├── main.py                   # 主启动脚本
│   ├── requirements.txt          # Python依赖
│   └── README.md                 # 项目说明
│
├── Chinese-Names-Corpus-master/  # 中文人名语料库（120万+）
├── 智能姓名生成系统/              # 前端uni-app项目
├── docs/                         # 开发文档
│   ├── 使用说明.md
│   ├── 历史记录功能说明.md
│   ├── 前端修复说明.md
│   ├── 新增风格说明.md
│   └── 首页响应式优化说明.md
├── venv/                         # Python虚拟环境
├── CLAUDE.md                     # Claude Code指南
└── .gitignore                    # Git忽略文件
```

## 🚀 快速开始

### 1. 安装依赖

```bash
cd NameGenerationAgent
pip install -r requirements.txt
```

### 2. 配置API密钥

复制 `env.example` 为 `.env` 并配置至少一个API密钥：

```bash
cp env.example .env
# 编辑.env文件，添加API密钥
```

### 3. 启动应用

```bash
# Windows
quick_start.bat

# 或手动启动
python main.py
```

访问 http://localhost:5000 使用Web界面。

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
