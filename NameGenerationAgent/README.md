# NameGenerationAgent - 智能姓名生成系统

基于AI的智能中文姓名生成系统，采用适配器模式集成6个AI平台，支持多文化风格和语料库增强。

## 主要特性

- **多AI平台支持**：集成6个AI平台（阿里云、硅基流动、OpenAI、Gemini、派欧云、AI Studio），自动降级
- **多文化风格**：支持中文传统、中文现代、中文古典、西方、日式、奇幻等多种风格
- **语料库增强**：基于228万+真实姓名数据的SQLite数据库，提供高质量姓名示例
- **智能缓存**：自动缓存生成结果，提升响应速度
- **RESTful API**：纯API服务，支持跨平台前端接入

## 技术栈

- **后端**：Python 3.8+ + Flask
- **数据库**：SQLite（228万+记录，179MB）
- **AI集成**：6个AI平台适配器
- **架构模式**：适配器模式 + 自动降级 + 语料库增强

## 快速开始

### 环境要求

- Python 3.8+
- 至少一个AI平台的API密钥

### 安装步骤

```bash
# 1. 激活虚拟环境（注意：项目使用 venv/ 而不是 .venv/）
venv\Scripts\activate                    # Windows
# source venv/bin/activate               # Linux/Mac

# 2. 安装依赖
pip install -r requirements.txt

# 3. 配置API密钥
copy env.example .env                    # Windows
# cp env.example .env                    # Linux/Mac

# 编辑 .env 文件，填入至少一个API密钥：
# PAIOU_API_KEY=your_key
# AISTUDIO_API_KEY=your_key
# 等等...

# 4. 启动服务
quick_start.bat                          # Windows（推荐）
# python main.py                         # 或手动启动
```

服务将在 `http://127.0.0.1:5000` 启动。

### 验证安装

```bash
# 检查健康状态
curl http://127.0.0.1:5000/health

# 测试生成姓名
curl -X POST http://127.0.0.1:5000/generate \
  -H "Content-Type: application/json" \
  -d '{"description": "聪明可爱的女孩", "count": 5}'
```

## 项目结构

```
NameGenerationAgent/
├── config/                   # 配置文件
│   ├── api_config.py        # API配置和管理
│   └── prompts.py           # 提示词模板
├── src/
│   ├── api/                 # API层
│   │   ├── adapters/        # 6个AI平台适配器
│   │   └── unified_client.py # 统一API客户端
│   ├── core/                # 核心业务逻辑
│   │   ├── name_generator.py    # 姓名生成器
│   │   └── corpus_enhancer.py   # 语料库增强器
│   ├── data/                # 数据访问层
│   │   └── corpus_loader.py     # 语料库加载器
│   ├── web/                 # Web层
│   │   └── app.py           # Flask应用
│   └── utils/               # 工具类
├── data/
│   ├── names_corpus.db      # SQLite数据库（179MB）
│   └── cache/               # 缓存目录
├── tests/                   # 测试文件
├── logs/                    # 日志目录
├── main.py                  # 启动入口
├── requirements.txt         # Python依赖
└── .env                     # 环境变量配置（需自行创建）
```

## API端点

### 核心端点

- `POST /generate` - 生成姓名
  - 参数：`description`, `count`, `cultural_style`, `gender`, `age`, `preferred_api`, `use_cache`
- `GET /options` - 获取可用选项（文化风格、性别等）
- `GET /health` - 健康检查
- `GET /stats` - 统计信息（API使用情况、缓存命中率等）

### 管理端点

- `GET /history/list` - 生成历史
- `POST /favorites` - 添加收藏
- `POST /cache/clear` - 清除缓存

详细API文档请参考 [CLAUDE.md](../CLAUDE.md)。

## 数据库说明

项目使用SQLite数据库存储228万+条真实姓名数据，用于语料库增强。

- **数据库文件**：`data/names_corpus.db`（179MB）
- **主要数据表**：
  - `chinese_names` - 中文人名
  - `ancient_names` - 古代人名
  - `family_names` - 姓氏库
  - 其他主题和风格相关表

### 数据库维护

```bash
# 如果数据库损坏或需要重建
cd data
python convert_csv_to_sqlite.py

# 测试数据库连接
python test_corpus_sqlite.py
```

## 配置说明

### 环境变量（.env）

