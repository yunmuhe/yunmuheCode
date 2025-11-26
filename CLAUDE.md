# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目概述

这是一个基于多平台大模型API的智能中文姓名生成系统，支持根据角色描述生成具有文化内涵的姓名。系统采用适配器模式集成多个AI平台（阿里云、硅基流动、百度、派欧云、AI Studio等），并包含语料库增强功能。

## 常用命令

### 环境设置
```bash
# 激活虚拟环境（Windows）
venv\Scripts\activate

# 安装依赖
pip install -r NameGenerationAgent/requirements.txt
```

### 运行应用
```bash
# 启动Flask Web应用（主要方式）
cd NameGenerationAgent
python main.py

# 直接运行Flask应用
python NameGenerationAgent/src/web/app.py
```

### 测试
```bash
# 运行所有测试
cd NameGenerationAgent
python -m pytest tests/

# 运行单个测试文件
python -m pytest tests/test_basic.py

# 运行特定测试
python -m pytest tests/test_basic.py::TestNameGenerator::test_get_available_options
```

### 代码质量
```bash
# 代码格式化
black NameGenerationAgent/src/
isort NameGenerationAgent/src/

# 代码检查
flake8 NameGenerationAgent/src/
```

## 项目架构

### 核心架构模式

**适配器模式（Adapter Pattern）**：系统的核心设计模式
- `src/api/adapters/base_adapter.py` - 定义统一的API接口
- `src/api/adapters/*_adapter.py` - 各平台的具体实现（阿里云、硅基流动、百度、派欧云、AI Studio等）
- `src/api/unified_client.py` - 统一客户端，管理所有适配器，实现API调用的优先级和降级策略

**关键流程**：
1. 用户请求 → Flask路由（`src/web/app.py`）
2. 调用 `NameGenerator.generate_names()` （`src/core/name_generator.py`）
3. 构建提示词（`config/prompts.py`）
4. 可选：语料库增强（`src/core/corpus_enhancer.py`）
5. 通过 `UnifiedAPIClient` 调用API适配器
6. API适配器按优先级尝试调用（aliyun → siliconflow → baishan → baidu → paiou → aistudio）
7. 失败时自动降级到下一个API或返回模拟数据
8. 解析响应并返回结果

### 目录结构

```
NameGenerationAgent/
├── config/                    # 配置模块
│   ├── settings.py           # 应用基础配置（环境、日志、缓存）
│   ├── api_config.py         # 多平台API配置和管理器
│   └── prompts.py            # 提示词模板（文化风格、性别、年龄）
├── src/
│   ├── api/                  # API集成层
│   │   ├── adapters/         # 各平台适配器
│   │   │   ├── base_adapter.py      # 基础适配器接口
│   │   │   ├── aliyun_adapter.py    # 阿里云百炼
│   │   │   ├── siliconflow_adapter.py
│   │   │   ├── baishan_adapter.py
│   │   │   ├── baidu_adapter.py
│   │   │   ├── paiou_adapter.py     # 派欧云（OpenAI兼容）
│   │   │   └── aistudio_adapter.py  # AI Studio
│   │   └── unified_client.py # 统一API客户端（核心调度器）
│   ├── core/                 # 核心业务逻辑
│   │   ├── name_generator.py # 姓名生成器（主要业务逻辑）
│   │   ├── knowledge_base.py # 知识库管理（姓氏、名字、寓意）
│   │   └── corpus_enhancer.py # 语料库增强器
│   ├── data/                 # 数据处理
│   │   └── corpus_loader.py  # 语料库加载器
│   ├── utils/                # 工具模块
│   │   ├── cache_manager.py  # 缓存管理
│   │   ├── logger.py         # 日志工具
│   │   └── validation.py     # 输入输出验证
│   └── web/                  # Web应用
│       ├── app.py            # Flask应用主文件
│       └── templates/        # HTML模板
├── tests/                    # 测试文件
├── data/                     # 运行时数据目录
│   ├── cache/               # 缓存数据
│   └── knowledge_base.json  # 知识库数据
├── main.py                   # 主启动脚本
└── requirements.txt          # 依赖包列表

Chinese-Names-Corpus-master/  # 中文人名语料库（120万+）
├── Chinese_Names_Corpus/     # 中文姓氏和称呼
├── English_Names_Corpus/     # 英文人名（48万）
└── Japanese_Names_Corpus/    # 日文人名（18万）
```

### 关键组件交互

**API调用链路**：
```
Flask路由 → NameGenerator → PromptTemplates → CorpusEnhancer（可选）
                ↓
         UnifiedAPIClient
                ↓
    按优先级尝试各个适配器
                ↓
         解析和验证响应
                ↓
            返回结果
```

**配置加载顺序**：
1. `.env` 文件加载（`config/api_config.py` 和 `src/web/app.py`）
2. 环境变量读取（各 `*Config` 类）
3. API管理器初始化（`APIManager`）
4. 适配器注册（`UnifiedAPIClient._initialize_adapters()`）

### 重要设计决策

1. **延迟导入**：为避免循环依赖，多处使用函数内导入或延迟导入模式
2. **降级策略**：API调用失败时自动尝试下一个API，最终降级到模拟数据
3. **缓存机制**：使用MD5哈希的请求参数作为缓存键，减少重复API调用
4. **语料库增强**：可选地使用真实人名语料库增强提示词，提高生成质量
5. **响应解析**：适配器需要解析各平台的不同响应格式，统一为标准格式

## 环境变量配置

必须在 `NameGenerationAgent/.env` 文件中配置至少一个API密钥：

```bash
# 至少配置一个
ALIYUN_API_KEY=your_key_here
SILICONFLOW_API_KEY=your_key_here
BAISHAN_API_KEY=your_key_here
BAIDU_API_KEY=your_key_here
PAIOU_API_KEY=your_key_here
AISTUDIO_API_KEY=your_key_here
AISTUDIO_API_URL=https://api-xxx.aistudio-app.com/v1
AISTUDIO_MODEL=qwen3:235b

# 可选配置
ALLOWED_ORIGINS=*  # CORS配置
```

## 添加新的API适配器

1. 在 `src/api/adapters/` 创建新适配器文件（如 `newapi_adapter.py`）
2. 继承 `BaseAPIAdapter` 并实现 `generate_names()` 方法
3. 在 `config/api_config.py` 添加配置类
4. 在 `APIManager.__init__()` 中注册新API
5. 在 `unified_client.py` 的 `_initialize_adapters()` 中添加导入逻辑

## 语料库数据

项目包含 `Chinese-Names-Corpus-master` 目录，提供：
- 120万中文常见人名
- 1千中文姓氏
- 5千中文称呼词根
- 48万英文翻译人名
- 18万日文人名

语料库通过 `src/data/corpus_loader.py` 加载，由 `src/core/corpus_enhancer.py` 用于增强提示词。

## 常见问题

### API适配器未初始化
检查 `.env` 文件是否存在且API密钥正确配置。查看 `main.py` 启动日志中的API诊断信息。

### 循环导入错误
项目使用延迟导入模式。如果遇到循环导入，检查是否在模块顶层导入了相互依赖的模块，改为函数内导入。

### 提示词格式问题
提示词模板在 `config/prompts.py` 中定义。修改时注意保持格式要求部分的完整性，确保AI能正确解析输出。

### 缓存问题
缓存数据存储在 `data/cache/` 目录。如需清空缓存，删除该目录下的文件或通过 `CacheManager.clear()` 方法清空。
