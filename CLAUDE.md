# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目概述

智能姓名生成系统 - 基于AI的中文姓名生成服务，使用适配器模式集成6个AI平台（阿里云、硅基流动、OpenAI、Gemini、派欧云、AI Studio），支持多文化风格和228万+真实姓名语料库增强。

**技术栈**：Python 3.8+ + Flask + SQLite
**核心架构**：适配器模式 + 自动降级 + 语料库增强

**重要提示**：所有后端命令都应在 `NameGenerationAgent/` 目录下执行。

## 常用命令

```bash
cd NameGenerationAgent

# 激活虚拟环境（项目使用 .venv/）
../.venv/Scripts/activate                     # Windows
# source ../.venv/bin/activate                # Linux/Mac

# 安装依赖
pip install -r requirements.txt

# 启动服务（http://127.0.0.1:5000）
python main.py

# 运行测试
python -m pytest tests/ -v
python -m pytest tests/test_basic.py::TestNameGenerator::test_get_available_options -v
python -m pytest tests/test_corpus_integration.py -v

# 性能测试（需先启动服务）
locust -f tests/locustfile.py --host=http://127.0.0.1:5000

# API测试
curl http://127.0.0.1:5000/health
curl -X POST http://127.0.0.1:5000/generate -H "Content-Type: application/json" -d "{\"description\": \"聪明可爱的女孩\", \"count\": 5}"

# 日志查看
Get-Content .\logs\app.log -Wait -Tail 50    # PowerShell
tail -f logs/app.log                          # Git Bash/WSL
```

## 核心架构

```
Web层 (src/web/app.py)              → Flask应用，RESTful API端点
    ↓
Core层 (src/core/)                  → NameGenerator: 业务逻辑编排
                                    → CorpusEnhancer: 语料库增强
    ↓
API层 (src/api/)                    → UnifiedClient: 统一API接口 + 自动降级
                                    → RouterStrategy: 路由策略（4种）
                                    → Adapters: 6个AI平台适配器
    ↓
Data层 (src/data/corpus_loader.py)  → CorpusLoader: SQLite语料库访问
Utils  (src/utils/)                 → CacheManager, InputValidator, NameValidator, Logger
```

### 适配器模式

所有AI平台适配器继承 `BaseAPIAdapter` (src/api/adapters/base_adapter.py:14)，实现 `generate_names()` 方法。基类提供 `list_models()` 默认实现和 `_make_request()` 通用HTTP请求方法。适配器异常使用 `APIException` (base_adapter.py:164)。

6个适配器：AliyunAdapter（支持降级模型）、SiliconFlowAdapter、OpenAIAdapter、GeminiAdapter、PaiouAdapter（流式）、AistudioAdapter（流式）。

### 自动降级机制

API调用失败时自动按优先级降级 (src/api/unified_client.py:138)：
1. 优先使用用户指定API（`preferred_api`参数）
2. 按路由策略选择API
3. 失败时自动尝试下一个API
4. 所有API失败时使用模拟数据（可通过`use_mock_on_failure`控制）

**路由默认优先级** (src/api/router_strategy.py:7)：
```python
['aistudio', 'aliyun', 'siliconflow', 'paiou', 'openai', 'gemini']
```

**注意**：路由策略的默认顺序与 `get_primary_api()` (config/api_config.py:202) 不同，后者用于健康检查和初始化诊断，优先级顺序为 `['aliyun', 'siliconflow', 'openai', 'gemini', 'paiou', 'aistudio']`。

### 路由策略

支持4种策略 (src/api/router_strategy.py)：PriorityRouterStrategy（默认）、WeightedRouterStrategy、RoundRobinRouterStrategy、CapabilityRouterStrategy。配置在 config/settings.py 的 `ROUTER_STRATEGY` 和 `ROUTER_WEIGHTS`。

### 语料库增强

SQLite数据库（data/names_corpus.db，179MB，已gitignore）存储228万+真实姓名，包含 `chinese_names`、`ancient_names`、`family_names` 三个表。通过 `src/data/corpus_loader.py` 的 CorpusLoader 访问。

增强流程 (src/core/corpus_enhancer.py)：提取关键词 → 检索相关姓名示例 → 注入提示词 → 排序过滤结果。

### 缓存机制

基于JSON文件的自定义缓存 (src/utils/cache_manager.py)：缓存键基于MD5(提示词+参数)，存储在 `data/cache/cache.json`，默认TTL 3600秒，最大1000条目，LRU淘汰。

## 配置管理

