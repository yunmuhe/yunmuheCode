# 中文人名语料库集成指南

## 📚 语料库概述

本项目集成了 **Chinese-Names-Corpus** 中文人名语料库，包含：

- **120万现代中文人名** （含性别标注）
- **25万古代中文人名**
- **5万成语词典**
- **性别分类**: 男性、女性、未知
- **风格分类**: 现代、古代

数据来源：[Chinese-Names-Corpus](https://github.com/wainshine/Chinese-Names-Corpus)

---

## 🗂️ 数据结构

### 目录布局

```
C:\名字生成智能体\
├── Chinese-Names-Corpus-master/     # 语料库数据（需单独下载）
│   ├── Chinese_Names_Corpus/
│   │   ├── Chinese_Names_Corpus（120W）.txt
│   │   ├── Chinese_Names_Corpus_Gender（120W）.txt
│   │   └── Ancient_Names_Corpus（25W）.txt
│   └── Chinese_Dict_Corpus/
│       └── ChengYu_Corpus（5W）.txt
│
└── NameGenerationAgent/             # 项目代码
    └── src/
        ├── data/
        │   └── corpus_loader.py     # 语料库加载器
        └── core/
            └── corpus_enhancer.py   # 语料库增强器
```

### 数据格式

#### 1. 现代人名（带性别）
```csv
dict,sex
张伟,男
李娜,女
王芳,女
```

#### 2. 古代人名
```
李白
杜甫
苏轼
```

#### 3. 成语词典
```
龙凤呈祥
锦绣前程
文质彬彬
```

---

## 🛠️ 核心模块

### 1. CorpusLoader (语料库加载器)

**位置**: `src/data/corpus_loader.py`

**功能**:
- 加载和缓存人名数据
- 性别筛选
- 风格筛选（现代/古代）
- 随机取名
- 关键词搜索
- 成语取名

**使用示例**:

```python
from src.data.corpus_loader import get_corpus_loader

# 获取加载器实例
loader = get_corpus_loader()

# 获取统计信息
stats = loader.get_stats()
print(stats)
# 输出: {'现代人名总数': 1144630, '古代人名总数': 253126, ...}

# 获取随机男性人名
male_names = loader.get_random_names(count=10, gender='男')
for name_info in male_names:
    print(f"{name_info['name']} ({name_info['gender']})")

# 获取随机古代人名
ancient_names = loader.get_random_names(count=10, style='ancient')

# 根据字符搜索人名
names = loader.search_names_by_char('明', gender='男', limit=20)

# 获取适合取名的成语
chengyus = loader.get_chengyu_for_naming(count=10)
for item in chengyus:
    print(f"{item['chengyu']} → {item['suggested_chars']}")
```

### 2. CorpusEnhancer (语料库增强器)

**位置**: `src/core/corpus_enhancer.py`

**功能**:
- 增强提示词（添加语料库示例）
- 基于关键词推荐姓名
- 成语取名
- 姓名质量评估

**使用示例**:

```python
from src.core.corpus_enhancer import get_corpus_enhancer

# 获取增强器实例
enhancer = get_corpus_enhancer()

# 基于关键词获取姓名建议
suggestions = enhancer.get_name_suggestions(
    keywords=['勇敢', '智慧'], 
    gender='male', 
    count=10
)

# 获取成语姓名
chengyu_names = enhancer.get_chengyu_names(count=5)
for name_info in chengyu_names:
    print(f"{name_info['name']} - {name_info['meaning']}")
# 输出: 诗雅 - 取自成语「诗情画意」

# 增强提示词
enhanced_prompt = enhancer.enhance_prompt(
    description="勇敢的战士",
    options={'gender': 'male', 'cultural_style': 'chinese_modern'}
)
```

---

## 🚀 集成使用

### 方式一：直接使用语料库推荐

适合需要快速获取真实人名的场景：

```python
from src.data.corpus_loader import get_corpus_loader

loader = get_corpus_loader()

# 场景1: 需要真实的中文人名
names = loader.get_random_names(count=5, gender='女', style='modern')

# 场景2: 需要古代风格人名
ancient = loader.get_random_names(count=5, style='ancient')

# 场景3: 基于成语取名
chengyus = loader.get_chengyu_for_naming(count=5)
```

### 方式二：结合大模型生成

使用语料库数据增强提示词，让大模型生成更符合中文习惯的姓名：

```python
from src.core.corpus_enhancer import get_corpus_enhancer
from src.core.name_generator import name_generator

enhancer = get_corpus_enhancer()

# 1. 获取语料库示例作为参考
examples = enhancer._get_style_examples('chinese_modern', gender='男')

# 2. 构建增强提示词
prompt = f"""
请为以下角色生成中文姓名：
描述：勇敢的战士

参考示例（真实人名）：{', '.join(examples[:5])}

要求：
1. 生成5个符合中文习惯的姓名
2. 每个姓名附带含义解释
"""

# 3. 调用大模型生成
result = name_generator.generate_names(
    description=prompt,
    count=5
)
```

### 方式三：混合推荐

同时使用语料库推荐和大模型生成：

```python
# 1. 从语料库获取真实人名
corpus_names = loader.get_random_names(count=3, gender='男')

# 2. 从成语获取诗意人名
chengyu_names = enhancer.get_chengyu_names(count=2)

# 3. 从大模型获取创意人名
ai_names = name_generator.generate_names(description="勇敢的战士", count=5)

# 4. 合并结果
all_names = corpus_names + chengyu_names + ai_names['names']
```

---

## 🧪 测试脚本

运行测试脚本验证集成：

```bash
python test_corpus.py
```

**测试内容**:
- ✅ 语料库加载器初始化
- ✅ 统计信息获取
- ✅ 随机人名获取（现代/古代，男/女）
- ✅ 成语取名功能
- ✅ 语料库增强器功能
- ✅ 关键词搜索

---

## 📊 性能优化

### 缓存机制

语料库数据在首次加载后会缓存在内存中，后续访问速度极快：

```python
loader = get_corpus_loader()

# 首次加载（需要读取文件，较慢）
names1 = loader.load_names()  # ~2-3秒

# 后续访问（从缓存读取，极快）
names2 = loader.load_names()  # <0.001秒
```

### 数据量控制

如果只需要少量数据，使用 `limit` 参数：

```python
# 只加载前1000条
names = loader.load_names(limit=1000)

# 随机获取10个
random_names = loader.get_random_names(count=10)
```

---

## 🎯 应用场景

### 1. 真实人名验证
检查生成的姓名是否为真实存在的中文人名：

```python
def is_real_name(name):
    names_list = loader.load_names()
    return name in names_list
```

### 2. 姓名推荐系统
基于用户输入的关键词推荐真实人名：

```python
keywords = ['明', '智']
suggestions = enhancer.get_name_suggestions(keywords, gender='male', count=10)
```

### 3. 诗词风格取名
使用成语为角色取富有文化内涵的名字：

```python
chengyu_names = enhancer.get_chengyu_names(count=5)
```

### 4. 性别分类训练
使用带性别标注的120万人名训练性别分类模型：

```python
names_with_gender = loader.load_names(with_gender=True)
# 用于机器学习训练
```

---

## 🔧 配置说明

### 自定义语料库路径

默认路径为项目上级目录的 `Chinese-Names-Corpus-master`，可自定义：

```python
from src.data.corpus_loader import CorpusLoader

# 使用自定义路径
loader = CorpusLoader(corpus_path='/path/to/Chinese-Names-Corpus-master')
```

### 环境变量配置

可在 `.env` 文件中配置：

```env
# 语料库路径（可选）
CORPUS_PATH=C:\名字生成智能体\Chinese-Names-Corpus-master
```

---

## 📝 数据更新

如需更新语料库数据：

1. 访问 [Chinese-Names-Corpus](https://github.com/wainshine/Chinese-Names-Corpus)
2. 下载最新版本
3. 替换 `Chinese-Names-Corpus-master` 目录
4. 重启应用（缓存会自动更新）

---

## ⚠️ 注意事项

### 1. 数据位置
确保语料库位于正确位置：
```
C:\名字生成智能体\Chinese-Names-Corpus-master\
```

### 2. 文件编码
所有语料库文件使用 UTF-8 编码。

### 3. 内存占用
完整加载所有数据约需 200-300MB 内存。如需节省内存，使用 `limit` 参数。

### 4. 首次加载
首次加载语料库需要2-3秒，后续访问从缓存读取非常快。

---

## 🎉 总结

通过集成 Chinese-Names-Corpus 语料库，本系统现在拥有：

✅ **120万+真实人名数据**  
✅ **性别和风格分类**  
✅ **成语诗词取名**  
✅ **智能推荐算法**  
✅ **大模型+语料库混合生成**  

这使得姓名生成更加：
- **真实可信**: 基于真实人名数据
- **文化内涵**: 融入成语诗词
- **智能推荐**: 结合关键词和性别
- **多样选择**: 现代、古代、诗意多种风格

---

**享受智能姓名生成的乐趣！** 🚀

