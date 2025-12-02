# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目概述

这是一个前后端分离的智能中文姓名生成系统：

- **后端（NameGenerationAgent）**：Flask API服务，集成6个AI平台（阿里云、硅基流动、百度、派欧云、AI Studio、白山云），采用适配器模式实现统一API接口，支持自动降级和缓存
- **前端（智能姓名生成系统）**：uni-app应用（Vue 3 + TypeScript），支持H5、小程序、APP多端部署
- **语料库**：120万+真实人名数据，用于提示词增强（可选）

## 常用命令

### 后端开发

```bash
# 环境设置（Windows）
cd NameGenerationAgent
..\venv\Scripts\activate      # 激活虚拟环境
pip install -r requirements.txt

# 快速启动（推荐，会自动检查配置）
quick_start.bat               # Windows批处理，自动检查.env并启动

# 手动启动
python main.py                # 主启动脚本（包含API诊断信息）
python src/web/app.py         # 直接启动Flask应用（跳过诊断）

# 快速配置API密钥
python quick_setup_api.py     # 交互式配置向导

# 域名/内网穿透配置
setup_domain.bat              # 配置CORS允许的域名
start_natapp.bat              # 启动natapp内网穿透（本地开发远程访问）

# 测试
python -m pytest tests/                           # 运行所有测试
python -m pytest tests/test_basic.py              # 运行单个测试文件
python -m pytest tests/test_basic.py::TestNameGenerator::test_get_available_options  # 运行特定测试
python -m pytest tests/ -v                        # 显示详细输出
python -m pytest tests/ -v -s                     # 显示print输出

# 代码质量（可选）
black src/          # 代码格式化
isort src/          # 导入语句排序
flake8 src/         # 代码风格检查
```

### 前端开发

```bash
cd 智能姓名生成系统
npm install                 # 安装依赖

# 开发运行
npm run dev:h5              # H5开发模式（浏览器访问 http://localhost:5173）
npm run dev:mp-weixin       # 微信小程序开发模式

# 构建
npm run build:h5            # H5生产构建（输出到 dist/build/h5/）
npm run build:mp-weixin     # 微信小程序构建

# 或使用HBuilderX
# 1. 用HBuilderX打开"智能姓名生成系统"目录
# 2. 点击"运行" -> "运行到浏览器"或"运行到小程序模拟器"
```

**技术栈**：Vue 3 + Vite + uni-app 3.0，构建输出位于 `dist/build/h5/`

### 语料库数据库（SQLite）

**重要提示**：语料库已完全迁移到SQLite数据库，旧的CSV文件已备份到 `data/archive/` 目录。

语料库数据库（228万+记录，179MB），位于 `NameGenerationAgent/data/names_corpus.db`：

```bash
cd NameGenerationAgent

# 测试语料库加载器
python test_corpus_sqlite.py

# 验证数据库
cd data
python verify_database.py

# 重新生成数据库（从archive/organized中的CSV文件）
python convert_csv_to_sqlite.py
```

**数据库表结构**（8个表）：
- `chinese_names` - 114万中文人名（男67万/女37万/未知9万）
- `ancient_names` - 25万古代人名
- `family_names` - 4千姓氏（带频率和来源）
- `idioms` - 5万成语（带类别：男孩/女孩/通用）
- `themed_names` - 214条主题名字（QQ网名、萌名等）
- `japanese_names` - 18万日文人名
- `english_names` - 46万英文人名（男性29万/女性17万，带中文翻译）
- `relationships` - 18万称呼关系词

**语料库加载器**（`src/data/corpus_loader.py`）：

语料库加载器使用SQLite数据库，每次查询创建新连接以保证线程安全。关键设计：
- 全局单例模式（`get_corpus_loader()`）避免重复初始化
- 使用 `sqlite3.Row` 支持列名访问
- 自动检查数据库文件存在性

```python
from src.data.corpus_loader import get_corpus_loader

loader = get_corpus_loader()

# 获取统计信息
stats = loader.get_stats()

# 加载中文人名（带性别）
names = loader.load_names(with_gender=True, limit=100)

# 随机获取人名
random_names = loader.get_random_names(count=10, gender='男', style='modern')

# 搜索包含特定字的人名
searched = loader.search_names_by_char('雨', gender='女', limit=20)

# 加载成语（用于取名）
chengyus = loader.get_chengyu_for_naming(count=10, category='女孩')

# 加载姓氏（按频率排序）
family_names = loader.load_family_names(limit=10, origin='Chinese')

# 加载英文人名
english_names = loader.load_english_names(gender='男性', limit=10)

# 加载古代人名
ancient = loader.load_ancient_names(limit=10)
```

