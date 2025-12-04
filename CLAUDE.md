# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目概述

前后端分离的智能中文姓名生成系统，采用适配器模式集成多个AI平台，支持语料库增强。

**技术栈**：
- 后端：Python 3.8+ + Flask，6个AI平台适配器（阿里云、硅基流动、百度、派欧云、AI Studio、白山云）
- 前端：uni-app（Vue 3 + TypeScript + Vite），支持H5/小程序/APP
- 数据库：SQLite（228万+记录，179MB），位于 `NameGenerationAgent/data/names_corpus.db`

**项目结构**：
```
名字生成智能体/
├── NameGenerationAgent/          # 后端（Flask）
│   ├── src/
│   │   ├── api/                  # API层
│   │   │   ├── adapters/         # 6个AI平台适配器
│   │   │   └── unified_client.py # 统一API客户端
│   │   ├── core/                 # 核心业务逻辑
│   │   │   ├── name_generator.py # 姓名生成器
│   │   │   └── corpus_enhancer.py # 语料库增强器
│   │   ├── data/                 # 数据访问层
│   │   │   └── corpus_loader.py  # SQLite数据加载器
│   │   ├── web/                  # Web层
│   │   │   └── app.py            # Flask应用
│   │   └── utils/                # 工具类
│   ├── config/                   # 配置文件
│   │   └── api_config.py         # API配置和管理
│   ├── data/
│   │   ├── names_corpus.db       # SQLite数据库（179MB）
│   │   └── cache/                # 响应缓存
│   ├── tests/                    # 测试用例
│   ├── main.py                   # 启动入口
│   └── .env                      # 环境变量配置
├── 智能姓名生成系统/              # 前端（uni-app）
│   ├── pages/                    # 页面
│   ├── common/
│   │   └── api.ts                # API请求封装
│   └── manifest.json             # 应用配置
└── venv/                         # Python虚拟环境
```

## 快速开始

### 首次使用

```bash
# 1. 激活虚拟环境
venv\Scripts\activate                             # Windows
# source venv/bin/activate                        # Linux/Mac

# 2. 安装依赖
cd NameGenerationAgent
pip install -r requirements.txt

# 3. 配置API密钥（至少配置一个）
python quick_setup_api.py

# 4. 启动后端
quick_start.bat                                   # Windows快速启动
# python main.py                                  # 或手动启动

# 5. 启动前端（新终端）
cd ../智能姓名生成系统
npm install
npm run dev:h5                                    # 访问 http://localhost:5173
```

### 日常开发

```bash
# 后端
cd NameGenerationAgent
venv\Scripts\activate                             # 激活虚拟环境
quick_start.bat                                   # 启动后端（5000端口）

# 前端
cd 智能姓名生成系统
npm run dev:h5                                    # H5开发（5173端口）
npm run dev:mp-weixin                             # 微信小程序开发
```

## 常用命令

### 后端开发

```bash
cd NameGenerationAgent

# 环境设置和启动
..\venv\Scripts\activate                          # 激活虚拟环境
pip install -r requirements.txt                   # 安装依赖
quick_start.bat                                   # 快速启动（推荐）
python main.py                                    # 手动启动（含API诊断）

# 配置
python quick_setup_api.py                         # 交互式配置API密钥
setup_domain.bat                                  # 配置CORS和域名
start_natapp.bat                                  # 启动内网穿透

# 测试
python -m pytest tests/                           # 运行所有测试
python -m pytest tests/test_basic.py::TestNameGenerator::test_get_available_options  # 运行特定测试
python -m pytest tests/ -v -s                     # 详细输出+print
```

### 前端开发

```bash
cd 智能姓名生成系统
npm install                                       # 安装依赖
npm run dev:h5                                    # H5开发（http://localhost:5173）
npm run dev:mp-weixin                             # 微信小程序开发
npm run build:h5                                  # H5构建（输出到 dist/build/h5/）
```

### 语料库操作（SQLite）

