# 前后端数据交互详细文档

## 概述

智能姓名生成系统采用前后端分离架构：
- **前端**: uni-app 多端应用（H5、微信小程序、iOS/Android APP）
- **后端**: Flask RESTful API（Python）
- **通信协议**: HTTP/HTTPS + JSON
- **跨域支持**: CORS（通过环境变量配置）

## API端点总览

| 端点 | 方法 | 功能 | 权限 |
|------|------|------|------|
| `/` | GET | 系统信息 | 公开 |
| `/health` | GET | 健康检查 | 公开 |
| `/options` | GET | 获取可用选项 | 公开 |
| `/generate` | POST | 生成姓名（核心功能） | 公开 |
| `/stats` | GET | 系统统计信息 | 公开 |
| `/history` | GET | 最近一次生成历史 | 会话 |
| `/history/list` | GET | 分页历史记录列表 | 会话 |
| `/favorites` | GET/POST/DELETE | 收藏管理 | 会话 |

## 详细API规范

### 1. 系统信息 - GET /

**请求**:
```http
GET / HTTP/1.1
Host: 127.0.0.1:5000
```

**响应**:
```json
{
  "name": "智能姓名生成系统 API",
  "version": "1.0.0",
  "status": "running",
  "endpoints": {
    "health": "/health",
    "options": "/options",
    "generate": "/generate",
    "stats": "/stats",
    "history": "/history/list",
    "favorites": "/favorites"
  },
  "frontend": "uni-app (智能姓名生成系统)",
  "description": "基于多平台AI的智能中文姓名生成API"
}
```

---

### 2. 健康检查 - GET /health

**用途**: 监控系统状态，用于负载均衡健康检查

**请求**:
```http
GET /health HTTP/1.1
Host: 127.0.0.1:5000
```

**响应**:
```json
{
  "status": "healthy",
  "timestamp": "2025-01-16T10:30:00.000Z",
  "version": "1.0.0"
}
```

**前端使用场景**:
- APP启动时检查后端可用性
- 定时心跳检测（每30秒）
- 网络恢复后重连验证

---

### 3. 获取可用选项 - GET /options

**用途**: 前端初始化时获取所有可选参数

**请求**:
```http
GET /options HTTP/1.1
Host: 127.0.0.1:5000
```

**响应**:
```json
{
  "success": true,
  "options": {
    "cultural_styles": [
      {
        "value": "chinese_modern",
        "label": "中文现代",
        "description": "现代简约风格，适合当代人物"
      },
      {
        "value": "chinese_traditional",
        "label": "中文传统",
        "description": "传统典雅风格，蕴含深厚文化"
      },
      {
        "value": "chinese_classic",
        "label": "中文古典",
        "description": "古风古韵，适合古装角色"
      },
      {
        "value": "western",
        "label": "西方风格",
        "description": "西方人名风格"
      },
      {
        "value": "japanese",
        "label": "日式风格",
        "description": "日本和风姓名"
      },
      {
        "value": "fantasy",
        "label": "奇幻风格",
        "description": "奇幻小说、游戏角色"
      }
    ],
    "genders": [
      {"value": "male", "label": "男性"},
      {"value": "female", "label": "女性"},
      {"value": "neutral", "label": "中性"}
    ],
    "ages": [
      {"value": "child", "label": "儿童"},
      {"value": "teen", "label": "青少年"},
      {"value": "adult", "label": "成人"},
      {"value": "elder", "label": "长者"}
    ],
    "apis": ["aliyun", "siliconflow", "openai", "gemini", "paiou", "aistudio"],
    "dynasties": [
      "先秦", "秦", "汉", "晋", "南北朝", "隋", "唐",
      "五代十国", "宋", "元", "明", "清"
    ]
  }
}
```

**前端数据处理**:
```javascript
// uni-app示例
export default {
  data() {
    return {
      culturalStyles: [],
      genders: [],
      ages: [],
      dynasties: []
    }
  },
  async onLoad() {
    const res = await uni.request({
      url: 'http://127.0.0.1:5000/options',
      method: 'GET'
    })

    if (res.data.success) {
      this.culturalStyles = res.data.options.cultural_styles
      this.genders = res.data.options.genders
      this.ages = res.data.options.ages
      this.dynasties = res.data.options.dynasties
    }
  }
}
```

