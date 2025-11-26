# 📁 项目结构说明

## 🎯 核心文件结构

```
NameGenerationAgent/
│
├── 📄 启动文件
│   ├── main.py                      # 主启动脚本
│   ├── quick_start.bat              # Windows快速启动
│   └── quick_setup_api.py           # API密钥配置工具
│
├── 📄 数据处理
│   ├── organize_data.py             # 数据整理工具（推荐）
│   └── process_corpus.py            # JSON数据处理（可选）
│
├── 📚 文档
│   ├── README.md                    # 项目总览
│   ├── QUICK_REFERENCE.md           # 快速参考手册
│   ├── CORPUS_INTEGRATION.md        # 语料库集成指南
│   ├── DATA_ORGANIZATION_GUIDE.md   # 数据整理指南
│   ├── DATA_PROCESSING_GUIDE.md     # 数据处理指南
│   ├── PROJECT_SUMMARY.md           # 项目技术总结
│   └── PROJECT_STRUCTURE.md         # 本文档
│
├── ⚙️ 配置文件
│   ├── requirements.txt             # Python依赖
│   ├── env.example                  # 环境变量示例
│   └── config/                      # 配置目录
│       ├── api_config.py            # API配置
│       ├── prompts.py               # 提示词模板
│       └── settings.py              # 系统设置
│
├── 💾 数据目录
│   └── data/
│       ├── organized/               # 整理后的CSV数据（推荐使用）
│       │   ├── 中文人名/           # 120万+现代人名
│       │   ├── 古代人名/           # 25万+古代人名
│       │   ├── 姓氏库/             # 姓氏数据
│       │   ├── 日文人名/           # 日文人名
│       │   ├── 英文人名/           # 英文人名
│       │   ├── 成语词典/           # 5万+成语
│       │   ├── 称呼关系/           # 称呼关系
│       │   ├── 诗词名字/           # 诗词成语名字
│       │   ├── 主题名字/           # 主题名字
│       │   └── DATA_CATALOG.txt    # 数据目录清单
│       │
│       ├── processed/               # JSON格式数据（可选）
│       └── cache/                   # 缓存目录
│
├── 🔧 源代码
│   └── src/
│       ├── api/                     # API层
│       │   ├── adapters/            # API适配器
│       │   │   ├── base_adapter.py          # 基础适配器
│       │   │   ├── paiou_adapter.py         # 派欧云
│       │   │   ├── aistudio_adapter.py      # Aistudio
│       │   │   ├── baidu_adapter.py         # 百度
│       │   │   ├── aliyun_adapter.py        # 阿里云
│       │   │   ├── siliconflow_adapter.py   # SiliconFlow
│       │   │   └── baishan_adapter.py       # 白山云
│       │   └── unified_client.py    # 统一API客户端
│       │
│       ├── core/                    # 核心功能
│       │   ├── name_generator.py    # 姓名生成器
│       │   ├── corpus_enhancer.py   # 语料库增强器
│       │   └── knowledge_base.py    # 知识库
│       │
│       ├── data/                    # 数据加载
│       │   └── corpus_loader.py     # 语料库加载器
│       │
│       ├── utils/                   # 工具函数
│       │   ├── cache_manager.py     # 缓存管理
│       │   ├── logger.py            # 日志系统
│       │   └── validation.py        # 数据验证
│       │
│       └── web/                     # Web应用
│           ├── app.py               # Flask应用
│           └── templates/           # HTML模板
│               ├── index.html       # 主页
│               ├── 404.html         # 404页面
│               └── 500.html         # 500页面
│
├── 🛠️ 工具目录
│   └── tools/
│       └── data_organizer.py        # 数据整理器
│
├── 🧪 测试目录
│   └── tests/
│       ├── test_basic.py            # 基础测试
│       └── __init__.py
│
└── 📝 日志目录
    └── logs/                        # 运行日志
```

---

## 📊 文件说明

### 核心启动文件

| 文件 | 用途 | 必需 |
|------|------|------|
| `main.py` | 主启动脚本，启动Web服务 | ✅ |
| `quick_start.bat` | Windows快速启动脚本 | 推荐 |
| `quick_setup_api.py` | API密钥配置向导 | 推荐 |

### 数据处理文件

| 文件 | 用途 | 推荐度 |
|------|------|--------|
| `organize_data.py` | 整理所有数据为CSV格式并分类 | ⭐⭐⭐⭐⭐ |
| `process_corpus.py` | 处理数据为JSON格式 | ⭐⭐⭐ |

### 文档文件