```bash
cd NameGenerationAgent
python test_corpus_sqlite.py                      # 测试加载器
cd data
python verify_database.py                         # 验证数据库
python convert_csv_to_sqlite.py                   # 重新生成数据库
```

**数据库表结构**（8个表，228万+记录）：`chinese_names`（114万）、`ancient_names`（25万）、`family_names`（4千）、`idioms`（5万）、`english_names`（46万）、`japanese_names`（18万）、`relationships`（18万）、`themed_names`（214条）

## 核心架构

### 适配器模式（系统核心）

6个AI平台通过适配器模式实现统一接口和自动降级：

```
用户请求 → NameGenerator → UnifiedAPIClient
                                ↓
         按优先级尝试 (aliyun → siliconflow → baishan → baidu → paiou → aistudio)
                                ↓
              成功：解析并缓存 | 失败：自动降级
```

**关键文件**：
- `src/api/adapters/base_adapter.py:15` - `BaseAPIAdapter` 抽象类，定义 `generate_names()` 接口
- `src/api/adapters/*_adapter.py` - 6个平台具体实现
- `src/api/unified_client.py:102-220` - `_initialize_adapters()` 动态导入适配器
- `src/core/name_generator.py` - 协调提示词构建、API调用、结果处理
- `config/api_config.py` - API配置和优先级（`get_primary_api()` 方法）

### 姓名生成流程

```
POST /generate → NameGenerator.generate_names()
  ↓
1. 输入验证 (validation.py)
2. 提示词构建 (config/prompts.py + 可选语料库增强)
   - 基础提示词：PromptTemplates.BASE_NAME_GENERATION_PROMPT
   - 文化风格：CULTURAL_STYLE_PROMPTS（chinese_traditional/modern, fantasy, western, japanese, ancient）
   - 性别/年龄：GENDER_PROMPTS, AGE_PROMPTS
   - 语料库增强：corpus_enhancer.enhance_prompt()（可选）
3. API调用 (unified_client.py:267-335)
   - 检查缓存 (MD5(prompt+params))
   - 按优先级尝试API，失败时自动降级
4. 响应解析 (各适配器，统一为 {name, meaning, source})
   - paiou_adapter.py:122-207 实现5种正则解析模式应对AI不稳定性
   - 统一输出格式要求："数字. 姓名：XXX - 含义说明"
5. 结果处理 (name_generator.py:235-266)
   - 生成ID、分析字符特征、缓存
6. 返回 {success, names: [...], api_name, model, total_generated}
```

**提示词格式要求**（关键）：
- AI必须严格按照 "数字. 姓名：XXX - 含义" 格式输出
- 西方姓名需包含英文和中文："John Smith（约翰·史密斯） - 含义"
- 所有适配器的解析器都依赖这个格式（使用正则表达式提取）
- 修改提示词格式时，必须同步更新各适配器的解析逻辑

### 重要设计模式

**1. 延迟导入（Lazy Import）** - 避免循环依赖
```python
# 错误示例（顶层导入）
from config.api_config import api_manager  # 可能循环依赖

# 正确示例（函数内导入）
def get_api_manager():
    from config.api_config import api_manager
    return api_manager
```
参考：`unified_client.py:11-90`, `base_adapter.py:11-18`, `name_generator.py:9-16`

**循环依赖问题说明**：
- `config.api_config` → `src.api.unified_client` → `src.api.adapters.*_adapter` → `config.api_config`
- 解决方案：在 `name_generator.py`, `unified_client.py`, 各适配器中使用函数级导入
- 关键原则：如果模块A和模块B相互依赖，将导入语句移到函数内部

**2. 降级策略** - API失败时自动切换
- 默认优先级：aliyun → siliconflow → baishan → baidu → paiou → aistudio
- 用户可通过 `preferred_api` 参数覆盖
- 配置在 `config/api_config.py:180-205` 的 `get_primary_api()` 中
- 实现在 `unified_client.py:267-335` 的 `generate_names()` 中

**3. 缓存机制** - MD5(prompt + params)
- 位置：`data/cache/`
- 管理：`src/utils/cache_manager.py`
- 禁用：`use_cache=False` 参数
- 缓存键：`MD5(json.dumps({prompt, count, cultural_style, gender, age}, sort_keys=True))`

