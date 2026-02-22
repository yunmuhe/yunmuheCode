# 智能姓名生成系统 - 架构图文档

本目录包含智能姓名生成系统的PlantUML架构图，用于可视化系统的核心模块、数据流和调用关系。

## 图表列表

### 1. 系统架构图 (architecture.puml)
**用途**: 展示系统的整体架构和模块划分

**包含内容**:
- Web层 (Flask API)
- Core层 (业务逻辑)
- API层 (AI平台适配器)
- Data层 (数据访问)
- Utils层 (工具类)
- Config层 (配置管理)
- 模块间的依赖关系

**适用场景**:
- 新开发者了解系统结构
- 技术方案评审
- 系统设计文档

### 2. 调用时序图 (sequence-diagram.puml)
**用途**: 展示一次完整的姓名生成请求的调用流程

**包含内容**:
- 从用户请求到响应的完整生命周期
- 参数验证流程
- 提示词构建过程
- 语料库增强逻辑
- API调用与缓存交互
- 异常处理与自动降级

**适用场景**:
- 理解系统运行流程
- 调试问题定位
- 性能优化分析

### 3. 类关系图 (class-diagram.puml)
**用途**: 展示核心类的设计和类之间的关系

**包含内容**:
- 适配器模式实现 (6个AI平台)
- 路由策略类层次 (Priority/Weighted/RoundRobin)
- 核心业务类 (NameGenerator, CorpusEnhancer)
- 工具类 (CacheManager, InputValidator, Logger)
- 配置类 (APIManager, PromptTemplates)

**适用场景**:
- 代码结构理解
- 设计模式学习
- 扩展开发参考

### 4. 数据流图 (data-flow-diagram.puml)
**用途**: 展示数据在系统中的流动路径

**包含内容**:
- 请求参数的传递
- 提示词的构建和增强
- 缓存的读写流程
- API调用的数据交换
- 结果的处理和返回

**适用场景**:
- 理解数据处理流程
- 性能瓶颈分析
- 数据一致性检查

### 5. 用例图 (use-case-diagram.puml)
**用途**: 展示系统的功能用例和用户交互

**包含内容**:
- 三类参与者（普通用户、开发者、系统管理员）
- 核心功能用例（生成姓名及其扩展）
- 查询功能用例（选项、历史、统计）
- 收藏管理用例
- 系统管理用例（健康检查、缓存管理、配置）
- 数据管理用例（语料库维护）
- 用例间的关系（include、extend）

**适用场景**:
- 需求分析和确认
- 用户手册编写
- 功能测试用例设计
- 产品演示和培训

**配套文档**: [use-case-specification.md](use-case-specification.md) - 详细的用例规约

### 6. 前后端交互时序图 (frontend-backend-interaction.puml)
**用途**: 展示前端（uni-app）与后端（Flask API）的完整交互流程

**包含内容**:
- APP启动初始化流程
- 用户生成姓名的完整交互
- 历史记录查询和搜索
- 收藏功能的CRUD操作
- 网络异常处理机制
- API自动降级流程

**适用场景**:
- 前端开发人员理解API调用
- 调试前后端交互问题
- 性能优化和错误处理
- 集成测试设计

**配套文档**: [API-DOCUMENTATION.md](API-DOCUMENTATION.md) - 完整的API文档

### 7. 数据模型图 (data-model-diagram.puml)
**用途**: 展示前后端数据传输的结构定义

**包含内容**:
- 请求数据模型（Frontend -> Backend）
- 响应数据模型（Backend -> Frontend）
- 会话数据模型（Session Storage）
- 前端本地存储模型（uni-app Storage）
- 数据字段详细说明和示例

**适用场景**:
- 前后端接口对接
- 数据结构设计和验证
- API文档编写
- 类型定义（TypeScript/JSON Schema）

**配套文档**: [API-DOCUMENTATION.md](API-DOCUMENTATION.md) - API规范文档

## 如何使用

### 在线渲染

