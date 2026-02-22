# 动态模型发现功能文档

## 功能概述

系统现在支持从各个AI平台动态获取可用的模型列表，用户可以在前端直接选择任意可用的模型进行姓名生成，无需手动配置。

## 架构设计

### 核心组件

1. **BaseAPIAdapter.list_models()** - 基类方法，所有适配器实现此方法
2. **ModelManager** - 模型管理器，负责缓存和统一管理
3. **API端点 `/models`** - RESTful接口，返回模型列表

### 支持的平台

| 平台 | 动态获取 | 说明 |
|------|---------|------|
| OpenAI | ✅ | 通过 `/v1/models` API获取 |
| 硅基流动 | ✅ | 通过 `/models` API获取 |
| Gemini | ✅ | 通过 `/v1beta/models` API获取 |
| 阿里云 | ⚠️ | 预定义列表（API暂不公开） |
| 派欧云 | ⚠️ | 预定义列表 |
| AI Studio | ⚠️ | 预定义列表 |

## API使用说明

### 1. 获取所有平台的模型列表

**请求：**
```bash
GET http://127.0.0.1:5000/models
```

**响应示例：**
```json
{
  "success": true,
  "models": {
    "aliyun": [
      {
        "id": "qwen-max",
        "name": "Qwen Max",
        "description": "通义千问超大规模语言模型，适用于复杂任务",
        "is_default": false
      },
      {
        "id": "qwen3-235b-a22b-thinking-2507",
        "name": "Qwen3 235B Thinking",
        "description": "通义千问3代思考模型",
        "is_default": true
      }
    ],
    "openai": [
      {
        "id": "gpt-4o",
        "name": "GPT-4o",
        "description": "OpenAI最新多模态模型",
        "is_default": true
      }
    ]
  },
  "platforms": ["aliyun", "openai", "siliconflow", "gemini", "paiou", "aistudio"],
  "total_count": 25
}
```

### 2. 获取特定平台的模型列表

**请求：**
```bash
GET http://127.0.0.1:5000/models?api=aliyun
```

**响应示例：**
```json
{
  "success": true,
  "api": "aliyun",
  "models": [
    {
      "id": "qwen-max",
      "name": "Qwen Max",
      "description": "通义千问超大规模语言模型，适用于复杂任务",
      "is_default": false
    }
  ],
  "count": 8
}
```

### 3. 强制刷新缓存

**请求：**
```bash
GET http://127.0.0.1:5000/models?refresh=true
```

**说明：** 模型列表默认缓存1小时，使用 `refresh=true` 参数可强制重新获取。

### 4. 使用指定模型生成姓名

**请求：**
```bash
POST http://127.0.0.1:5000/generate
Content-Type: application/json

{
  "description": "聪明可爱的女孩",
  "count": 5,
  "preferred_api": "aliyun",
  "model": "qwen-max"
}
```

**说明：** 在生成请求中添加 `model` 参数即可指定使用的模型。

## 缓存机制

### 缓存策略

- **缓存时间：** 1小时（3600秒）
- **缓存粒度：** 按平台缓存
- **失效策略：** 超时自动失效，支持手动刷新

### 缓存优势

1. **减少API调用：** 避免频繁请求模型列表
2. **提升响应速度：** 缓存命中时立即返回
3. **降低成本：** 减少对第三方API的依赖

### 缓存管理

```python
from src.api.model_manager import model_manager

# 清除特定平台缓存
model_manager.clear_cache('aliyun')

# 清除所有缓存
model_manager.clear_cache()

# 设置缓存时间（秒）
model_manager.set_cache_ttl(7200)  # 2小时
```

## 前端集成示例

### 1. 获取模型列表