**可选操作**（如需重新处理原始语料库）：
```bash
python organize_data.py     # 整理原始数据（txt/xlsx → csv）
python process_corpus.py    # 生成结构化数据（已弃用，改用SQLite）
```

## 核心架构

### 适配器模式（系统核心设计）

用于统一6个AI平台的接口，实现自动降级：

```
用户请求 → NameGenerator → UnifiedAPIClient
                                ↓
         按优先级尝试适配器 (aliyun → siliconflow → baishan → baidu → paiou → aistudio)
                                ↓
              成功：解析并缓存 | 失败：自动降级到下一个API
```

**关键组件**：
- `src/api/adapters/base_adapter.py` - 定义统一接口（`generate_names()` 抽象方法）
- `src/api/adapters/*_adapter.py` - 6个平台具体实现，处理不同请求/响应格式
- `src/api/unified_client.py` - 统一客户端，管理适配器优先级和降级逻辑（`_initialize_adapters()` 方法在 102-220行）
- `src/core/name_generator.py` - 核心业务逻辑，协调提示词构建、API调用和结果处理

**优先级顺序**：配置在 `config/api_config.py` 的 `get_primary_api()` 方法中

### 前端智能服务器发现

**问题**：Android模拟器/真机IP地址变化导致无法连接后端

**解决方案**（`智能姓名生成系统/common/api.ts:111-174`）：

1. 检查用户自定义服务器地址（`uni.storage`）并测试连通性
2. 如失效，根据平台生成候选地址列表：
   - Android: `10.0.2.2`（模拟器） + `192.168.10.x` + `192.168.1.x`
   - iOS: `localhost:5000`
   - H5: `127.0.0.1:5000`
3. 并行测试所有候选地址（`Promise.all` + `/health` 端点）
4. 选择响应最快的可用服务器

**关键函数**：`discoverServer()`, `testServerUrl()`, `setServerUrl()`, `ensureServerUrl()`

### 目录结构

```
名字生成智能体/
├── NameGenerationAgent/          # 后端Flask API服务
│   ├── config/
│   │   ├── api_config.py         # 多平台API配置（APIManager、6个Config类）
│   │   ├── prompts.py            # 提示词模板（5种风格）
│   │   └── settings.py           # 应用基础配置
│   ├── src/
│   │   ├── api/
│   │   │   ├── adapters/         # 6个平台适配器（base_adapter.py + 6个实现）
│   │   │   └── unified_client.py # 统一API客户端（降级逻辑）
│   │   ├── core/
│   │   │   ├── name_generator.py # 核心业务逻辑
│   │   │   ├── corpus_enhancer.py# 语料库增强器
│   │   │   └── knowledge_base.py # 知识库
│   │   ├── data/
│   │   │   └── corpus_loader.py  # 语料库加载器
│   │   ├── utils/
│   │   │   ├── cache_manager.py  # 缓存管理（MD5哈希）
│   │   │   ├── logger.py         # 日志管理
│   │   │   └── validation.py     # 输入输出验证
│   │   └── web/
│   │       └── app.py            # Flask应用（9个RESTful端点）
│   ├── main.py                   # 主启动脚本（包含API诊断）
│   └── quick_setup_api.py        # 交互式API配置向导
│
├── 智能姓名生成系统/              # 前端uni-app应用
│   ├── pages/                    # Generate/History/Favorites/Settings
│   ├── common/
│   │   ├── api.ts                # API请求封装（智能服务器发现）
│   │   ├── storage.ts            # 本地存储
│   │   └── theme.ts              # 主题管理
│   ├── manifest.json             # uni-app配置（vueVersion: "3"）
│   └── vite.config.js            # Vite构建配置
│
└── Chinese-Names-Corpus-master/  # 120万+人名语料库
```

### 姓名生成流程

```python
POST /generate → NameGenerator.generate_names()

1. 输入验证 (validation.py) - 描述长度、数量范围、参数合法性

2. 提示词构建 (prompts.py) - 基础模板 + 风格模板 + 性别/年龄要求 + 可选语料库增强

3. API调用 (unified_client.py:267-335)
   - 检查缓存 (MD5(prompt+params))
   - 按优先级尝试API，失败时自动降级
   - 各适配器处理平台特定的请求格式和认证

4. 响应解析 (各适配器) - 提取姓名列表，统一格式为 {name, meaning, source}
   注意：paiou_adapter.py:122-207 实现了5种正则解析模式应对AI输出不稳定性

5. 结果处理 (name_generator.py:235-266)
   - 生成唯一ID
   - 分析字符特征（笔画数、音韵、是否中文）
   - 添加元数据（创建时间、API来源）
   - 缓存成功结果

6. 返回 {success, names: [...], api_name, model, total_generated}
```

