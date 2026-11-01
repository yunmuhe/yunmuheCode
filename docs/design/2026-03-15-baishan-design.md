# 白山智算接入设计

## 目标

为项目新增独立的 `baishan` 供应商，按 OpenAI 兼容方式调用白山智算聊天补全接口，前端和统一路由中可像 `siliconflow`、`paiou` 一样单独选择。

## 现状

- 项目已有 `OpenAICompatibleAdapter`，`siliconflow`、`paiou` 复用这一层。
- 供应商配置集中在 `NameGenerationAgent/config/api_config.py`。
- 适配器注册集中在 `NameGenerationAgent/src/api/adapters/__init__.py`。
- 统一调度从 `APIManager.apis` 读取启用的供应商，再由 `build_adapters()` 构建。

## 方案

### 方案 A：新增独立 `baishan` 供应商，复用 OpenAI 兼容适配器

做法：
- 在 `config/api_config.py` 新增 `BaishanConfig`
- 在 `src/api/adapters/` 新增 `baishan_adapter.py`
- 在适配器注册入口导入 `baishan_adapter`
- 在路由优先级和可用 API 列表里纳入 `baishan`
- 增加针对配置和请求参数的测试

优点：
- 结构与现有兼容供应商保持一致
- 配置、模型、密钥互不污染
- 前端/API 列表能明确区分白山智算

缺点：
- 需要补一组配置和测试

### 方案 B：复用现有某个兼容供应商名，替换 base_url/model

优点：
- 改动更少

缺点：
- 容易把供应商配置混在一起
- 前端无法明确选择白山智算
- 后续排错不清晰

## 结论

采用方案 A。白山智算是新的独立供应商，但技术实现继续复用 `OpenAICompatibleAdapter`，不单独维护 `requests.post` 逻辑。

## 数据流

1. `.env` 提供 `BAISHAN_API_KEY`、`BAISHAN_MODEL`、可选 `BAISHAN_BASE_URL`
2. `BaishanConfig` 读取这些环境变量并暴露给统一 API 管理器
3. `build_adapters()` 构建 `BaishanAdapter`
4. `BaishanAdapter.generate_names()` 通过 `OpenAI(api_key=..., base_url=...)` 调 `chat.completions.create()`
5. 返回统一的 `success/names/raw_response/api_name/model` 结构

## 错误处理

- 未配置 `BAISHAN_API_KEY` 时，`baishan` 不会进入 active APIs
- OpenAI 客户端导入失败或调用失败时，沿用 `OpenAICompatibleAdapter` 的 `APIException` 包装
- 运行时传入 `model` 时，应优先覆盖配置默认模型

## 测试策略

- 配置测试：确认 `BaishanConfig` 正确读取 `BAISHAN_*` 环境变量
- 适配器测试：确认请求打到 `https://api.edgefn.net/v1`，模型为 `MiniMax-M2.5` 或运行时覆盖值
- 统一路由测试：确认启用后 `baishan` 出现在可用 API 列表中