使用PlantUML在线编辑器查看：
1. 访问 http://www.plantuml.com/plantuml/uml/
2. 复制对应的.puml文件内容
3. 粘贴到编辑器中即可查看

或者使用VS Code等编辑器：
1. 安装PlantUML插件
2. 打开.puml文件
3. 按 `Alt + D` 预览

### 导出图片

使用PlantUML命令行工具：
```bash
# 安装PlantUML (需要Java环境)
# 下载 plantuml.jar 从 http://plantuml.com/download

# 生成PNG图片
java -jar plantuml.jar architecture.puml

# 生成SVG矢量图
java -jar plantuml.jar -tsvg architecture.puml

# 批量生成所有图表
java -jar plantuml.jar *.puml
```

### VS Code插件

推荐安装以下VS Code扩展：
- **PlantUML**: 实时预览和导出PlantUML图表
- **Markdown Preview Enhanced**: 在Markdown中预览PlantUML

## 图表说明

### 系统分层

系统采用经典的分层架构：

```
┌─────────────────────────────────────┐
│  Web层 - Flask RESTful API          │
├─────────────────────────────────────┤
│  Core层 - 业务逻辑处理               │
├─────────────────────────────────────┤
│  API层 - AI平台集成（适配器模式）    │
├─────────────────────────────────────┤
│  Data层 - 数据访问（SQLite）         │
├─────────────────────────────────────┤
│  Utils层 - 工具类（缓存/日志/验证）  │
└─────────────────────────────────────┘
```

### 核心设计模式

1. **适配器模式** (Adapter Pattern)
   - 6个AI平台适配器继承自BaseAPIAdapter
   - 统一的generate_names()接口
   - 各平台差异在适配器内部处理

2. **策略模式** (Strategy Pattern)
   - RouterStrategy定义路由策略接口
   - 3种具体策略：Priority、Weighted、RoundRobin
   - 运行时可切换路由策略

3. **单例模式** (Singleton Pattern)
   - APIManager全局单例
   - CacheManager全局单例
   - UnifiedClient全局单例

4. **工厂模式** (Factory Pattern)
   - 适配器工厂：build_adapters()
   - 注册器模式：register_adapter()

### 自动降级机制

系统具有健壮的自动降级能力：

```
用户请求
    ↓
选择首选API (aliyun)
    ↓
调用失败？ → 是 → 选择下一个API (siliconflow)
    ↓ 否              ↓
返回结果 ← ← ← ← ← 调用失败？ → 是 → 继续降级...
```

降级优先级（可配置）：
1. aliyun (阿里云)
2. siliconflow (硅基流动)
3. openai (OpenAI)
4. gemini (Gemini)
5. paiou (派欧云)
6. aistudio (AI Studio)

### 缓存机制

系统使用多级缓存提升性能：

```
请求 → 计算缓存键(MD5) → 查询DiskCache
                           ↓
                    缓存命中？
                    ↙        ↘
                 是            否
                 ↓              ↓
            返回缓存        调用API
                              ↓
                          存入缓存
                              ↓
                          返回结果
```

缓存键计算：
```python
cache_key = md5(enhanced_prompt + json.dumps(options, sort_keys=True))
```

### 语料库增强

语料库增强流程：

```
1. 用户描述: "聪明可爱的女孩"
        ↓
2. 构建基础提示词
        ↓
3. 从SQLite查询示例: ["张雅婷", "李思琪", ...]
        ↓
4. 注入到提示词: "...参考以下真实姓名示例：..."
        ↓
5. 发送到AI API
        ↓
6. 获得更符合中文命名习惯的结果
```

数据库结构：
- **chinese_names**: 180万+现代中文姓名
- **ancient_names**: 40万+古代姓名
- **family_names**: 8万+姓氏数据

## 性能指标

根据架构设计，系统性能指标：

