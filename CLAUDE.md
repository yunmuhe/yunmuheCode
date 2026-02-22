# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目概述

智能姓名生成系统 - 基于AI的中文姓名生成服务，使用适配器模式集成6个AI平台（阿里云、硅基流动、OpenAI、Gemini、派欧云、AI Studio），支持多文化风格和228万+真实姓名语料库增强。

**技术栈**：Python 3.8+ + Flask + SQLite
**核心架构**：适配器模式 + 自动降级 + 语料库增强

**重要提示**：所有命令都应在 `NameGenerationAgent/` 目录下执行。

## 常用命令

```bash
# 进入后端项目目录
cd NameGenerationAgent

# 激活虚拟环境（项目使用 .venv1/）
../.venv1/Scripts/activate                    # Windows
# source ../.venv1/bin/activate               # Linux/Mac

# 安装依赖
pip install -r requirements.txt

# 启动服务（http://127.0.0.1:5000）
quick_start.bat                          # Windows（不自动激活虚拟环境，需手动激活）
python main.py                           # 直接启动

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
Get-Content .\logs\app.log -Wait -Tail 50                                    # PowerShell
tail -f logs/app.log                                                          # Git Bash/WSL
```

## 核心架构

### 三层架构

```
Web层 (src/web/app.py)          → Flask应用，RESTful API端点
    ↓
Core层 (src/core/)              → NameGenerator: 业务逻辑
                                → CorpusEnhancer: 语料库增强
    ↓
API层 (src/api/)                → UnifiedClient: 统一API接口
                                → RouterStrategy: 路由策略
                                → Adapters: 6个AI平台适配器
```

### 适配器模式

所有AI平台适配器继承 `BaseAPIAdapter` (src/api/adapters/base_adapter.py:22)，实现 `generate_names()` 方法。基类还提供 `list_models()` 默认实现（返回配置中的默认模型）和 `_make_request()` 通用HTTP请求方法：

- **AliyunAdapter** - 阿里云百炼（支持降级模型）
- **SiliconFlowAdapter** - 硅基流动
- **OpenAIAdapter** - OpenAI GPT系列
- **GeminiAdapter** - Google Gemini
- **PaiouAdapter** - 派欧云（支持流式响应）
- **AistudioAdapter** - AI Studio（支持流式响应）

### 自动降级机制

API调用失败时自动按优先级降级 (src/api/unified_client.py:138-206)：

1. 优先使用用户指定API（`preferred_api`参数）
2. 按路由策略选择API
3. 失败时自动尝试下一个API
4. 所有API失败时使用模拟数据（可通过`use_mock_on_failure`控制）

**默认优先级顺序** (src/api/router_strategy.py:6)：
```python
['aistudio', 'aliyun', 'siliconflow', 'paiou', 'openai', 'gemini']
```

**注意**：路由策略的默认顺序与 `get_primary_api()` (config/api_config.py:202) 不同，后者用于健康检查和初始化诊断。

### 路由策略

支持4种路由策略 (src/api/router_strategy.py)：

- **PriorityRouterStrategy**: 按固定优先级顺序（默认）
- **WeightedRouterStrategy**: 按权重排序
- **RoundRobinRouterStrategy**: 轮询
- **CapabilityRouterStrategy**: 按能力过滤（支持避免特定API、流式优先）

配置：在 config/settings.py 设置 `ROUTER_STRATEGY` 和 `ROUTER_WEIGHTS`。

### 语料库增强

使用SQLite数据库（data/names_corpus.db，179MB）存储228万+真实姓名。

增强流程 (src/core/corpus_enhancer.py)：
1. 从描述提取关键词 → 2. 检索相关姓名示例 → 3. 注入提示词 → 4. 排序过滤结果

### 缓存机制

使用基于JSON文件的自定义缓存 (src/utils/cache_manager.py)：缓存键基于提示词+参数的MD5哈希，存储在 `data/cache/cache.json`，默认TTL 3600秒，最大条目数1000，支持过期清理和LRU淘汰。

## 配置管理

### 环境变量（.env）

复制 `env.example` 为 `.env` 并配置至少一个API密钥：

```bash
ALIYUN_API_KEY=your_key
SILICONFLOW_API_KEY=your_key
OPENAI_API_KEY=your_key
GEMINI_API_KEY=your_key
PAIOU_API_KEY=your_key
AISTUDIO_API_KEY=your_key

ALLOWED_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
DEBUG=True
LOG_LEVEL=INFO
CACHE_TTL=3600
```

### API配置类

每个平台在 config/api_config.py 有配置类，继承 `APIConfig` 基类 (line 34)。注意 `AistudioConfig` 未继承 `APIConfig`，而是独立实现了相同接口。

阿里云支持降级模型 (line 63)：
```python
self.fallback_models = [os.environ.get('ALIYUN_FALLBACK_MODEL', 'qwen-turbo')]
```

## 添加新API适配器

1. **创建适配器** `src/api/adapters/newapi_adapter.py`：
```python
from .base_adapter import BaseAPIAdapter, APIException

class NewAPIAdapter(BaseAPIAdapter):
    def generate_names(self, prompt: str, **kwargs) -> dict:
        data = {'model': self.config.model, 'messages': [{'role': 'user', 'content': prompt}]}
        response = self._make_request('chat/completions', data)
        return self._parse_response(response)
```