---

### 4. 生成姓名 - POST /generate ⭐核心接口

**用途**: 根据角色描述生成姓名列表

**请求头**:
```http
POST /generate HTTP/1.1
Host: 127.0.0.1:5000
Content-Type: application/json
Cookie: session=xxx  # 自动保存历史需要
```

**请求体（完整参数）**:
```json
{
  "description": "聪明可爱的女孩，活泼开朗，擅长绘画",
  "count": 5,
  "cultural_style": "chinese_modern",
  "gender": "female",
  "age": "child",
  "preferred_api": "aliyun",
  "use_cache": true,
  "preferred_surname": "李",
  "surname_weight": 0.8,
  "preferred_era": "唐",
  "era_weight": 0.7
}
```

**请求参数说明**:

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| description | string | ✅ | - | 角色描述（自然语言） |
| count | integer | ❌ | 5 | 生成数量（1-20） |
| cultural_style | string | ❌ | chinese_modern | 文化风格 |
| gender | string | ❌ | neutral | 性别 |
| age | string | ❌ | adult | 年龄段 |
| preferred_api | string | ❌ | null | 首选API平台 |
| use_cache | boolean | ❌ | true | 是否使用缓存 |
| preferred_surname | string | ❌ | "" | 指定姓氏 |
| surname_weight | float | ❌ | 1.0 | 姓氏权重（0-1） |
| preferred_era | string | ❌ | "" | 指定朝代（仅古典风格） |
| era_weight | float | ❌ | 1.0 | 朝代权重（0-1） |

**成功响应（200 OK）**:
```json
{
  "success": true,
  "names": [
    {
      "id": "name_1737012345678_1",
      "name": "李思语",
      "meaning": "思维活跃，语言天赋出众，善于表达内心感受",
      "source": "ai_generated",
      "features": {
        "surname": "李",
        "given_name": "思语",
        "pinyin": "lǐ sī yǔ",
        "stroke_count": 14,
        "five_elements": "木水金"
      }
    },
    {
      "id": "name_1737012345678_2",
      "name": "王雅琪",
      "meaning": "优雅文静，琴棋书画样样精通，气质出众",
      "source": "ai_generated",
      "features": {
        "surname": "王",
        "given_name": "雅琪",
        "pinyin": "wáng yǎ qí",
        "stroke_count": 16,
        "five_elements": "土木木"
      }
    }
  ],
  "api_name": "aliyun",
  "model": "qwen-max",
  "cache_hit": false,
  "generation_time": 2.34,
  "timestamp": "2025-01-16T10:30:00.000Z"
}
```

**错误响应（400 Bad Request）**:
```json
{
  "success": false,
  "error": "角色描述不能为空"
}
```

**错误响应（500 Internal Server Error）**:
```json
{
  "success": false,
  "error": "生成姓名失败: API调用超时"
}
```

**前端调用示例**:
```javascript
// uni-app示例
export default {
  data() {
    return {
      loading: false,
      names: []
    }
  },
  methods: {
    async generateNames() {
      this.loading = true

      try {
        const res = await uni.request({
          url: 'http://127.0.0.1:5000/generate',
          method: 'POST',
          header: {
            'Content-Type': 'application/json'
          },
          data: {
            description: this.description,
            count: this.count,
            cultural_style: this.selectedStyle,
            gender: this.selectedGender,
            age: this.selectedAge,
            use_cache: true
          }
        })

        if (res.data.success) {
          this.names = res.data.names
          // 显示成功提示
          uni.showToast({
            title: `成功生成${res.data.names.length}个姓名`,
            icon: 'success'
          })
        } else {
          // 显示错误信息
          uni.showToast({
            title: res.data.error || '生成失败',
            icon: 'none'
          })
        }
      } catch (error) {
        console.error('请求失败:', error)
        uni.showToast({
          title: '网络错误',
          icon: 'none'
        })
      } finally {
        this.loading = false
      }
    }
  }
}
```

