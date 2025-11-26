# 智能姓名生成系统

一个基于多平台大语言模型的智能姓名生成系统，支持多种API提供商，具有现代化的Web界面。

## ✨ 功能特性

- 🤖 **多平台API支持**: 支持派欧云、Aistudio、阿里云、百度等多个LLM平台
- 📚 **120万人名语料库**: 集成Chinese-Names-Corpus，包含现代/古代人名、成语词典
- 🎨 **智能生成**: 结合大模型+语料库，生成具有文化内涵和真实性的姓名
- 🌐 **Web界面**: 现代化的Web界面，支持实时生成和API切换
- ⚡ **高性能**: 内置缓存机制，支持并发请求
- 🔄 **容错机制**: 自动故障转移和重试机制
- 📊 **统计分析**: 详细的API调用统计和性能监控
- 🎭 **多种风格**: 现代、古代、诗词成语等多种命名风格

## 🚀 快速开始

### 方法一：使用快速启动脚本（推荐）

**Windows系统**:
```cmd
quick_start.bat
```

脚本会自动：
1. 检查并创建 `.env` 文件
2. 运行系统诊断
3. 启动Web服务

### 方法二：手动启动

#### 1. 安装依赖
```bash
pip install -r requirements.txt
```

#### 2. 配置API密钥
运行快速设置工具：
```bash
python quick_setup_api.py
```

#### 3. 启动Web应用
```bash
python main.py
```

访问 http://localhost:5000 使用Web界面。

## 📚 语料库集成（可选）

本系统支持集成 **Chinese-Names-Corpus** 人名语料库，提供120万+真实人名数据。

### 下载语料库