**4. SQLite线程安全** - 每次查询创建新连接
- `CorpusLoader` 避免跨线程共享连接
- 全局单例模式（`get_corpus_loader()`）
- 参考：`src/data/corpus_loader.py:45-80`

### Flask API端点（src/web/app.py）

**核心端点**：
- `POST /generate` - 生成姓名
  - 请求参数：`description`（必需）, `count`, `cultural_style`, `gender`, `age`, `preferred_api`, `use_cache`
  - 响应格式：`{success, names: [{name, meaning, source, id}], api_name, model, total_generated}`
- `GET /options` - 获取可用选项
  - 响应格式：`{cultural_styles, genders, ages, available_apis: [{name, enabled, model}]}`
- `GET /health` - 健康检查
  - 响应格式：`{status: "ok", version, uptime, timestamp}`

**历史与收藏**：
- `GET /history/list` - 获取生成历史
- `POST /favorites` - 添加收藏（请求体：`{name, meaning, source}`）
- `GET /favorites` - 获取收藏列表
- `DELETE /favorites/<id>` - 删除收藏

**统计与管理**：
- `GET /stats` - 获取统计信息（缓存命中率、API使用次数）
- `POST /cache/clear` - 清除缓存

**CORS配置**：`.env` 中的 `ALLOWED_ORIGINS`（前端访问必需）

## 环境变量配置

在 `NameGenerationAgent/.env` 中配置（至少一个API密钥）：

```bash
# API平台（至少配置一个）
PAIOU_API_KEY=sk_xxx
AISTUDIO_API_KEY=your_key
AISTUDIO_API_URL=https://api-xxx.aistudio-app.com/v1
AISTUDIO_MODEL=qwen3:235b
# 其他：ALIYUN_API_KEY, SILICONFLOW_API_KEY, BAISHAN_API_KEY, BAIDU_API_KEY

# CORS配置（前端访问必需）
ALLOWED_ORIGINS=http://localhost:5173,http://127.0.0.1:5173,http://nameagent.natapp1.cc

# 可选
DEBUG=True
LOG_LEVEL=INFO
```

**快速配置**：运行 `python quick_setup_api.py` 或 `setup_domain.bat`

## 添加新API适配器

**按顺序修改4个文件**：

1. **创建适配器**（`src/api/adapters/newapi_adapter.py`）
```python
from .base_adapter import BaseAPIAdapter

class NewAPIAdapter(BaseAPIAdapter):
    def generate_names(self, prompt: str, **kwargs) -> Dict[str, Any]:
        # 返回统一格式：{success, names: [{name, meaning, source}], api_name, model}
```

2. **添加配置**（`config/api_config.py`）
```python
class NewAPIConfig:
    name = "newapi"
    base_url = os.getenv("NEWAPI_BASE_URL", "https://api.example.com")
    api_key = os.getenv("NEWAPI_API_KEY", "")
    enabled = bool(api_key)
```

3. **注册到APIManager**（`config/api_config.py` 的 `APIManager.__init__()`）
```python
self.apis = {'newapi': NewAPIConfig(), ...}
```

4. **初始化适配器**（`src/api/unified_client.py` 的 `_initialize_adapters()`）
```python
if 'newapi' in self.api_manager.active_apis:
    from .adapters.newapi_adapter import NewAPIAdapter
    self.adapters['newapi'] = NewAPIAdapter(config)
```

5. **更新优先级**（可选，`config/api_config.py` 的 `get_primary_api()` 中的 `priority_order` 列表）

## 调试与故障排查

### 快速诊断

```bash
# 1. 检查后端健康
curl http://127.0.0.1:5000/health  # 应返回 {"status": "ok"}

# 2. 查看API配置（启动时自动显示）
cd NameGenerationAgent
python main.py

# 3. 查看日志（实时）
Get-Content .\logs\app.log -Wait -Tail 50  # PowerShell
tail -f logs/app.log                        # Git Bash/WSL
```