复制 `env.example` 为 `.env` 并配置至少一个API密钥（`ALIYUN_API_KEY`、`SILICONFLOW_API_KEY`、`OPENAI_API_KEY`、`GEMINI_API_KEY`、`PAIOU_API_KEY`、`AISTUDIO_API_KEY`）。其他可选配置：`ALLOWED_ORIGINS`、`DEBUG`、`LOG_LEVEL`、`CACHE_TTL`。

每个平台在 config/api_config.py 有配置类，继承 `APIConfig` 基类 (line 34)。注意 `AistudioConfig` 未继承 `APIConfig`，而是独立实现了相同接口。适配器注册在 `APIManager.apis` (line 183)。

## 添加新API适配器

1. **创建适配器** `src/api/adapters/newapi_adapter.py`：继承 `BaseAPIAdapter`，实现 `generate_names()`
2. **创建配置类** `config/api_config.py`：继承 `APIConfig`
3. **注册配置** 在 `config/api_config.py:183` 的 `APIManager.apis` 字典添加
4. **注册工厂** 在适配器文件底部调用 `register_adapter()`，并在 `src/api/adapters/__init__.py` 的 `ensure_adapters_imported()` 添加导入
5. **更新优先级** 在 `src/api/router_strategy.py:7` 和 `config/api_config.py:204`

## API端点

核心端点：
- `POST /generate` - 生成姓名（description, count, cultural_style, gender, age, preferred_api, model, use_cache）
- `GET /options` - 获取可用选项
- `GET /models` - 获取可用模型列表（支持 `api` 和 `refresh` 查询参数）
- `GET /health` - 健康检查
- `GET /stats` - 统计信息

管理端点：
- `GET /history/list` - 生成历史
- `POST /favorites` - 添加收藏
- `POST /cache/clear` - 清除缓存

## 调试与故障排查

**API适配器未初始化**（启动时显示"已初始化 0 个API适配器"）：
- 确保 `.env` 文件存在并配置了API密钥
- 检查 `config/api_config.py` 中的 `APIManager.apis` 字典
- 检查 `src/api/adapters/__init__.py` 中的 `ensure_adapters_imported()`

**语料库未加载**：检查 `data/names_corpus.db` 是否存在，可通过 `cd data && python convert_csv_to_sqlite.py` 重建。

**循环导入**：项目使用延迟导入模式，如遇导入错误检查是否在模块顶层导入了相互依赖的模块，使用函数内导入或 `get_*()` 辅助函数。

## 代码规范

### 延迟导入（避免循环依赖）
```python
def get_unified_client():
    from ..api.unified_client import unified_client
    return unified_client
```

### 异常处理
```python
from src.api.adapters.base_adapter import APIException
try:
    result = adapter.generate_names(prompt)
except APIException as e:
    logger.warning(f"API调用失败: {str(e)}")
```

### 日志记录
```python
from src.utils.logger import get_logger
logger = get_logger(__name__)
```

### 输入验证
使用 `src/utils/validation.py` 中的 `InputValidator`（请求参数校验）和 `NameValidator`（生成结果校验）。所有SQL查询必须参数化。

## 关键文件

- **main.py** - 启动入口（UTF-8编码设置、环境变量加载、Flask启动）
- **config/api_config.py** - API配置类和管理器（APIConfig基类、6个平台配置、APIManager）
- **config/prompts.py** - 提示词模板（多文化风格）
- **config/settings.py** - 应用配置（Config/DevelopmentConfig/ProductionConfig/TestingConfig）
- **src/core/name_generator.py** - 核心生成逻辑（协调API调用和语料库增强）
- **src/api/unified_client.py** - 统一API客户端（自动降级实现）
- **src/api/router_strategy.py** - 路由策略（4种策略实现）
- **src/api/model_manager.py** - 动态模型发现与缓存
- **src/api/adapters/base_adapter.py** - 适配器基类和APIException
- **src/web/app.py** - Flask应用和所有API端点定义
- **src/data/corpus_loader.py** - SQLite语料库数据访问层
- **src/utils/validation.py** - 输入和姓名验证器

## 前端

前端使用 uni-app（Vue 3 + TypeScript），位于 `../智能姓名生成系统/`：
```bash
cd ../智能姓名生成系统
npm install
npm run dev:h5              # H5
npm run dev:mp-weixin       # 微信小程序
```
API地址配置在 `common/api.ts` 的 `BASE_URL`。

## Windows注意事项

- main.py 已设置控制台UTF-8编码 (main.py:8-11)
- 虚拟环境位于项目根目录 `.venv/`
- 如遇到 `.env` 文件未找到错误，main.py 会提示运行 `python quick_setup_api.py`
