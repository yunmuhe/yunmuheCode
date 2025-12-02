# Android模拟器调试步骤

## 问题现象
前端在Android模拟器（MuMu 5.0）上显示空白页面

## 已完成的修复

### 1. ✅ 修复路径大小写问题
- 统一使用大写路径（Index、Generate等）
- 修改跳转方式为 `uni.switchTab`

### 2. ✅ 修复网络配置
- 后端CORS配置：`ALLOWED_ORIGINS=http://192.168.10.15:5000,...`
- 前端API地址：Android自动使用 `http://192.168.10.15:5000`

### 3. ✅ 修复条件编译语法错误
- 移除了TypeScript文件中不支持的注释形式条件编译
- 改用运行时平台检测

### 4. ✅ 创建测试页面
- 新增 `pages/Test/Test.vue` 用于快速诊断连接问题

---

## 🚀 立即执行步骤

### 第1步：重启后端服务

```bash
# 停止当前运行的Python进程（Ctrl+C）
# 然后重新启动
cd NameGenerationAgent
python main.py
```

**验证输出包含**：
```
✓ CORS已配置: ['http://localhost:5173', ..., 'http://192.168.10.15:5000']
* Running on http://0.0.0.0:5000
```

### 第2步：在HBuilderX中完全重新编译

**重要**：简单的"刷新"可能不够，需要完全重新编译

1. 停止当前运行：点击 **运行 → 停止运行**
2. 清理缓存：关闭HBuilderX，删除项目目录下的 `unpackage` 文件夹
3. 重新打开HBuilderX
4. 运行：**运行 → 运行到手机或模拟器 → Android自定义基座**

### 第3步：查看测试页面

应用启动后，会直接进入 **连接测试** 页面（我已将它设为首页）。

**测试页面会显示**：
- ✅ 平台信息（android / Android 5.0）
- ✅ API地址（http://192.168.10.15:5000）
- ✅ 连接状态（已连接/未连接）
- ✅ 详细日志输出

### 第4步：分析结果

#### 场景A：测试页面正常显示，但连接失败

**可能原因**：防火墙阻止或网络配置问题

**解决方案**：

1. **测试后端可达性** - 在模拟器浏览器中访问：
   ```
   http://192.168.10.15:5000/health
   ```
   应该看到JSON响应：`{"status": "healthy", ...}`

2. **配置Windows防火墙**：
   ```
   控制面板 → Windows Defender 防火墙 → 高级设置 → 入站规则 → 新建规则
   - 类型：端口
   - 协议：TCP，端口：5000
   - 操作：允许连接
   - 配置文件：全选
   - 名称：Flask Backend
   ```

3. **检查IP地址是否正确**：
   ```bash
   ipconfig | findstr IPv4
   ```
   如果IP变了，需要更新 `common/api.ts` 中的 `DEFAULT_BASE_URL_ANDROID`

#### 场景B：测试页面本身也是空白

**可能原因**：应用编译或加载错误

**解决方案**：

1. **查看HBuilderX控制台**：
   - 点击底部 **控制台** 标签
   - 查找红色错误信息
   - 截图错误内容

2. **使用Chrome远程调试**：
   ```
   1. Chrome访问：chrome://inspect/#devices
   2. 找到你的MuMu模拟器设备
   3. 点击 inspect
   4. 查看Console标签中的错误
   ```

3. **检查MuMu模拟器设置**：
   - 打开MuMu多开器
   - 检查模拟器版本（建议Android 7.1+）
   - 检查网络模式（NAT或桥接）

#### 场景C：测试页面显示且连接成功

**太好了！**现在可以恢复正常首页：

编辑 `pages.json`，将 `pages/Index/Index` 移到第一位：

```json
{
  "pages": [
    {
      "path": "pages/Index/Index",
      "style": { "navigationBarTitleText": "首页" }
    },
    {
      "path": "pages/Test/Test",
      "style": { "navigationBarTitleText": "连接测试" }
    },
    // ... 其他页面
  ]
}
```

---

## 🔍 常见问题排查

### 1. 外部图片无法加载

`Index.vue` 使用了外部图片（mastergo.com），可能导致：
- 图片显示为空白
- 页面加载缓慢

**临时解决**：将图片下载到本地

```bash
# 在 static 目录下创建 images 文件夹
mkdir 智能姓名生成系统/static/images

# 将图片放入该文件夹，然后修改 Index.vue：
# src="https://..." 改为 src="/static/images/logo.png"
```

### 2. 样式不生效

某些CSS属性在老版本Android不支持，例如：
- `clamp()` - Android 7以下不支持
- `aspect-ratio` - Android 8以下不支持

**解决**：使用固定值或媒体查询替代

### 3. uni-icons组件未显示

需要安装uni-ui组件库：

```bash
npm install @dcloudio/uni-ui
```

或在HBuilderX中：
```
工具 → 插件市场 → 搜索 "uni-ui" → 导入
```

---

## 📝 调试日志示例

**正常日志（测试页面）**：
```
[Platform Detection] Platform: android
[Platform Detection] Using Android URL: http://192.168.10.15:5000
[API Base URL detected]: http://192.168.10.15:5000
[14:23:45] 页面加载成功
[14:23:45] 平台: android / Android 5.0
[14:23:45] API地址: http://192.168.10.15:5000
[14:23:45] 开始测试连接...
[14:23:46] 连接成功! 状态: healthy
```

**异常日志示例**：
```
[14:23:46] 连接失败: Network request failed
→ 检查防火墙设置

[14:23:46] 连接失败: timeout
→ 检查后端是否运行、IP是否正确

ReferenceError: uni is not defined
→ 编译问题，需要重新构建
```

---

## 📞 需要提供的信息

如果问题仍未解决，请提供：

1. **HBuilderX控制台截图**（红色错误部分）
2. **Chrome远程调试Console截图**
3. **测试页面截图**（如果能显示）
4. **后端启动日志**（main.py的输出）
5. **MuMu模拟器版本和Android版本**

---

## ✅ 检查清单

执行完上述步骤后，请确认：

- [ ] 后端服务正常运行（http://0.0.0.0:5000）
- [ ] CORS配置包含 `http://192.168.10.15:5000`
- [ ] 前端已完全重新编译（删除unpackage文件夹）
- [ ] 测试页面能够显示
- [ ] IP地址配置正确（192.168.10.15）
- [ ] 防火墙已允许5000端口
- [ ] MuMu模拟器网络正常（能上网）

完成所有检查后，应用应该能正常运行！
