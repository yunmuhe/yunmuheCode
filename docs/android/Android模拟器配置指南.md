# Android模拟器配置快速指南

## 问题说明

Android模拟器中的 `127.0.0.1` 指向模拟器自己，而不是宿主机（你的电脑）。因此需要配置正确的服务器地址。

## 解决方案（3选1）

### 方案1：手动配置（最可靠）⭐ 推荐

**步骤1：获取电脑IP地址**

在电脑上运行：
```bash
# Windows
ipconfig

# 输出示例：
# IPv4 地址 . . . . . . . . . . . . : 192.168.10.12
```

记下类似 `192.168.10.12` 的地址

**步骤2：在Android应用中配置**

1. 打开应用 → 点击底部"设置"标签
2. 找到"智能体连接"部分
3. 点击"配置"按钮展开
4. 在输入框中输入：`http://192.168.10.12:5000`（替换为你的IP）
5. 点击"测试连接"验证
6. 点击"保存并使用"

**步骤3：验证连接**

- 连接状态应显示：绿点 + "已连接"
- 如果显示"未连接"，检查防火墙配置

---

### 方案2：自动发现（可能较慢）

**步骤1：触发自动发现**

1. 打开应用 → 点击"设置"
2. 找到"智能体连接" → "自定义服务器地址"
3. 点击"配置"展开
4. 点击"自动发现"按钮

**步骤2：等待搜索**

- 系统会测试约80个候选地址
- 等待2-5秒
- 自动选择最快响应的服务器

**步骤3：验证结果**

- 查看"当前服务器"是否显示正确的IP
- 检查"连接状态"是否为"已连接"

---

### 方案3：使用Android Studio模拟器特定地址

如果你使用的是Android Studio自带的模拟器：

1. 在应用设置中配置：`http://10.0.2.2:5000`
2. 这个地址在Android Studio模拟器中代表宿主机
3. 测试并保存

---

## 常见问题

### Q1: 自动发现找不到服务器

**原因**：
- 防火墙阻止了连接
- 电脑和模拟器不在同一网络

**解决**：
1. 配置防火墙（运行 `setup_firewall.bat`）
2. 或使用手动配置方式

### Q2: 手动配置后仍无法连接

**检查清单**：
1. ✅ 后端是否在运行？
   ```bash
   netstat -ano | findstr ":5000"
   ```

2. ✅ IP地址是否正确？
   - 再次运行 `ipconfig` 确认
   - 确保使用 `http://` 前缀
   - 确保端口是 `:5000`

3. ✅ 防火墙是否允许？
   - 以管理员身份运行 `setup_firewall.bat`
   - 或在电脑上测试：`curl http://你的IP:5000/health`

4. ✅ CORS是否配置？
   - 编辑 `NameGenerationAgent/.env`
   - 确保包含：`ALLOWED_ORIGINS=http://你的IP:5000`

### Q3: IP地址变化了怎么办？

**快速解决**：
1. 进入应用设置
2. 点击"配置"
3. 更新IP地址或点击"自动发现"

---

## 不同模拟器的配置

### MuMu模拟器
- 使用宿主机局域网IP：`http://192.168.x.x:5000`
- 需要配置防火墙

### 夜神模拟器
- 方式1：使用 `http://10.0.2.2:5000`
- 方式2：使用局域网IP `http://192.168.x.x:5000`

### 雷电模拟器
- 使用宿主机局域网IP：`http://192.168.x.x:5000`
- 需要配置防火墙

### Android Studio模拟器
- 优先使用：`http://10.0.2.2:5000`
- 这个地址代表宿主机，无需知道实际IP

### 真机（手机/平板）
- 必须使用局域网IP：`http://192.168.x.x:5000`
- 确保手机和电脑连接同一WiFi

---

## 测试验证

运行测试脚本：
```bash
cd NameGenerationAgent
test_server_discovery.bat
```

脚本会显示：
- ✅ 你的电脑IP
- ✅ 后端运行状态
- ✅ 连接测试结果
- 📋 推荐配置

---

## 快速诊断

**后端未连接时**：

1. 查看应用控制台日志（如果可以）：
   ```
   [Server Discovery] Platform: android
   [Server Discovery] Android: Generated XX candidates
   [Server Discovery] Testing XX candidate URLs...
   ```

2. 最快的日志应该显示成功：
   ```
   [Server Discovery] ✅ http://192.168.10.12:5000 - XXms
   [Server Discovery] Using fastest: ...
   ```

3. 如果全部失败：
   ```
   [Server Discovery] ❌ http://... - timeout
   [Server Discovery] No available servers found
   ```

   → 使用手动配置方式

---

## 完整配置示例

假设你的电脑IP是 `192.168.10.12`：

### 1. 后端配置（`.env`）
```env
# 允许Android访问
ALLOWED_ORIGINS=http://192.168.10.12:5000

# 其他API配置...
PAIOU_API_KEY=sk_xxx
```

### 2. 防火墙配置
```bash
# 以管理员身份运行
setup_firewall.bat
```

### 3. 启动后端
```bash
cd NameGenerationAgent
python main.py
```

### 4. Android应用配置
- 输入：`http://192.168.10.12:5000`
- 测试连接 → 保存

### 5. 验证
- 连接状态：✅ 已连接
- 尝试生成姓名测试功能

---

## 需要帮助？

如果仍然无法连接：

1. 运行完整诊断：`test_server_discovery.bat`
2. 检查日志：`NameGenerationAgent/logs/app.log`
3. 参考文档：`问题诊断和解决.md`