---

### 5. 系统统计 - GET /stats

**用途**: 获取系统运行状态和统计信息

**请求**:
```http
GET /stats HTTP/1.1
Host: 127.0.0.1:5000
```

**响应**:
```json
{
  "success": true,
  "stats": {
    "available_apis": 3,
    "api_status": {
      "aliyun": {
        "enabled": true,
        "success_count": 1234,
        "error_count": 5,
        "avg_response_time": 2.3
      },
      "siliconflow": {
        "enabled": true,
        "success_count": 567,
        "error_count": 2,
        "avg_response_time": 1.8
      },
      "openai": {
        "enabled": false,
        "reason": "API密钥未配置"
      }
    },
    "cache_stats": {
      "total_size": 1024,
      "hits": 5678,
      "misses": 1234,
      "hit_rate": 0.821,
      "total_requests": 6912
    },
    "corpus_stats": {
      "total_names": 2280000,
      "tables": {
        "chinese_names": 1800000,
        "ancient_names": 400000,
        "family_names": 80000
      }
    }
  }
}
```

**前端使用场景**:
- 管理后台展示
- 性能监控面板
- API健康度指示器

---

### 6. 历史记录 - GET /history/list

**用途**: 分页获取用户生成历史

**请求**:
```http
GET /history/list?page=1&page_size=10&q=女孩 HTTP/1.1
Host: 127.0.0.1:5000
Cookie: session=xxx
```

**查询参数**:

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| page | integer | ❌ | 1 | 页码（从1开始） |
| page_size | integer | ❌ | 10 | 每页数量（最大50） |
| q | string | ❌ | "" | 搜索关键词（搜索描述） |

**响应**:
```json
{
  "success": true,
  "page": 1,
  "page_size": 10,
  "total": 53,
  "items": [
    {
      "id": "h_1737012345678",
      "description": "聪明可爱的女孩",
      "count": 5,
      "time": "2025-01-16T10:30:00.000Z",
      "names": ["李思语", "王雅琪", "张诗涵", "陈婉儿", "林晓彤"]
    },
    {
      "id": "h_1737012300000",
      "description": "勇敢坚强的男孩",
      "count": 3,
      "time": "2025-01-16T10:25:00.000Z",
      "names": ["张浩然", "李天翔", "王宇轩"]
    }
  ]
}
```

**前端分页实现**:
```javascript
export default {
  data() {
    return {
      historyList: [],
      currentPage: 1,
      pageSize: 10,
      total: 0,
      loading: false
    }
  },
  methods: {
    async loadHistory() {
      this.loading = true

      const res = await uni.request({
        url: 'http://127.0.0.1:5000/history/list',
        method: 'GET',
        data: {
          page: this.currentPage,
          page_size: this.pageSize,
          q: this.searchKeyword
        }
      })

      if (res.data.success) {
        this.historyList = res.data.items
        this.total = res.data.total
      }

      this.loading = false
    },

    onPageChange(page) {
      this.currentPage = page
      this.loadHistory()
    }
  }
}
```

---

### 7. 收藏管理 - /favorites

#### 7.1 获取收藏列表 - GET /favorites

**请求**:
```http
GET /favorites HTTP/1.1
Host: 127.0.0.1:5000
Cookie: session=xxx
```

**响应**:
```json
{
  "success": true,
  "items": [
    {
      "id": "f_1737012345678",
      "name": "李思语",
      "meaning": "思维活跃，语言天赋出众",
      "style": "chinese_modern",
      "gender": "female",
      "source": "ai_generated",
      "time": "2025-01-16T10:30:00.000Z"
    }
  ]
}
```

#### 7.2 添加收藏 - POST /favorites

**请求**:
```http
POST /favorites HTTP/1.1
Host: 127.0.0.1:5000
Content-Type: application/json
Cookie: session=xxx
```

**请求体**:
```json
{
  "id": "name_1737012345678_1",
  "name": "李思语",
  "meaning": "思维活跃，语言天赋出众",
  "style": "chinese_modern",
  "gender": "female",
  "source": "ai_generated"
}
```

