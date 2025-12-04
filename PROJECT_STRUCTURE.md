# 项目文件结构

## 根目录
```
名字生成智能体/
├── NameGenerationAgent/          # 后端（Python Flask）
├── 智能姓名生成系统/              # 前端（uni-app）
├── venv/                         # Python虚拟环境
├── .gitignore                    # Git忽略配置
├── CLAUDE.md                     # Claude Code项目指南
└── README.md                     # 项目说明文档
```

## 后端目录结构（NameGenerationAgent/）
```
NameGenerationAgent/
├── config/                       # 配置文件
│   ├── api_config.py            # API配置和管理器
│   └── prompts.py               # 提示词模板
├── src/                         # 源代码
│   ├── api/                     # API层
│   │   ├── adapters/            # 6个AI平台适配器
│   │   │   ├── base_adapter.py
│   │   │   ├── aliyun_adapter.py
│   │   │   ├── siliconflow_adapter.py
│   │   │   ├── baishan_adapter.py
│   │   │   ├── baidu_adapter.py
│   │   │   ├── paiou_adapter.py
│   │   │   └── aistudio_adapter.py
│   │   └── unified_client.py    # 统一API客户端
│   ├── core/                    # 核心业务逻辑
│   │   ├── name_generator.py    # 姓名生成器
│   │   ├── corpus_enhancer.py   # 语料库增强器
│   │   └── knowledge_base.py    # 知识库
│   ├── data/                    # 数据访问层
│   │   └── corpus_loader.py     # SQLite数据加载器
│   ├── web/                     # Web层
│   │   └── app.py               # Flask应用
│   └── utils/                   # 工具类
│       ├── cache_manager.py     # 缓存管理
│       ├── logger.py            # 日志工具
│       └── validation.py        # 输入验证
├── tests/                       # 测试用例
│   ├── test_basic.py            # 基础功能测试
│   └── test_corpus_integration.py  # 语料库集成测试
├── data/                        # 数据目录
│   ├── names_corpus.db          # SQLite数据库（179MB，.gitignore）
│   ├── cache/                   # API响应缓存（.gitignore）
│   ├── convert_csv_to_sqlite.py # 数据库生成脚本
│   └── verify_database.py       # 数据库验证脚本
├── logs/                        # 日志目录（.gitignore）
├── main.py                      # 启动入口
├── requirements.txt             # Python依赖
├── quick_start.bat              # 快速启动脚本（Windows）
├── quick_setup_api.py           # API配置脚本
├── setup_domain.bat             # 域名配置脚本
├── start_natapp.bat             # 内网穿透启动脚本
├── .env                         # 环境变量（.gitignore）
└── README.md                    # 后端说明文档
```

## 前端目录结构（智能姓名生成系统/）
```
智能姓名生成系统/
├── pages/                       # 页面
│   ├── Generate/                # 生成页面
│   ├── History/                 # 历史页面
│   ├── Favorites/               # 收藏页面
│   └── Settings/                # 设置页面
├── common/                      # 公共模块
│   └── api.ts                   # API请求封装
├── static/                      # 静态资源
├── uni_modules/                 # uni-app模块
├── manifest.json                # 应用配置
├── pages.json                   # 页面配置
├── package.json                 # 前端依赖
└── README.md                    # 前端说明文档
```

## 已清理的文件类型
- ✅ Python缓存文件（`__pycache__/`, `*.pyc`, `*.pyo`）
- ✅ 临时日志文件（`app.log`）
- ✅ 临时测试脚本（`test_connection.bat`）
- ✅ 临时文档文件（`project_structure.txt`, `1.puml`）

## 保留的重要文件
- ✅ 正式测试文件（`tests/test_*.py`）
- ✅ 配置脚本（`quick_*.bat`, `setup_*.bat`）
- ✅ 数据库工具脚本（`data/*.py`）
- ✅ 文档文件（`*.md`）

## 文件忽略说明（.gitignore）
- 虚拟环境：`venv/`, `.venv/`
- 环境变量：`.env`, `*.env`
- Python缓存：`__pycache__/`, `*.pyc`, `*.pyo`
- 日志文件：`logs/`, `*.log`
- 数据库文件：`*.db`, `*.sqlite`（需自行运行脚本生成）
- 缓存目录：`data/cache/`
- 临时文件：`*.tmp`, `*.bak`, `*.puml`, `project_structure.txt`
- 测试脚本：`test_*.bat`, `debug_*.py`, `temp_*.py`
- 前端项目：`智能姓名生成系统/`（有独立仓库）