| 文件 | 内容 |
|------|------|
| `README.md` | 项目介绍、快速开始 |
| `QUICK_REFERENCE.md` | 常用命令和代码速查 |
| `CORPUS_INTEGRATION.md` | 语料库集成详细说明 |
| `DATA_ORGANIZATION_GUIDE.md` | 数据整理完整指南 |
| `DATA_PROCESSING_GUIDE.md` | 数据处理详细指南 |
| `PROJECT_SUMMARY.md` | 技术架构和设计要点 |
| `PROJECT_STRUCTURE.md` | 项目结构说明（本文档） |

### 配置文件

| 文件 | 用途 |
|------|------|
| `requirements.txt` | Python依赖包列表 |
| `env.example` | 环境变量配置示例 |
| `config/api_config.py` | API平台配置 |
| `config/prompts.py` | 提示词模板 |
| `config/settings.py` | 系统设置 |

---

## 🎯 使用流程

### 首次使用

```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 配置API
python quick_setup_api.py

# 3. 整理数据（如果有语料库）
python organize_data.py

# 4. 启动服务
python main.py
```

### 日常使用

```bash
# 直接启动
quick_start.bat

# 或
python main.py
```

---

## 📂 数据目录说明

### data/organized/ （推荐使用）

已整理好的CSV格式数据，按类别分类：

- **中文人名/**: 120万+现代中文人名
- **古代人名/**: 25万+古代人名
- **姓氏库/**: 中文和日文姓氏
- **日文人名/**: 日文姓名数据
- **英文人名/**: 英文姓名数据
- **成语词典/**: 5万+成语
- **称呼关系/**: 称呼关系数据
- **诗词名字/**: 诗词成语风格名字
- **主题名字/**: 季节、网名等主题

### data/processed/ （可选）

JSON格式的处理数据：

- `modern_names.json`: 现代人名（按性别分类）
- `ancient_names.json`: 古代人名
- `surnames.json`: 姓氏库（按频次排序）
- `given_names.json`: 名字库（按性别分类）
- `chengyu_high_quality.json`: 高质量成语
- `statistics.json`: 统计数据

---

## 🔧 核心模块说明

### API适配器 (src/api/adapters/)

每个适配器负责对接一个LLM平台：
- 继承自 `BaseAPIAdapter`
- 实现 `generate_names()` 方法
- 处理API调用和响应解析

### 统一客户端 (src/api/unified_client.py)

- 管理所有API适配器
- 实现API切换和故障转移
- 提供缓存和统计功能

### 姓名生成器 (src/core/name_generator.py)

- 构建提示词
- 调用API生成姓名
- 验证和处理结果

### 语料库加载器 (src/data/corpus_loader.py)

- 加载语料库数据
- 提供姓名推荐
- 成语取名功能

### Web应用 (src/web/app.py)

- Flask Web服务
- API路由
- 前端交互

---

## 🚀 开发指南

### 添加新的API平台

1. 在 `src/api/adapters/` 创建新适配器
2. 继承 `BaseAPIAdapter`
3. 在 `config/api_config.py` 添加配置
4. 在 `unified_client.py` 注册

### 添加新的数据源

1. 将数据文件放入语料库目录
2. 运行 `python organize_data.py`
3. 自动分类到对应目录

### 自定义提示词

编辑 `config/prompts.py` 中的模板

---

## 📊 数据规模

| 数据类型 | 数量 | 位置 |
|---------|------|------|
| 中文人名 | 120万+ | data/organized/中文人名/ |
| 古代人名 | 25万+ | data/organized/古代人名/ |
| 日文人名 | 18万+ | data/organized/日文人名/ |
| 英文人名 | 48万+ | data/organized/英文人名/ |
| 成语词典 | 5万+ | data/organized/成语词典/ |
| 称呼关系 | 18万+ | data/organized/称呼关系/ |

**总计: 350万+ 条数据**

---

## 🎯 最佳实践

### 数据使用

```python
# 推荐：使用整理后的CSV数据
import pandas as pd

df = pd.read_csv('data/organized/中文人名/Chinese_Names_Corpus_Gender.csv', 
                 encoding='utf-8-sig')
```

### 配置管理

```python
# 使用.env文件管理API密钥
# 不要将.env文件提交到版本控制
```

### 日志查看

```bash
# 查看运行日志
cat logs/app.log

# 或在Windows上
type logs\app.log
```

---

## ✅ 项目特点

- ✅ **结构清晰**: 按功能分层组织
- ✅ **易于扩展**: 模块化设计
- ✅ **文档完善**: 详细的使用文档
- ✅ **数据丰富**: 350万+数据
- ✅ **多平台**: 支持多个LLM平台
- ✅ **开箱即用**: 快速启动脚本

---

**查看其他文档获取更多信息！** 📚

