# API快速参考指南

## 快速导航

| 需求 | 参考文档 | 相关图表 |
|------|---------|---------|
| 查看API端点列表 | [API文档 - 端点总览](#api端点总览) | - |
| 了解生成姓名接口 | [API文档 - POST /generate](#4-生成姓名---post-generate-核心接口) | [前后端交互图](frontend-backend-interaction.puml) |
| 查看数据格式 | [数据模型图](data-model-diagram.puml) | [API文档 - 请求响应示例](#) |
| 调试前后端交互 | [前后端交互图](frontend-backend-interaction.puml) | [API文档 - 错误处理](#错误处理规范) |
| 实现前端调用 | [API文档 - 前端示例](#前端调用示例) | [前后端交互图](frontend-backend-interaction.puml) |
| 配置CORS | [API文档 - CORS配置](#cors跨域配置) | - |
| 性能优化 | [API文档 - 性能优化](#性能优化建议) | [数据流图](data-flow-diagram.puml) |

## 核心接口速查

### 1. 生成姓名（最常用）

```javascript
// uni-app请求示例
const response = await uni.request({
  url: 'http://127.0.0.1:5000/generate',
  method: 'POST',
  header: {
    'Content-Type': 'application/json'
  },
  data: {
    description: '聪明可爱的女孩',  // 必填
    count: 5,                       // 可选，默认5
    cultural_style: 'chinese_modern', // 可选
    gender: 'female',               // 可选
    use_cache: true                 // 可选，默认true
  }
})

// 成功响应
if (response.data.success) {
  console.log(response.data.names)  // 姓名数组
}
```

### 2. 获取可用选项

```javascript
// 获取所有配置选项（APP启动时调用一次）
const response = await uni.request({
  url: 'http://127.0.0.1:5000/options',
  method: 'GET'
})

// 响应包含：文化风格、性别、年龄、朝代等选项
const options = response.data.options
```

### 3. 历史记录

```javascript
// 分页获取历史记录
const response = await uni.request({
  url: 'http://127.0.0.1:5000/history/list',
  method: 'GET',
  data: {
    page: 1,
    page_size: 10,
    q: '女孩'  // 可选，搜索关键词
  }
})
```

### 4. 收藏管理

```javascript
// 添加收藏
await uni.request({
  url: 'http://127.0.0.1:5000/favorites',
  method: 'POST',
  data: {
    name: '李思语',
    meaning: '思维活跃',
    style: 'chinese_modern'
  }
})

// 获取收藏列表
const response = await uni.request({
  url: 'http://127.0.0.1:5000/favorites',
  method: 'GET'
})

// 删除收藏
await uni.request({
  url: 'http://127.0.0.1:5000/favorites',
  method: 'DELETE',
  data: {
    ids: ['f_xxx_1', 'f_xxx_2']
  }
})
```

## 常见参数说明

### 文化风格 (cultural_style)

| 值 | 说明 | 适用场景 |
|----|------|---------|
| chinese_modern | 中文现代 | 当代人物、现实题材 |
| chinese_traditional | 中文传统 | 传统文化、历史小说 |
| chinese_classic | 中文古典 | 古装剧、武侠小说 |
| western | 西方风格 | 欧美人物 |
| japanese | 日式风格 | 日本动漫、和风作品 |
| fantasy | 奇幻风格 | 奇幻小说、游戏角色 |

### 性别 (gender)

| 值 | 说明 |
|----|------|
| male | 男性 |
| female | 女性 |
| neutral | 中性 |

### 年龄段 (age)

| 值 | 说明 |
|----|------|
| child | 儿童（0-12岁） |
| teen | 青少年（13-18岁） |
| adult | 成人（19-60岁） |
| elder | 长者（60岁以上） |

### AI平台 (preferred_api)

| 值 | 说明 | 特点 |
|----|------|------|
| aliyun | 阿里云百炼 | 稳定性高，支持降级 |
| siliconflow | 硅基流动 | 响应快速 |
| openai | OpenAI | 创意性强 |
| gemini | Google Gemini | 多语言支持好 |
| paiou | 派欧云 | 本地化优秀 |
| aistudio | AI Studio | 定制化能力强 |

## 错误码速查

| HTTP状态码 | 说明 | 常见原因 | 解决方案 |
|-----------|------|---------|---------|
| 200 | 成功 | - | - |
| 400 | 请求错误 | 参数缺失或格式错误 | 检查请求参数 |
| 404 | 未找到 | API端点不存在 | 检查URL是否正确 |
| 500 | 服务器错误 | API调用失败、内部错误 | 查看日志、重试 |

## 响应数据结构速查

### 成功响应

```typescript
interface SuccessResponse {
  success: true
  names: Array<{
    id: string
    name: string
    meaning: string
    source: string
    features: {
      surname: string
      given_name: string
      pinyin: string
      stroke_count?: number
      five_elements?: string
    }
  }>
  api_name: string
  model: string
  cache_hit: boolean
  generation_time: number
  timestamp: string
}
```

### 错误响应

```typescript
interface ErrorResponse {
  success: false
  error: string
  code?: string
  details?: object
}
```

## 前端最佳实践

### 1. 请求封装

```javascript
// utils/request.js
const API_BASE = 'http://127.0.0.1:5000'

export function request(options) {
  return new Promise((resolve, reject) => {
    uni.request({
      url: `${API_BASE}${options.url}`,
      method: options.method || 'GET',
      data: options.data,
      header: {
        'Content-Type': 'application/json',
        ...options.header
      },
      success: (res) => {
        if (res.statusCode === 200 && res.data.success) {
          resolve(res.data)
        } else {
          reject(new Error(res.data.error || '请求失败'))
        }
      },
      fail: (err) => {
        reject(err)
      }
    })
  })
}

// 使用
import { request } from '@/utils/request'

async function generateNames(description) {
  try {
    const data = await request({
      url: '/generate',
      method: 'POST',
      data: { description, count: 5 }
    })
    return data.names
  } catch (error) {
    uni.showToast({
      title: error.message,
      icon: 'none'
    })
  }
}
```

### 2. 加载状态管理

```javascript
export default {
  data() {
    return {
      loading: false
    }
  },
  methods: {
    async handleGenerate() {
      if (this.loading) return

      this.loading = true
      uni.showLoading({ title: '生成中...' })

      try {
        const names = await generateNames(this.description)
        this.names = names
      } finally {
        this.loading = false
        uni.hideLoading()
      }
    }
  }
}
```

### 3. 错误处理

```javascript
function handleError(error, context) {
  console.error(`[${context}] 错误:`, error)

  let message = '操作失败'

  if (error.message) {
    message = error.message
  } else if (error.errMsg) {
    if (error.errMsg.includes('timeout')) {
      message = '请求超时，请重试'
    } else if (error.errMsg.includes('fail')) {
      message = '网络错误，请检查网络连接'
    }
  }

  uni.showToast({
    title: message,
    icon: 'none',
    duration: 2000
  })
}
```

### 4. 缓存策略

```javascript
// 缓存配置选项
const OPTIONS_CACHE_KEY = 'app_options'
const CACHE_DURATION = 24 * 60 * 60 * 1000  // 24小时

async function getOptions() {
  try {
    const cached = uni.getStorageSync(OPTIONS_CACHE_KEY)
    const now = Date.now()

    if (cached && now - cached.timestamp < CACHE_DURATION) {
      console.log('使用缓存的选项数据')
      return cached.data
    }

    const response = await request({ url: '/options' })
    const options = response.options

    uni.setStorageSync(OPTIONS_CACHE_KEY, {
      data: options,
      timestamp: now
    })

    return options
  } catch (error) {
    // 失败时尝试使用缓存
    const cached = uni.getStorageSync(OPTIONS_CACHE_KEY)
    if (cached) {
      console.warn('使用过期的缓存数据')
      return cached.data
    }
    throw error
  }
}
```

## 调试技巧

### 1. 查看请求详情

```javascript
// 在uni-app中打印请求信息
uni.request({
  url: 'http://127.0.0.1:5000/generate',
  method: 'POST',
  data: { description: '测试' },
  success: (res) => {
    console.log('状态码:', res.statusCode)
    console.log('响应头:', res.header)
    console.log('响应体:', res.data)
  },
  fail: (err) => {
    console.error('请求失败:', err)
  }
})
```

### 2. 使用Postman测试

```bash
# POST /generate
POST http://127.0.0.1:5000/generate
Content-Type: application/json

{
  "description": "聪明可爱的女孩",
  "count": 5,
  "cultural_style": "chinese_modern"
}
```

### 3. 查看后端日志

```bash
# 实时查看日志
cd NameGenerationAgent
Get-Content .\logs\app.log -Wait -Tail 50

# 仅查看错误
Get-Content .\logs\app.log -Wait -Tail 50 | Select-String -Pattern "ERROR"
```

## 性能优化清单

- [ ] 启动时预加载配置选项（/options）
- [ ] 启用请求缓存（use_cache: true）
- [ ] 实现请求防抖（500ms）
- [ ] 本地缓存历史记录和收藏
- [ ] 离线时使用缓存数据
- [ ] 请求超时设置（30秒）
- [ ] 实现请求重试机制（最多3次）
- [ ] 分页加载历史记录
- [ ] 图片懒加载
- [ ] 使用虚拟列表（长列表）

## 安全检查清单

- [ ] 不在前端存储API密钥
- [ ] 使用HTTPS（生产环境）
- [ ] 实现请求频率限制
- [ ] 验证用户输入（前后端双重验证）
- [ ] 防止XSS攻击（转义用户输入）
- [ ] 使用HTTPOnly Cookie（会话管理）
- [ ] 实现CSRF保护（生产环境）
- [ ] 敏感信息加密传输
- [ ] 定期更新依赖包
- [ ] 日志脱敏（不记录密钥）

## 相关链接

- [完整API文档](API-DOCUMENTATION.md)
- [前后端交互时序图](frontend-backend-interaction.puml)
- [数据模型图](data-model-diagram.puml)
- [用例规约文档](use-case-specification.md)
- [系统架构图](architecture.puml)
