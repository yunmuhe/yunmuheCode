# 智能姓名生成系统（前端 · uni-app）

本前端通过 HTTP API 调用本地或远程部署的智能体（Flask 服务）完成姓名生成。已适配 `H5/小程序/APP` 多端的请求封装。

## 核心特性

- 多端支持：H5、微信小程序、Android/iOS APP
- 固定服务器地址：使用natapp公网映射地址，无需配置
- 主题系统：7种主题切换（浅色/深色/自动/蓝色/绿色/粉色/紫色）
- 收藏与历史：本地存储常用姓名和生成历史

## 一、运行后端（本地智能体）

1. 进入后端目录并安装依赖：
   ```bash
   pip install -r ../NameGenerationAgent/requirements.txt
   ```
2. 配置跨域来源（在 `../NameGenerationAgent/.env` 中）：
   ```env
   ALLOWED_ORIGINS=http://localhost:5173,http://127.0.0.1:5173,http://nameagent.natapp1.cc
   ```
3. 启动后端：
   ```bash
   python ../NameGenerationAgent/main.py
   ```
   后端默认地址：`http://127.0.0.1:5000`

## 二、配置前端 API 地址

前端使用固定的服务器地址（natapp公网映射）：`http://nameagent.natapp1.cc`

如需修改为本地地址或其他地址，编辑 `common/api.ts` 中的 `BASE_URL` 常量：

```typescript
// 固定服务器地址
const BASE_URL = 'http://127.0.0.1:5000';  // 本地开发
// const BASE_URL = 'http://nameagent.natapp1.cc';  // 公网访问
```

## 三、运行前端

### 使用 HBuilderX（推荐）

1. 用 HBuilderX 打开"智能姓名生成系统"目录
2. 点击"运行" → "运行到浏览器"或"运行到小程序模拟器"

### 使用命令行

```bash
# 安装依赖
npm install

# H5开发
npm run dev:h5

# 微信小程序开发
npm run dev:mp-weixin

# 构建
npm run build:h5
npm run build:mp-weixin
```

## 四、主要页面

- **Generate页面**：`pages/Generate/Generate.vue`
  - 请求后端 `/options` 拉取风格、性别、年龄、API 供应商
  - 请求后端 `/generate` 获取姓名结果并展示
  - 实时显示后端连接状态和版本号

- **Settings页面**：`pages/Settings/Settings.vue`
  - 显示当前服务器地址和连接状态
  - 偏好设置（默认生成数量、API提供商、风格）
  - 显示设置（主题模式、字体大小、动画效果）

- **History页面**：`pages/History/History.vue`
  - 生成历史记录查看

- **Favorites页面**：`pages/Favorites/Favorites.vue`
  - 收藏的姓名管理

## 五、常见问题

### CORS 报错

确认后端已安装 `Flask-Cors` 且 `.env` 中设置了正确的 `ALLOWED_ORIGINS`：

```env
ALLOWED_ORIGINS=http://localhost:5173,http://127.0.0.1:5173,http://nameagent.natapp1.cc
```

### 无法连接后端

1. 确认后端 `http://127.0.0.1:5000/health` 可访问
   ```bash
   curl http://127.0.0.1:5000/health
   ```
2. 检查防火墙是否阻止5000端口
3. 检查后端是否正常启动（查看终端输出）

### Android模拟器连接问题

如需在Android模拟器中访问本机后端：

1. 将 `common/api.ts` 中的 `BASE_URL` 改为：
   ```typescript
   const BASE_URL = 'http://10.0.2.2:5000';  // Android模拟器专用地址
   ```
2. 或使用natapp公网地址（无需修改代码）

### Android真机连接问题

如需在Android真机中访问本机后端：

1. 确保手机和电脑在同一局域网
2. 查看电脑局域网IP：
   ```bash
   ipconfig | findstr "IPv4"
   ```
3. 将 `common/api.ts` 中的 `BASE_URL` 改为：
   ```typescript
   const BASE_URL = 'http://192.168.x.x:5000';  // 替换为电脑IP
   ```
4. 或使用natapp公网地址（无需修改代码，推荐）

### H5开发时跨域问题

确保后端 `.env` 配置了本地开发地址：

```env
ALLOWED_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
```

修改后需要重启后端服务。

---

**技术栈**：Vue 3 + TypeScript + uni-app 3.0 + Vite