### 重要设计决策

1. **延迟导入（Lazy Import）**：为避免循环依赖，使用函数内导入
   - `unified_client.py:11-90` - `get_api_manager()`, `get_logger()`
   - `unified_client.py:102-220` - `_initialize_adapters()` 动态导入各适配器
   - `base_adapter.py:11-18` - `get_logger()`
   - **注意**：添加新功能时遵循此模式，避免模块顶层导入可能循环依赖的模块

2. **降级策略**：API按优先级顺序尝试，失败时自动切换
   - 默认优先级：aliyun → siliconflow → baishan → baidu → paiou → aistudio
   - 用户可通过 `preferred_api` 参数覆盖优先级
   - 全部失败时返回模拟数据（`use_mock_on_failure=True`）或错误

3. **缓存机制**：`CacheManager` 减少API调用
   - 缓存键：MD5(prompt + count + 其他参数)
   - 存储位置：`data/cache/`
   - 可通过 `use_cache=False` 禁用

4. **统一响应格式**：各适配器标准化响应为 `{success, names: [{name, meaning, source}], api_name, model, total_generated, generated_at}`

5. **配置加载顺序**：
   - `.env` 文件加载（`config/api_config.py` 中的 `load_env_file()`）
   - 环境变量读取（各 `*Config` 类的 `__init__()`）
   - API管理器初始化（`APIManager` 收集已启用的API）
   - 适配器注册（`UnifiedAPIClient._initialize_adapters()` 动态实例化）

### Flask API端点（`src/web/app.py`）

**核心端点**：
- `POST /generate` - 生成姓名
  - 参数：`description`（必需）, `count`, `cultural_style`, `gender`, `age`, `preferred_api`, `use_cache`
  - 返回：`{success, names: [...], api_name, model, total_generated}`
- `GET /options` - 获取可用选项（文化风格、性别、年龄、已配置的API列表）
- `GET /health` - 健康检查（前端服务器发现机制使用此端点）

**历史与收藏**：
- `GET /history/list` - 获取生成历史（支持分页）
- `POST /favorites` - 添加收藏
- `GET /favorites` - 获取收藏列表
- `DELETE /favorites/<id>` - 删除收藏

**统计与管理**：
- `GET /stats` - API统计信息（缓存命中率、各API调用次数等）
- `POST /cache/clear` - 清除缓存（可选）

**CORS配置**：通过 `.env` 中的 `ALLOWED_ORIGINS` 配置跨域来源（前端访问必需）

## 环境变量配置

必须在 `NameGenerationAgent/.env` 文件中配置至少一个API密钥：

```bash
# 至少配置一个API平台（推荐：派欧云或AI Studio）
PAIOU_API_KEY=sk_xxx
AISTUDIO_API_KEY=your_key
AISTUDIO_API_URL=https://api-xxx.aistudio-app.com/v1
AISTUDIO_MODEL=qwen3:235b

# 其他可选平台
ALIYUN_API_KEY=sk_xxx
SILICONFLOW_API_KEY=sk_xxx
BAISHAN_API_KEY=sk_xxx
BAIDU_API_KEY=sk_xxx

# 前端跨域配置（重要：APP远程访问必须配置）
# 本地开发
ALLOWED_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
# 生产环境（添加你的域名或内网穿透地址）
# ALLOWED_ORIGINS=https://api.yourdomain.com,https://xxx.natappfree.cc

# 可选配置
DEBUG=True
LOG_LEVEL=INFO
```

**快速配置**：
- API密钥：运行 `python quick_setup_api.py` 进行交互式配置
- 域名/CORS：运行 `setup_domain.bat` 配置远程访问地址

## 添加新API适配器

1. **创建适配器**（`src/api/adapters/newapi_adapter.py`）：
   ```python
   from .base_adapter import BaseAPIAdapter

   class NewAPIAdapter(BaseAPIAdapter):
       def generate_names(self, prompt: str, **kwargs) -> Dict[str, Any]:
           # 实现API调用，返回统一格式
           return {success, names: [{name, meaning, source}], api_name, model}
   ```