```javascript
// 获取所有平台的模型
async function fetchAllModels() {
  const response = await fetch('http://127.0.0.1:5000/models');
  const data = await response.json();

  if (data.success) {
    console.log('可用平台:', data.platforms);
    console.log('模型总数:', data.total_count);

    // 遍历每个平台的模型
    for (const [platform, models] of Object.entries(data.models)) {
      console.log(`${platform}:`, models);
    }
  }
}

// 获取特定平台的模型
async function fetchPlatformModels(platform) {
  const response = await fetch(`http://127.0.0.1:5000/models?api=${platform}`);
  const data = await response.json();

  if (data.success) {
    return data.models;
  }
}
```

### 2. 动态生成模型选择器

```javascript
async function createModelSelector() {
  const response = await fetch('http://127.0.0.1:5000/models');
  const data = await response.json();

  if (!data.success) return;

  const selector = document.getElementById('model-selector');

  // 按平台分组
  for (const [platform, models] of Object.entries(data.models)) {
    const optgroup = document.createElement('optgroup');
    optgroup.label = platform.toUpperCase();

    models.forEach(model => {
      const option = document.createElement('option');
      option.value = `${platform}:${model.id}`;
      option.textContent = `${model.name} - ${model.description}`;
      option.selected = model.is_default;
      optgroup.appendChild(option);
    });

    selector.appendChild(optgroup);
  }
}
```

### 3. 使用选定模型生成姓名

```javascript
async function generateWithModel(description, platform, modelId) {
  const response = await fetch('http://127.0.0.1:5000/generate', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      description: description,
      count: 5,
      preferred_api: platform,
      model: modelId
    })
  });

  const result = await response.json();
  return result;
}
```

## 添加新平台支持

### 1. 实现 list_models() 方法

```python
class NewAPIAdapter(BaseAPIAdapter):
    def list_models(self) -> List[Dict[str, Any]]:
        """获取平台可用的模型列表"""
        if not self.is_available():
            return []

        try:
            # 调用平台API获取模型列表
            response = self._make_request("models", {}, method='GET')

            models = []
            for model_data in response.get('data', []):
                models.append({
                    'id': model_data['id'],
                    'name': model_data['name'],
                    'description': model_data.get('description', ''),
                    'is_default': model_data['id'] == self.config.model
                })

            return models
        except Exception as e:
            logger.warning(f"获取模型列表失败: {str(e)}")
            return self._get_default_models()

    def _get_default_models(self) -> List[Dict[str, Any]]:
        """返回默认模型列表（备用）"""
        return [
            {
                'id': 'default-model',
                'name': 'Default Model',
                'description': '默认模型',
                'is_default': True
            }
        ]
```

### 2. 支持动态模型选择

```python
def generate_names(self, prompt: str, **kwargs) -> Dict[str, Any]:
    # 支持动态指定模型
    model = kwargs.get('model', self.config.model)

    # 使用指定的模型进行生成
    data = {
        'model': model,
        'messages': [...]
    }

    response = self._make_request('chat/completions', data)
    # ...
```

## 故障排查

### 问题1：模型列表为空

**原因：** API密钥未配置或平台未启用

**解决：**
```bash
# 检查.env文件
cat .env | grep API_KEY

# 确保至少配置一个API密钥
ALIYUN_API_KEY=your_key_here
```

### 问题2：获取模型超时

**原因：** 网络连接问题或API响应慢

**解决：**
- 使用 `refresh=false` 依赖缓存
- 增加超时时间（在适配器中修改 `timeout` 参数）
- 检查网络连接

### 问题3：模型ID不匹配

**原因：** 不同平台的模型ID格式不同

**解决：**
- 使用 `/models` 端点查看正确的模型ID
- 参考各平台的官方文档

## 性能优化建议

1. **前端缓存：** 在前端也缓存模型列表，减少请求
2. **懒加载：** 只在用户打开模型选择器时才加载
3. **预加载：** 应用启动时预加载常用平台的模型
4. **增量更新：** 只刷新变化的平台

## 未来改进

- [ ] 支持模型能力标签（如：支持流式、支持函数调用）
- [ ] 模型性能评分和推荐
- [ ] 模型使用统计和热度排行
- [ ] 自动检测新模型上线
- [ ] 模型价格信息展示
