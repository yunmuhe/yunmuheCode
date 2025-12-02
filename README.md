，# 智能姓名生成系统（前端 · uni-app）

本前端通过 HTTP API 调用本地部署的智能体（Flask 服务）完成姓名生成。已适配 `H5/小程序/APP` 多端的请求封装。

## 核心特性

### 智能服务器发现机制

**问题背景**：Android模拟器/真机IP地址变化导致无法连接后端

**解决方案**（`common/api.ts:111-338`）：
1. **自动检测平台**：区分H5/Android/iOS,使用不同的默认地址
   - H5: `http://127.0.0.1:5000`
   - Android: `http://10.0.2.2:5000` (模拟器专用地址)
   - iOS: `http://localhost:5000`

2. **用户自定义地址优先**：
   - 检查本地存储的自定义服务器地址
   - 测试连通性，如可用则直接使用

3. **自动网络扫描**：
   - 如自定义地址失效，生成候选地址列表：
     - Android: `10.0.2.2` + `192.168.10.x` + `192.168.1.x` (x=1-255)
     - iOS/H5: `localhost` + `127.0.0.1`
   - 并行测试所有候选地址（`Promise.all` + `/health` 端点）
   - 选择第一个响应成功的服务器

4. **页面启动时自动检查**：
   - Generate页面 `onLoad` 时调用 `ensureServerUrl()`
   - 如当前地址不可用，自动触发服务器发现

### API函数

- `ensureServerUrl()`: 确保服务器地址可用，启动时自动调用
- `discoverServer()`: 自动发现可用服务器（Settings页面"自动发现"按钮）
- `setServerUrl(url)`: 手动设置服务器地址（Settings页面"手动配置"按钮）
- `getCustomServerUrl()`: 获取用户自定义地址
- `clearCustomServerUrl()`: 清除自定义地址，恢复默认（Settings页面"恢复默认"按钮）

## 一、运行后端（本地智能体）

1. 进入后端目录并安装依赖：
   ```bash
   pip install -r ../NameGenerationAgent/requirements.txt
   ```
2. 可选：在 `../NameGenerationAgent/.env` 中配置跨域来源（H5 调试时建议写入本机端口）：
   ```env
   ALLOWED_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
   ```
3. 启动后端：
   ```bash
   python ../NameGenerationAgent/main.py
   ```
   后端默认地址：`http://127.0.0.1:5000`

## 二、配置前端 API 地址

### 方式1：环境变量（构建时配置）

前端默认会根据平台自动选择地址。如需覆盖，可使用环境变量：
- `VITE_API_BASE_URL=http://127.0.0.1:5000`
- 或 `UNI_APP_API_BASE_URL=http://127.0.0.1:5000`

### 方式2：Settings页面配置（推荐，运行时配置）

1. 打开APP → 设置页面 → 智能体连接
2. 点击"手动配置"按钮，输入服务器地址
3. 或点击"自动发现"按钮，自动扫描局域网可用服务器
4. 配置保存后，所有页面立即生效

### 方式3：直接修改代码

直接修改 `common/api.ts` 内的 `DEFAULT_BASE_URL_*` 常量。

说明：`common/api.ts` 会按以下优先级选择服务器地址：
1. 环境变量（构建时固定）
2. 用户自定义地址（Settings页面配置，本地存储）
3. 平台默认地址（H5/Android/iOS各不同）

## 三、运行前端

- 使用 HBuilderX 运行到 H5 或小程序
- 或使用 CLI（以 H5 为例）：
  ```bash
  npm install
  npm run dev:h5
  ```

## 四、主要页面

- **Generate页面**：`pages/Generate/Generate.vue`
  - 启动时自动调用 `ensureServerUrl()` 检查服务器连通性
  - 请求后端 `/options` 拉取风格、性别、年龄、API 供应商
  - 请求后端 `/generate` 获取姓名结果并展示
  - 实时显示后端连接状态和版本号

- **Settings页面**：`pages/Settings/Settings.vue`
  - 智能体连接配置（手动配置/自动发现/恢复默认）
  - 偏好设置（默认生成数量、API提供商、风格）
  - 显示设置（主题模式、字体大小、动画效果）

- **History页面**：`pages/History/History.vue`
  - 生成历史记录查看

- **Favorites页面**：`pages/Favorites/Favorites.vue`
  - 收藏的姓名管理

## 五、常见问题

- **CORS 报错**：确认后端已安装 `Flask-Cors` 且 `.env` 中设置了正确的 `ALLOWED_ORIGINS`；或先用默认放行（仅本地开发）。

- **无法连接后端**：
  1. 确认后端 `http://127.0.0.1:5000/health` 可访问
  2. 检查防火墙是否阻止5000端口
  3. Android模拟器：确认后端在主机运行，前端使用 `http://10.0.2.2:5000`
  4. Android真机：确认手机和电脑在同一局域网，使用电脑的局域网IP（如 `http://192.168.1.100:5000`）
  5. 使用Settings页面的"自动发现"功能，自动扫描可用服务器

- **IP地址变化导致连接失败**：
  - 智能服务器发现机制会自动检测并重新连接
  - 或在Settings页面手动配置新的服务器地址
  - 或点击"自动发现"按钮重新扫描

- **H5开发时跨域问题**：
  - 确保后端 `.env` 配置了 `ALLOWED_ORIGINS=http://localhost:5173,http://127.0.0.1:5173`
  - 如使用Vite dev server的proxy功能，修改 `vite.config.js`

---