**响应**:
```json
{
  "success": true,
  "item": {
    "id": "f_1737012345678",
    "name": "李思语",
    "meaning": "思维活跃，语言天赋出众",
    "style": "chinese_modern",
    "gender": "female",
    "source": "ai_generated",
    "time": "2025-01-16T10:30:00.000Z"
  }
}
```

#### 7.3 删除收藏 - DELETE /favorites

**请求**:
```http
DELETE /favorites HTTP/1.1
Host: 127.0.0.1:5000
Content-Type: application/json
Cookie: session=xxx
```

**请求体**:
```json
{
  "ids": ["f_1737012345678", "f_1737012300000"]
}
```

**响应**:
```json
{
  "success": true,
  "deleted": ["f_1737012345678", "f_1737012300000"]
}
```

---

## CORS跨域配置

### 服务端配置

在 `.env` 文件中配置允许的来源：

```bash
# 允许所有来源（开发环境）
ALLOWED_ORIGINS=*

# 或指定特定来源（生产环境推荐）
ALLOWED_ORIGINS=http://localhost:5173,http://127.0.0.1:5173,https://yourapp.com
```

### 前端配置

**uni-app manifest.json**:
```json
{
  "h5": {
    "devServer": {
      "proxy": {
        "/api": {
          "target": "http://127.0.0.1:5000",
          "changeOrigin": true,
          "pathRewrite": {
            "^/api": ""
          }
        }
      }
    }
  }
}
```

**前端请求示例**:
```javascript
// 使用代理（开发环境）
const API_BASE = process.env.NODE_ENV === 'development'
  ? '/api'  // 通过代理
  : 'http://127.0.0.1:5000'  // 直接访问

export const generateNames = (data) => {
  return uni.request({
    url: `${API_BASE}/generate`,
    method: 'POST',
    data
  })
}
```

---

## 会话管理

系统使用Flask Session存储用户数据：

**存储内容**:
- `last_generation`: 最近一次生成记录
- `history`: 历史记录列表（最多200条）
- `favorites`: 收藏列表（最多500条）

**会话配置**:
```python
# Flask配置
app.config['SECRET_KEY'] = 'your-secret-key'
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SECURE'] = True  # HTTPS环境
```

**前端Cookie处理**:
```javascript
// uni-app自动处理Cookie
// 确保request配置中包含：
uni.request({
  url: 'http://127.0.0.1:5000/generate',
  method: 'POST',
  withCredentials: true,  // 携带Cookie
  data: {...}
})
```

---

## 错误处理规范

### HTTP状态码

| 状态码 | 说明 | 场景 |
|--------|------|------|
| 200 | 成功 | 正常响应 |
| 400 | 请求错误 | 参数验证失败 |
| 404 | 未找到 | 端点不存在 |
| 500 | 服务器错误 | 内部错误、API调用失败 |

### 错误响应格式

```json
{
  "success": false,
  "error": "错误信息（用户可读）",
  "code": "ERROR_CODE",  // 可选，错误代码
  "details": {}  // 可选，详细信息
}
```

### 前端错误处理

```javascript
async function handleRequest() {
  try {
    const res = await uni.request({...})

    if (res.statusCode === 200 && res.data.success) {
      // 成功处理
      return res.data
    } else {
      // 业务错误
      throw new Error(res.data.error || '操作失败')
    }
  } catch (error) {
    // 网络错误或其他异常
    console.error('请求失败:', error)
    uni.showToast({
      title: error.message || '网络错误',
      icon: 'none'
    })
  }
}
```

---

## 性能优化建议

### 1. 缓存策略

**后端**:
- 生成结果自动缓存（TTL: 3600秒）
- 使用DiskCache持久化