2. **添加配置**（`config/api_config.py`）：
   ```python
   class NewAPIConfig:
       name = "newapi"
       base_url = os.getenv("NEWAPI_BASE_URL", "https://api.example.com")
       api_key = os.getenv("NEWAPI_API_KEY", "")
       enabled = bool(api_key)
   ```

3. **注册到APIManager**（`config/api_config.py` 的 `APIManager.__init__()`）：
   ```python
   self.apis = {'newapi': NewAPIConfig(), ...}
   ```

4. **初始化适配器**（`src/api/unified_client.py` 的 `_initialize_adapters()`）：
   ```python
   if 'newapi' in self.api_manager.active_apis:
       from .adapters.newapi_adapter import NewAPIAdapter
       self.adapters['newapi'] = NewAPIAdapter(config)
   ```

5. **更新优先级**（`config/api_config.py` 的 `get_primary_api()` 中的 `priority_order` 列表）

## 语料库数据

项目包含 `Chinese-Names-Corpus-master` 目录，提供：
- 120万中文常见人名
- 1千中文姓氏
- 5千中文称呼词根
- 48万英文翻译人名
- 18万日文人名

语料库通过 `src/data/corpus_loader.py` 加载，由 `src/core/corpus_enhancer.py` 用于增强提示词。

## 调试与故障排查

### 快速诊断流程

**1. 检查后端健康状态**：
```bash
curl http://127.0.0.1:5000/health
# 应返回: {"status": "ok"}
```

**2. 查看API配置诊断**：
```bash
cd NameGenerationAgent
python main.py  # 启动时自动显示已配置API和初始化状态
```

**3. 手动检查API可用性**：
```python
from src.core.name_generator import name_generator
options = name_generator.get_available_options()
print(f"可用API: {options['apis']}")
```

### 日志查看

日志文件：`NameGenerationAgent/logs/app.log`
```bash
# Windows PowerShell
Get-Content .\logs\app.log -Wait -Tail 50
# Git Bash / WSL
tail -f logs/app.log
```

**日志级别**：在 `.env` 中配置 `LOG_LEVEL=DEBUG|INFO|WARNING|ERROR`

### 常见问题速查

**API适配器未初始化**：
- 症状：启动显示"已初始化 0 个API适配器"
- 原因：`.env` 文件中未配置任何API密钥
- 解决：运行 `python quick_setup_api.py` 或手动编辑 `.env` 文件

**循环导入错误**：
- 症状：`ImportError: cannot import name 'xxx' from partially initialized module`
- 原因：在模块顶层导入相互依赖的模块
- 解决：将导入语句移到函数内部（参考 `unified_client.py:102-220`）

**前端无法连接后端**：
- 检查后端是否运行：`curl http://127.0.0.1:5000/health`
- 检查CORS配置：在 `.env` 中添加 `ALLOWED_ORIGINS=http://localhost:5173`
- 检查防火墙：确保5000和5173端口未被阻止

**Android模拟器连接问题**：
- 检查本机IP：`ipconfig | findstr "IPv4"`
- 更新前端配置：`智能姓名生成系统/common/api.ts` 中的 `DEFAULT_BASE_URL_ANDROID`
- 配置防火墙允许5000端口：
  ```powershell
  # 以管理员身份运行
  New-NetFirewallRule -DisplayName "Flask Port 5000" -Direction Inbound -Protocol TCP -LocalPort 5000 -Action Allow
  ```
- 注：前端有自动服务器发现机制，会自动扫描 `10.0.2.2` 和 `192.168.x.x` 网段

**缓存问题**：
- 清除缓存：`rm -rf data/cache/*` 或 `curl -X POST http://127.0.0.1:5000/cache/clear`
- 临时禁用：`result = name_generator.generate_names(..., use_cache=False)`

**提示词格式问题**：
- 位置：`config/prompts.py` 中定义所有提示词模板
- 调试：检查 `logs/app.log` 中的完整提示词和API响应

**语料库未加载**：
- 症状：提示"语料库数据库不存在"或导入错误
- 检查数据库文件：`NameGenerationAgent/data/names_corpus.db` 是否存在
- 重新生成数据库：`cd data && python convert_csv_to_sqlite.py`
- 测试加载器：`python test_corpus_sqlite.py`
- 禁用语料库增强（可选）：编辑 `src/core/name_generator.py`，将 `corpus_enhancer` 设为 `None`