2. **创建配置类** `config/api_config.py`：
```python
class NewAPIConfig(APIConfig):
    def __init__(self):
        super().__init__(name='newapi', base_url='https://api.newapi.com/v1',
                        api_key=os.environ.get('NEWAPI_API_KEY'))
        self.model = 'model-name'
```

3. **注册适配器** 在 `config/api_config.py:182` APIManager.apis 字典添加配置

4. **注册工厂** 在适配器文件底部：
```python
from . import register_adapter
register_adapter('newapi', lambda config: NewAPIAdapter(config))
```
并在 `src/api/adapters/__init__.py` 的 `ensure_adapters_imported()` 添加导入

5. **更新优先级** 在 `src/api/router_strategy.py:6` 和 `config/api_config.py:202`

## API端点

核心端点：
- `POST /generate` - 生成姓名（description, count, cultural_style, gender, age, preferred_api, model, use_cache）
- `GET /options` - 获取可用选项
- `GET /models` - 获取可用模型列表（支持 api 和 refresh 参数）
- `GET /health` - 健康检查
- `GET /stats` - 统计信息

管理端点：
- `GET /history/list` - 生成历史
- `POST /favorites` - 添加收藏
- `POST /cache/clear` - 清除缓存

### 动态模型选择

系统支持动态获取和选择各平台的可用模型：

```bash
# 获取所有平台的模型列表
curl http://127.0.0.1:5000/models

# 获取特定平台的模型
curl http://127.0.0.1:5000/models?api=aliyun

# 强制刷新缓存
curl http://127.0.0.1:5000/models?refresh=true

# 使用指定模型生成
curl -X POST http://127.0.0.1:5000/generate \
  -H "Content-Type: application/json" \
  -d '{"description": "聪明的女孩", "preferred_api": "aliyun", "model": "qwen-max"}'
```

详细文档见 `docs/MODEL_DISCOVERY.md`。

## 调试与故障排查

**API适配器未初始化**（启动时显示"已初始化 0 个API适配器"）：
- 确保 `.env` 文件存在并配置了API密钥
- 检查 `config/api_config.py` 中的 APIManager.apis 字典是否正确注册
- 检查 `src/api/adapters/__init__.py` 中的 `ensure_adapters_imported()` 是否导入所有适配器

**前端无法连接**：
- 检查 `ALLOWED_ORIGINS` 配置
- 检查防火墙5000端口
- 确认后端服务已启动：`curl http://127.0.0.1:5000/health`

**语料库未加载**：
- 检查 `data/names_corpus.db` 是否存在（179MB）
- 重建：`cd data && python convert_csv_to_sqlite.py`
- 或禁用语料库增强（编辑 `src/core/name_generator.py`）

**日志级别**：在 `.env` 设置 `LOG_LEVEL=DEBUG/INFO/WARNING/ERROR`

**循环导入问题**：
- 项目使用延迟导入模式避免循环依赖
- 如遇到导入错误，检查是否在模块顶层导入了相互依赖的模块
- 使用函数内导入或 `get_*()` 辅助函数

## 代码规范

### 延迟导入

项目使用延迟导入避免循环依赖：
```python
def get_unified_client():
    from ..api.unified_client import unified_client
    return unified_client
```

### 异常处理

使用 `APIException` (src/api/adapters/base_adapter.py:91)：
```python
try:
    result = adapter.generate_names(prompt)
except APIException as e:
    logger.warning(f"API调用失败: {str(e)}")
```

### 日志记录

使用 `src/utils/logger.py`：
```python
from src.utils.logger import get_logger
logger = get_logger(__name__)
```

## 关键文件

- **main.py** - 启动入口，设置UTF-8编码，加载环境变量，启动Flask
- **config/api_config.py** - API配置和管理器，所有平台配置类
- **config/prompts.py** - 提示词模板，支持多文化风格
- **config/settings.py** - 应用配置，路由策略设置
- **src/core/name_generator.py** - 核心生成逻辑，协调API调用和语料库增强
- **src/api/unified_client.py** - 统一API客户端，实现自动降级
- **src/api/router_strategy.py** - 路由策略实现（4种策略）
- **src/api/model_manager.py** - 动态模型发现与缓存
- **src/api/adapters/base_adapter.py** - 适配器基类
- **src/web/app.py** - Flask应用，所有API端点定义

## 数据库

`data/names_corpus.db`（179MB，已在.gitignore）包含：
- `chinese_names` - 中文现代姓名
- `ancient_names` - 古代姓名
- `family_names` - 姓氏库

新开发者需从CSV重建或从团队获取。

## 前端

前端使用uni-app，位于 `../智能姓名生成系统/`：
```bash
cd ../智能姓名生成系统
npm install
npm run dev:h5              # H5
npm run dev:mp-weixin       # 微信小程序
```

## Windows注意事项

- main.py 已设置控制台UTF-8编码 (main.py:8-11)
- 虚拟环境位于项目根目录 `.venv1/`
- quick_start.bat 不自动激活虚拟环境，需手动激活后再运行 `python main.py`
- 如遇到 `.env` 文件未找到错误，main.py 会提示运行 `python quick_setup_api.py`

## 文档资源

- **docs/API-DOCUMENTATION.md** - 完整API文档
- **docs/API-QUICK-REFERENCE.md** - API快速参考
- **docs/MODEL_DISCOVERY.md** - 动态模型发现功能详解
- **docs/FRONTEND_MODEL_SELECTION.md** - 前端模型选择集成指南
- **docs/README.md** - 文档索引
- **docs/*.puml** - PlantUML架构图（架构、类图、数据流、时序图等）