### 常见问题

**API适配器未初始化**（启动显示"已初始化 0 个API适配器"）
- 原因：`.env` 中未配置任何API密钥
- 解决：运行 `python quick_setup_api.py`

**循环导入错误**（`ImportError: cannot import name 'xxx' from partially initialized module`）
- 原因：模块顶层导入相互依赖的模块
- 解决：将导入语句移到函数内部（参考 `unified_client.py:102-220`）

**前端无法连接后端**
- 检查后端运行：`curl http://127.0.0.1:5000/health`
- 检查CORS：`.env` 中配置 `ALLOWED_ORIGINS`
- 检查防火墙：确保5000和5173端口开放
- 重启后端：修改 `.env` 后需重启

**Android连接问题**
- 模拟器：编辑 `智能姓名生成系统/common/api.ts`，设置 `BASE_URL = 'http://10.0.2.2:5000'`
- 真机：确保同一局域网，使用电脑局域网IP（`ipconfig | findstr "IPv4"`）
- 推荐：使用natapp公网地址（无需修改配置）

**语料库未加载**（提示"语料库数据库不存在"）
- 检查数据库：`NameGenerationAgent/data/names_corpus.db` 是否存在
- 重新生成：`cd data && python convert_csv_to_sqlite.py`
- 测试加载器：`python test_corpus_sqlite.py`
- 禁用语料库（可选）：编辑 `src/core/name_generator.py`，设置 `corpus_enhancer = None`

**缓存问题**
- 清除缓存：`rm -rf data/cache/*` 或 `curl -X POST http://127.0.0.1:5000/cache/clear`
- 临时禁用：`use_cache=False` 参数

## 部署与前端配置

### 内网穿透（开发测试）

```bash
cd NameGenerationAgent
start_natapp.bat                              # 启动natapp
setup_domain.bat                              # 配置CORS（选择"2. 配置natapp地址"）
# 重启后端应用配置
```

### 云服务器部署（生产环境）

```bash
cd /path/to/NameGenerationAgent
chmod +x deploy/deploy_to_server.sh
sudo ./deploy/deploy_to_server.sh            # 自动安装依赖、配置Nginx、SSL证书

# 运维命令
systemctl status nameagent                    # 查看服务状态
journalctl -u nameagent -f                    # 查看实时日志
systemctl restart nameagent                   # 重启服务
```

### 前端服务器配置

**前端API地址配置**（`智能姓名生成系统/common/api.ts`）：
```typescript
const BASE_URL = 'http://nameagent.natapp1.cc';  // 默认：natapp公网地址

// 修改为本地/其他地址
const BASE_URL = 'http://127.0.0.1:5000';        // 本地开发
const BASE_URL = 'http://10.0.2.2:5000';         // Android模拟器
const BASE_URL = 'http://192.168.x.x:5000';      // Android真机（局域网）
```

**CORS配置**（后端 `.env`）：
```bash
ALLOWED_ORIGINS=http://localhost:5173,http://127.0.0.1:5173,http://nameagent.natapp1.cc
```

---

## 开发注意事项

**Python环境**：
- 虚拟环境位置：根目录 `venv/`（不是`.venv/`）
- 依赖文件：`NameGenerationAgent/requirements.txt`
- Python版本：推荐 3.8+
- 激活命令：`venv\Scripts\activate`（Windows）或 `source venv/bin/activate`（Linux/Mac）

**数据库操作**：
- SQLite线程安全：`CorpusLoader` 每次查询创建新连接
- 数据库位置：`NameGenerationAgent/data/names_corpus.db`（179MB）
- 备份建议：定期备份数据库和CSV源文件（`data/archive/organized/`）

**测试**：
- 单元测试：`tests/test_basic.py` - 测试API适配器、降级策略、缓存
- 集成测试：`tests/test_corpus_integration.py` - 测试语料库加载器性能
- 手动测试：`curl -X POST http://127.0.0.1:5000/generate -H "Content-Type: application/json" -d '{"description": "聪明可爱的女孩", "count": 5}'`

---
