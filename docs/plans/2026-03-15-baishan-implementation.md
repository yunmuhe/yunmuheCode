# 白山智算接入 Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** 为项目新增独立的 `baishan` 供应商，并按 OpenAI 兼容方式接入白山智算聊天补全接口。

**Architecture:** 复用现有 `OpenAICompatibleAdapter`，仅补 `BaishanConfig`、`BaishanAdapter` 和注册接线。避免新增独立 HTTP 调用栈，保持与 `siliconflow`、`paiou` 一致。

**Tech Stack:** Python, OpenAI Python SDK, pytest, PowerShell

---

### Task 1: 补配置层测试

**Files:**
- Modify: `NameGenerationAgent/tests/test_openai_compatible_adapter.py`
- Create: `NameGenerationAgent/tests/test_baishan_adapter.py`

**Step 1: Write the failing test**

- 写一个测试，断言 `BaishanAdapter` 使用 `https://api.edgefn.net/v1`
- 写一个测试，断言默认模型是 `MiniMax-M2.5`
- 写一个测试，断言运行时 `model` 可覆盖默认值

**Step 2: Run test to verify it fails**

Run: `python -m pytest NameGenerationAgent/tests/test_baishan_adapter.py -q`
Expected: FAIL，因为 `baishan_adapter.py` 尚不存在

**Step 3: Write minimal implementation**

- 新增 `baishan_adapter.py`
- 复用 `OpenAICompatibleAdapter`

**Step 4: Run test to verify it passes**

Run: `python -m pytest NameGenerationAgent/tests/test_baishan_adapter.py -q`
Expected: PASS

### Task 2: 补配置与注册接线

**Files:**
- Modify: `NameGenerationAgent/config/api_config.py`
- Modify: `NameGenerationAgent/src/api/adapters/__init__.py`
- Modify: `NameGenerationAgent/src/api/unified_client.py`

**Step 1: Write the failing test**

- 写一个测试，断言 `APIManager` 在配置 `BAISHAN_API_KEY` 后能激活 `baishan`

**Step 2: Run test to verify it fails**

Run: `python -m pytest NameGenerationAgent/tests/test_baishan_adapter.py -q`
Expected: FAIL，因为 `APIManager` 还没有 `baishan`

**Step 3: Write minimal implementation**

- 新增 `BaishanConfig`
- 把 `baishan` 加入 `APIManager.apis`
- 在适配器导入和默认路由优先级里加入 `baishan`

**Step 4: Run test to verify it passes**

Run: `python -m pytest NameGenerationAgent/tests/test_baishan_adapter.py -q`
Expected: PASS

### Task 3: 最小回归验证

**Files:**
- Test: `NameGenerationAgent/tests/test_baishan_adapter.py`
- Test: `NameGenerationAgent/tests/test_openai_compatible_adapter.py`

**Step 1: Run focused tests**

Run: `python -m pytest NameGenerationAgent/tests/test_baishan_adapter.py NameGenerationAgent/tests/test_openai_compatible_adapter.py -q`
Expected: PASS

**Step 2: Commit**

```bash
git add docs/plans/2026-03-15-baishan-design.md docs/plans/2026-03-15-baishan-implementation.md NameGenerationAgent/config/api_config.py NameGenerationAgent/src/api/adapters/__init__.py NameGenerationAgent/src/api/adapters/baishan_adapter.py NameGenerationAgent/src/api/unified_client.py NameGenerationAgent/tests/test_baishan_adapter.py
git commit -m "feat: add baishan provider"
```