1. 访问 [Chinese-Names-Corpus](https://github.com/wainshine/Chinese-Names-Corpus)
2. 下载并解压到项目上级目录：
   ```
   C:\名字生成智能体\Chinese-Names-Corpus-master\
   ```

### 整理和转换数据（推荐）

一键整理所有数据（txt和xlsx转csv，并分类存储）：

```bash
python organize_data.py
```

这将：
- 转换所有txt文件为csv
- 转换所有xlsx文件为csv
- 按类别分类存储（中文人名、姓氏、成语等10个分类）
- 生成数据目录清单

### 处理语料库数据（可选）

```bash
python process_corpus.py
```

这将处理原始数据并生成：
- 结构化JSON数据
- 姓氏库和名字库
- 高质量成语推荐
- 统计分析报告

### 语料库功能

- ✅ 120万现代人名（含性别标注）
- ✅ 25万古代人名
- ✅ 5万成语词典
- ✅ 智能姓氏和名字分离
- ✅ 基于关键词推荐真实人名
- ✅ 成语诗词风格取名
- ✅ 性别和风格筛选

详细说明：
- 使用指南：[CORPUS_INTEGRATION.md](CORPUS_INTEGRATION.md)
- 数据整理：[DATA_ORGANIZATION_GUIDE.md](DATA_ORGANIZATION_GUIDE.md)
- 数据处理：[DATA_PROCESSING_GUIDE.md](DATA_PROCESSING_GUIDE.md)

## 📁 项目结构

```
NameGenerationAgent/
├── main.py                 # 主启动脚本
├── quick_setup_api.py      # API密钥快速设置工具
├── quick_start.bat         # Windows快速启动脚本
├── requirements.txt        # Python依赖
├── env.example             # 环境变量配置示例
├── config/                 # 配置文件
│   ├── api_config.py       # API配置
│   ├── prompts.py          # 提示词模板
│   └── settings.py         # 系统设置
├── src/                    # 源代码
│   ├── api/                # API适配器层
│   │   ├── adapters/       # 各平台适配器
│   │   │   ├── paiou_adapter.py      # 派欧云适配器
│   │   │   ├── aistudio_adapter.py   # Aistudio适配器
│   │   │   ├── baidu_adapter.py      # 百度适配器
│   │   │   └── base_adapter.py       # 基础适配器
│   │   └── unified_client.py # 统一API客户端
│   ├── core/               # 核心功能
│   │   └── name_generator.py # 姓名生成器
│   ├── utils/              # 工具函数
│   │   ├── cache_manager.py # 缓存管理
│   │   ├── logger.py       # 日志系统
│   │   └── validation.py   # 数据验证
│   └── web/                # Web应用
│       ├── app.py          # Flask应用
│       └── templates/      # HTML模板
└── tests/                  # 测试文件
    └── test_basic.py       # 基础测试
```

## 🔧 配置说明

### 环境变量

复制 `env.example` 为 `.env` 并配置：

```env
# 派欧云API配置
PAIOU_API_KEY=your_paiou_api_key_here

# Aistudio大模型API配置
AISTUDIO_API_KEY=your_aistudio_api_key_here
AISTUDIO_API_URL=https://api-xxx.aistudio-app.com/v1
AISTUDIO_MODEL=qwen3:235b

# 其他平台API（可选）
BAIDU_API_KEY=your_baidu_api_key_here
SILICONFLOW_API_KEY=your_siliconflow_api_key_here
```

### 支持的API平台

系统支持多个API平台，可在Web界面切换：

- **派欧云**: 使用 DeepSeek-V3 模型
- **Aistudio**: 支持 Qwen3 等多种模型
- **百度千帆**: 文心一言系列
- **SiliconFlow**: 多种开源模型
- **阿里云**: 通义千问系列

## 🎯 使用方法

### Web界面

1. 启动应用：`python main.py`
2. 访问 http://localhost:5000
3. 输入角色描述
4. 选择文化风格、性别、年龄等参数
5. 点击生成按钮获取姓名建议

### API调用

```python
from src.core.name_generator import name_generator

# 生成姓名
result = name_generator.generate_names(
    description="勇敢的战士",
    count=5,
    cultural_style="chinese_modern",
    gender="male",
    age="adult"
)

if result['success']:
    for name in result['names']:
        print(f"{name['name']} - {name['meaning']}")
```

### uni-app 前端集成指南

> 本仓库提供的 `智能姓名生成系统/前端` 为 uni-app 工程，可以直接通过 HTTP API 与本地部署的智能体交互。

1. **启动本地智能体服务**
   ```bash
   pip install -r requirements.txt
   python main.py
   ```
   - 默认监听 `http://localhost:5000`
   - 如需限制跨域访问，可在 `.env` 中新增 `ALLOWED_ORIGINS=http://localhost:5173`（多个地址用逗号分隔）

2. **配置前端 API 地址**
   - 前端默认请求 `http://127.0.0.1:5000`
   - 可在构建脚本或 `uni-app` 项目的环境变量中设置：
     - `VITE_API_BASE_URL`
     - 或 `UNI_APP_API_BASE_URL`
   - 也可直接修改 `智能姓名生成系统/common/api.ts` 中的 `DEFAULT_BASE_URL`

3. **前端调用说明**
   - `POST /generate`：提交描述、风格、性别、年龄等参数，返回姓名列表
   - `GET /options`：获取可用风格、性别、年龄与已配置的 API 供应商
   - `GET /stats`：获取当前服务状态
   - `GET /health`：健康检查接口
   - uni-app 侧已封装请求方法，见 `智能姓名生成系统/common/api.ts`

4. **运行 uni-app 项目**
   - 使用 HBuilderX 或 CLI（如 `npm run dev:h5`）启动前端
   - 生成页面位于 `pages/Generate/Generate.vue`，可实时输入描述并查看生成结果

## 📊 性能特性

- **缓存机制**: 自动缓存生成结果，提高响应速度
- **并发支持**: 支持多个并发请求
- **故障转移**: API失败时自动切换到备用API
- **重试机制**: 自动重试失败的请求
- **性能监控**: 详细的API调用统计

## 🔍 故障排除

### 常见问题

1. **API密钥未设置**
   ```bash
   python quick_setup_api.py
   ```

2. **系统测试失败**
   ```bash
   python test.py
   ```

3. **Web应用无法启动**
   - 检查端口5000是否被占用
   - 检查Python依赖是否安装完整

### 日志查看

系统日志保存在 `logs/` 目录中，可以查看详细的错误信息。

## 📝 开发说明

### 添加新的API平台

1. 在 `src/api/adapters/` 中创建新的适配器
2. 在 `config/api_config.py` 中添加配置
3. 在 `src/api/unified_client.py` 中注册适配器

### 自定义提示词

在 `config/prompts.py` 中修改提示词模板。

## 📄 许可证

本项目仅供学习和研究使用。

## 🤝 贡献

欢迎提交Issue和Pull Request来改进项目。

---

**智能姓名生成系统** - 让AI为您的角色创造完美的姓名！