```bash
# API平台配置（至少配置一个）
PAIOU_API_KEY=sk_xxx
AISTUDIO_API_KEY=your_key
AISTUDIO_API_URL=https://api-xxx.aistudio-app.com/v1
ALIYUN_API_KEY=your_key
SILICONFLOW_API_KEY=your_key
OPENAI_API_KEY=your_key
GEMINI_API_KEY=your_key

# CORS配置（前端访问必需）
ALLOWED_ORIGINS=http://localhost:5173,http://127.0.0.1:5173

# 可选配置
DEBUG=True
LOG_LEVEL=INFO
```

### API优先级

系统会按以下优先级尝试API（可在 `config/api_config.py` 中调整）：
1. 阿里云（aliyun）
2. 硅基流动（siliconflow）
3. OpenAI
4. Gemini
5. 派欧云（paiou）
6. AI Studio（aistudio）

## 开发指南

### 运行测试

```bash
# 运行所有测试
python -m pytest tests/ -v

# 运行特定测试
python -m pytest tests/test_basic.py::TestNameGenerator::test_get_available_options -v
```

### 查看日志

```bash
# 实时查看日志（PowerShell）
Get-Content .\logs\app.log -Wait -Tail 50

# 实时查看日志（Git Bash/WSL）
tail -f logs/app.log

# 仅查看错误和警告
Get-Content .\logs\app.log -Wait -Tail 50 | Select-String -Pattern "ERROR|WARNING"
```

### 添加新的AI适配器

1. 在 `src/api/adapters/` 创建新适配器文件
2. 继承 `BaseAPIAdapter` 并实现 `generate_names()` 方法
3. 在 `config/api_config.py` 添加配置类
4. 在 `src/api/unified_client.py` 注册适配器

详细步骤请参考 [CLAUDE.md](../CLAUDE.md) 的"添加新API适配器"章节。

## 部署

### 开发环境（内网穿透）

```bash
# 使用natapp进行内网穿透
start_natapp.bat
setup_domain.bat
```

### 生产环境（云服务器）

```bash
cd /path/to/NameGenerationAgent
chmod +x deploy/deploy_to_server.sh
sudo ./deploy/deploy_to_server.sh

# 服务管理
systemctl status nameagent
systemctl restart nameagent
journalctl -u nameagent -f
```

## 常见问题

### API适配器未初始化

**症状**：启动时显示"已初始化 0 个API适配器"

**解决**：
1. 确保 `.env` 文件存在（复制 `env.example` 为 `.env`）
2. 在 `.env` 中填入至少一个API密钥
3. 重启服务

### 前端无法连接后端

**解决**：
1. 检查后端是否运行：`curl http://127.0.0.1:5000/health`
2. 检查 `.env` 中的 `ALLOWED_ORIGINS` 配置
3. 确保防火墙允许5000端口

### 语料库未加载

**解决**：
1. 检查 `data/names_corpus.db` 是否存在
2. 如不存在，运行：`cd data && python convert_csv_to_sqlite.py`
3. 或禁用语料库增强（编辑 `src/core/name_generator.py`）

更多问题请参考 [CLAUDE.md](../CLAUDE.md) 的"调试与故障排查"章节。

## 性能说明

- **典型响应时间**：2-4秒（主要取决于AI API响应时间）
- **缓存命中**：<50ms
- **并发能力**：使用Gunicorn部署可支持多worker并发

性能优化建议请参考 [CLAUDE.md](../CLAUDE.md) 的"性能优化"章节。

## 相关文档

- [CLAUDE.md](../CLAUDE.md) - 完整的开发指南和架构文档
- [docs/FIX_CULTURAL_STYLE.md](docs/FIX_CULTURAL_STYLE.md) - 文化风格切换修复说明
- [CLEANUP_SUMMARY.md](CLEANUP_SUMMARY.md) - 项目架构演进记录

## 前端项目

本项目的前端使用 uni-app 开发，位于 `../智能姓名生成系统/` 目录。

前端支持：
- H5网页
- 微信小程序
- Android/iOS APP

前端启动：
```bash
cd ../智能姓名生成系统
npm install
npm run dev:h5              # H5开发
npm run dev:mp-weixin       # 微信小程序
```

## License

MIT

## 贡献

欢迎提交Issue和Pull Request！

开发前请阅读 [CLAUDE.md](../CLAUDE.md) 了解项目架构和开发规范。