| 指标 | 数值 | 说明 |
|------|------|------|
| 缓存命中响应时间 | <50ms | DiskCache读取 |
| 语料库查询时间 | <100ms | SQLite查询10条 |
| API调用时间 | 2-4秒 | 取决于AI平台响应 |
| 降级切换时间 | <200ms | 路由策略计算 + 适配器切换 |
| 并发能力 | 50+ req/s | Gunicorn多worker部署 |

## 扩展开发

### 添加新的AI平台

参考类关系图中的适配器模式：

1. 创建适配器类继承BaseAPIAdapter
2. 实现generate_names()方法
3. 在APIManager中注册配置
4. 在适配器工厂中注册
5. 更新路由优先级

详细步骤参见 [CLAUDE.md](../CLAUDE.md)。

### 添加新的路由策略

参考类关系图中的策略模式：

1. 创建策略类继承RouterStrategy
2. 实现get_priority()方法
3. 在settings.py中注册策略名称
4. 在router_strategy.py的工厂中添加

### 添加新的数据源

参考数据流图中的数据访问层：

1. 创建Loader类
2. 实现查询方法
3. 在CorpusEnhancer中调用
4. 更新缓存策略

## 常见问题

### Q: 为什么使用适配器模式？
**A**: 不同AI平台的API接口格式不同，适配器模式可以：
- 统一调用接口，简化上层逻辑
- 隔离变化，平台API变更只影响对应适配器
- 易于扩展，添加新平台无需修改核心代码

### Q: 路由策略如何选择？
**A**: 根据使用场景选择：
- **Priority**: 生产环境推荐，按稳定性和成本优先
- **Weighted**: 需要负载均衡时使用
- **RoundRobin**: 测试环境或平均分配请求

### Q: 缓存会导致结果重复吗？
**A**: 不会。缓存键包含了：
- 提示词内容（已包含description）
- 所有参数（count, style, gender等）
- 相同参数才会命中缓存
- 可通过use_cache=false禁用缓存

### Q: 如何查看系统运行状态？
**A**: 通过API端点：
- `GET /health` - 健康检查
- `GET /stats` - 统计信息（API调用、缓存命中率）
- `GET /options` - 可用选项
- 查看日志文件 `logs/app.log`

## 相关文档

- [CLAUDE.md](../CLAUDE.md) - 完整的开发指南
- [README.md](../README.md) - 项目说明和快速开始
- [FIX_CULTURAL_STYLE.md](FIX_CULTURAL_STYLE.md) - 文化风格修复说明
- [CLEANUP_SUMMARY.md](../CLEANUP_SUMMARY.md) - 项目架构演进记录

## 图表总览

| 图表名称 | 文件名 | 类型 | 主要用途 | 配套文档 |
|---------|--------|------|---------|---------|
| 系统架构图 | architecture.puml | 组件图 | 展示模块划分和依赖关系 | - |
| 调用时序图 | sequence-diagram.puml | 时序图 | 展示完整调用流程 | - |
| 类关系图 | class-diagram.puml | 类图 | 展示类设计和继承关系 | - |
| 数据流图 | data-flow-diagram.puml | 数据流图 | 展示数据流动路径 | - |
| 用例图 | use-case-diagram.puml | 用例图 | 展示功能用例和用户交互 | use-case-specification.md |
| 前后端交互图 | frontend-backend-interaction.puml | 时序图 | 展示前后端完整交互流程 | API-DOCUMENTATION.md |
| 数据模型图 | data-model-diagram.puml | 类图 | 展示数据传输结构 | API-DOCUMENTATION.md |

## 文档总览

| 文档名称 | 文件名 | 类型 | 主要内容 |
|---------|--------|------|---------|
| 架构图说明 | README.md | 指南 | 所有图表的使用说明 |
| 用例规约 | use-case-specification.md | 规范 | 详细的用例描述和流程 |
| API文档 | API-DOCUMENTATION.md | 规范 | 完整的REST API规范 |

## 更新日志

- 2025-01-16: 创建初始版本，包含5个核心架构图和用例规约文档
- 2025-01-16: 新增前后端交互时序图、数据模型图和完整API文档