**数据库损坏**：
- 备份现有数据库：`mv data/names_corpus.db data/names_corpus.db.bak`
- 从CSV重新生成：确保 `data/archive/organized/` 目录下的CSV文件存在，运行 `python data/convert_csv_to_sqlite.py`

## 部署配置

### 本地开发测试（内网穿透）

```bash
cd NameGenerationAgent

# 1. 启动natapp（需先在 https://natapp.cn 注册）
start_natapp.bat

# 2. 配置CORS
setup_domain.bat
# 选择 "2. 配置natapp内网穿透地址"
# 输入natapp显示的地址（如 https://xxx.natappfree.cc）

# 3. 重启后端应用配置
```

### 生产环境部署（云服务器）

```bash
# 在服务器上执行
cd /path/to/NameGenerationAgent
chmod +x deploy/deploy_to_server.sh
sudo ./deploy/deploy_to_server.sh
```

**自动化部署脚本功能**（`deploy/deploy_to_server.sh`）：
- 安装系统依赖（Python3、Nginx、Certbot）
- 配置Python虚拟环境和环境变量
- 配置systemd服务（自动重启）
- 配置Nginx反向代理
- 配置SSL证书（Let's Encrypt）

**运维命令**：
```bash
systemctl status nameagent       # 查看服务状态
journalctl -u nameagent -f       # 查看实时日志
systemctl restart nameagent      # 重启服务
```

### CORS配置

后端必须配置允许的跨域来源：

```bash
# 编辑 NameGenerationAgent/.env
ALLOWED_ORIGINS=http://localhost:5173,https://api.yourdomain.com,https://xxx.natappfree.cc

# 或使用配置工具
setup_domain.bat
```

### APP端配置

1. APP → 设置 → 智能体连接 → 配置
2. 输入服务器地址（云服务器/内网穿透地址）
3. 测试连接 → 保存并使用

**前端自动发现**：首次启动或自定义URL失效时，APP会自动扫描局域网IP（Android: `10.0.2.2` + `192.168.x.x`，H5: `127.0.0.1`）

### 部署场景对比

| 方案 | 适用场景 | 成本 | 稳定性 |
|------|---------|------|--------|
| **内网穿透（natapp/ngrok）** | 开发测试 | 免费-¥50/月 | ⭐⭐⭐ |
| **云服务器 + 域名** | 生产环境 | ¥100+/月 | ⭐⭐⭐⭐⭐ |

详细配置参见：`后端域名配置指南.md` 和 `问题诊断和解决.md`

## 开发注意事项

### Python环境

- **虚拟环境**：项目使用独立虚拟环境（根目录 `.venv/`），避免全局污染
- **依赖管理**：所有依赖定义在 `NameGenerationAgent/requirements.txt`
- **Python版本**：推荐 Python 3.8+

### 数据库操作

- **SQLite线程安全**：`CorpusLoader` 每次查询创建新连接，避免跨线程共享连接
- **数据库位置**：默认 `NameGenerationAgent/data/names_corpus.db`（179MB）
- **备份建议**：定期备份数据库文件和CSV源文件（`data/archive/organized/`）

### API适配器开发

添加新API适配器时需要修改4个文件（按顺序）：
1. 创建 `src/api/adapters/newapi_adapter.py` - 实现具体适配器
2. 添加 `config/api_config.py` 中的 `NewAPIConfig` 类
3. 在 `APIManager.__init__()` 中注册配置
4. 在 `UnifiedAPIClient._initialize_adapters()` 中动态导入并初始化
5. （可选）更新 `get_primary_api()` 中的优先级顺序

### 前端API调用

前端使用智能服务器发现机制（`common/api.ts`），关键点：
- 首次启动或URL失效时自动扫描可用服务器
- Android平台特殊处理：`10.0.2.2`（模拟器）+ 局域网IP扫描
- 通过 `/health` 端点验证服务器可用性
- 用户可手动配置服务器地址（Settings页面）

### 测试策略

**单元测试**（`tests/test_basic.py`）：
- 测试各API适配器的独立功能
- 测试降级策略和缓存机制
- 使用 pytest fixture 管理测试数据

**集成测试**（`tests/test_corpus_integration.py`）：
- 测试语料库加载器与名字生成器的集成
- 验证数据库查询性能

**手动测试**：
```bash
# 测试完整流程
curl -X POST http://127.0.0.1:5000/generate \
  -H "Content-Type: application/json" \
  -d '{"description": "聪明可爱的女孩", "count": 5}'
```

---