**前端**:
```javascript
// 缓存可用选项（启动时获取一次）
const OPTIONS_CACHE_KEY = 'name_generator_options'
const CACHE_DURATION = 24 * 60 * 60 * 1000  // 24小时

async function getOptions() {
  const cached = uni.getStorageSync(OPTIONS_CACHE_KEY)
  if (cached && Date.now() - cached.timestamp < CACHE_DURATION) {
    return cached.data
  }

  const res = await uni.request({url: '/options', method: 'GET'})
  uni.setStorageSync(OPTIONS_CACHE_KEY, {
    data: res.data.options,
    timestamp: Date.now()
  })

  return res.data.options
}
```

### 2. 请求优化

**防抖处理**:
```javascript
import { debounce } from 'lodash'

export default {
  methods: {
    generateNames: debounce(async function() {
      // 生成逻辑
    }, 500)  // 500ms防抖
  }
}
```

**加载状态管理**:
```javascript
export default {
  data() {
    return {
      loading: false,
      names: []
    }
  },
  methods: {
    async generateNames() {
      if (this.loading) return  // 防止重复请求

      this.loading = true
      try {
        // 请求逻辑
      } finally {
        this.loading = false
      }
    }
  }
}
```

### 3. 离线支持

```javascript
// 检测网络状态
uni.onNetworkStatusChange((res) => {
  console.log('网络状态:', res.isConnected)
  if (!res.isConnected) {
    uni.showToast({
      title: '网络已断开',
      icon: 'none'
    })
  }
})

// 离线时使用缓存数据
async function fetchWithCache(url, options) {
  const cacheKey = `cache_${url}`

  try {
    const res = await uni.request({url, ...options})
    // 成功时缓存
    uni.setStorageSync(cacheKey, res.data)
    return res.data
  } catch (error) {
    // 失败时使用缓存
    const cached = uni.getStorageSync(cacheKey)
    if (cached) {
      console.warn('使用缓存数据')
      return cached
    }
    throw error
  }
}
```

---

## 安全建议

### 1. API密钥保护

❌ **不要**在前端存储API密钥
✅ **应该**在后端统一管理

### 2. 请求频率限制

前端实现:
```javascript
class RequestLimiter {
  constructor(maxRequests = 10, timeWindow = 60000) {
    this.requests = []
    this.maxRequests = maxRequests
    this.timeWindow = timeWindow
  }

  canRequest() {
    const now = Date.now()
    this.requests = this.requests.filter(t => now - t < this.timeWindow)

    if (this.requests.length >= this.maxRequests) {
      return false
    }

    this.requests.push(now)
    return true
  }
}

const limiter = new RequestLimiter(10, 60000)  // 每分钟最多10次

async function generateNames() {
  if (!limiter.canRequest()) {
    uni.showToast({
      title: '请求过于频繁，请稍后再试',
      icon: 'none'
    })
    return
  }

  // 继续请求
}
```

### 3. 输入验证

前端验证:
```javascript
function validateInput(description, count) {
  if (!description || description.trim().length === 0) {
    throw new Error('请输入角色描述')
  }

  if (description.length > 500) {
    throw new Error('角色描述不能超过500字')
  }

  if (count < 1 || count > 20) {
    throw new Error('生成数量必须在1-20之间')
  }

  return true
}
```

---

## 测试数据示例

### 测试用例1: 基础生成

**请求**:
```json
{
  "description": "聪明可爱的女孩",
  "count": 3
}
```

**预期响应**: 成功生成3个中文现代风格的女性姓名

### 测试用例2: 完整参数

**请求**:
```json
{
  "description": "勇敢善良的古代将军",
  "count": 5,
  "cultural_style": "chinese_classic",
  "gender": "male",
  "age": "adult",
  "preferred_era": "唐",
  "use_cache": false
}
```

**预期响应**: 成功生成5个唐代风格的男性姓名

### 测试用例3: 错误处理

**请求**:
```json
{
  "description": "",
  "count": 5
}
```

**预期响应**: 400错误，提示"角色描述不能为空"

---

## 相关文档

- [API端点详细说明](use-case-specification.md) - 用例规约
- [系统架构图](architecture.puml) - 系统整体架构
- [数据流图](data-flow-diagram.puml) - 数据流动路径
- [时序图](sequence-diagram.puml) - 完整调用流程
