# NameGenerationAgent 名字生成智能体

NameGenerationAgent 是一个智能名字生成系统，可以根据不同的风格、文化背景和主题生成各种类型的名字。

## 功能特点

- 支持多种文化背景的名字生成（中文、日文、英文等）
- 多种主题风格（古风、现代、动漫、游戏等）
- 基于真实数据集的高质量名字库
- 可扩展的插件式架构

## 数据来源

本项目使用的数据来源于公开的中文名字语料库，包含超过300万条名字数据：

- 中文人名语料库（120万条）
- 古代人名语料库（25万条）
- 日文人名语料库（18万条）
- 英文人名语料库（48万条）
- 姓氏库（1000+条）
- 成语词典（5万条）
- 称呼关系词典（4800条）
- 主题名字库（动漫、游戏等）

## 数据库使用

项目现在使用SQLite数据库存储所有名字数据，提高了查询效率和数据管理的便利性。

### 数据库文件

- 位置：`data/names.db`
- 包含9个数据表：
  - `chinese_names`: 中文人名
  - `ancient_names`: 古代人名
  - `family_names`: 姓氏库
  - `idioms`: 成语词典
  - `japanese_names`: 日文人名
  - `english_names`: 英文人名
  - `relationships`: 称呼关系
  - `poetic_names`: 诗词名字
  - `thematic_names`: 主题名字

### 数据转换

CSV数据已转换为SQLite数据库，转换脚本位于 `data/convert_csv_to_sqlite.py`。

如果需要重新转换数据：
```bash
cd data
python convert_csv_to_sqlite.py
```

## 使用方法

1. 确保已安装依赖：
   ```bash
   pip install pandas
   ```

2. 运行测试脚本验证数据库连接：
   ```bash
   python test_agent.py
   ```

3. 在Vue前端中，可以通过API调用后端接口来获取名字数据。

## 配置文件

- `config/db_config.py`: 数据库配置和访问接口

## 项目结构

```
NameGenerationAgent/
├── config/
│   └── db_config.py          # 数据库配置
├── data/
│   ├── organized/            # 原始CSV数据
│   ├── names.db              # SQLite数据库文件
│   ├── convert_csv_to_sqlite.py  # CSV转SQLite脚本
│   └── schema_design.md      # 数据库模式设计
├── src/
│   └── backend/              # 后端代码
├── src/
│   └── frontend/             # Vue前端代码
├── test_agent.py             # 测试脚本
└── README.md
```

## 注意事项

1. 首次运行时，系统会自动检查数据库文件是否存在，如果不存在则尝试运行转换脚本创建数据库。
2. 原始CSV数据文件位于 `data/organized/` 目录下，不要删除这些文件，因为在数据库损坏时可以用来重新生成。
3. 如果需要更新数据，修改CSV文件后重新运行转换脚本即可。

## 技术栈

- 后端：Python + SQLite
- 前端：Vue.js + Element Plus
- 数据处理：pandas

## License

MIT