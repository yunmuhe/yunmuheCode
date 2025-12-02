，# 智能姓名生成系统（前端 · uni-app）

本前端通过 HTTP API 调用本地部署的智能体（Flask 服务）完成姓名生成。已适配 `H5/小程序` 端的请求封装。

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

前端默认请求 `http://127.0.0.1:5000`。如需修改：
- 使用环境变量（推荐其一）：
  - `VITE_API_BASE_URL=http://127.0.0.1:5000`
  - 或 `UNI_APP_API_BASE_URL=http://127.0.0.1:5000`
- 或直接修改 `common/api.ts` 内的 `DEFAULT_BASE_URL`。

说明：`common/api.ts` 会优先读取上述环境变量，其次回退到默认地址。

## 三、运行前端

- 使用 HBuilderX 运行到 H5 或小程序
- 或使用 CLI（以 H5 为例）：
  ```bash
  npm install
  npm run dev:h5
  ```

## 四、主要页面

- 生成页：`pages/Generate/Generate.vue`
  - 请求后端 `/options` 拉取风格、性别、年龄、API 供应商
  - 请求后端 `/generate` 获取姓名结果并展示

## 五、常见问题

- CORS 报错：确认后端已安装 `Flask-Cors` 且 `.env` 中设置了正确的 `ALLOWED_ORIGINS`；或先用默认放行（仅本地开发）。
- 无法连接：确认后端 `http://127.0.0.1:5000/health` 可访问；确认前端 `VITE_API_BASE_URL` 设置一致。

---

