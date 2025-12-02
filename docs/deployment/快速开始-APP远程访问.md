# 🚀 快速开始 - APP远程访问配置

本文档帮助您快速配置后端域名，让移动APP能够远程访问服务。

## 📋 配置方案选择

### 方案对比

| 方案 | 适用场景 | 时间 | 成本 | 稳定性 |
|------|---------|------|------|--------|
| **内网穿透（推荐新手）** | 开发测试、快速演示 | 5分钟 | 免费 | ⭐⭐⭐ |
| **云服务器 + 域名** | 生产环境、正式上线 | 1-2小时 | ¥100+/月 | ⭐⭐⭐⭐⭐ |

---

## ⚡ 方案1：内网穿透（5分钟上手）

### 适用场景
- 个人开发测试
- 临时演示
- 团队协作开发

### 步骤1：注册natapp账号

访问 https://natapp.cn/ 注册账号（微信扫码即可）

### 步骤2：获取免费隧道

1. 登录后进入"我的隧道"
2. 点击"免费隧道"（或购买VIP隧道获得固定域名）
3. 记下你的 `authtoken`

### 步骤3：启动内网穿透

```bash
# Windows 用户
cd NameGenerationAgent
start_natapp.bat

# 按提示输入authtoken
```

等待启动完成，会显示类似：

```
Tunnel Status: online
Forwarding: https://abc123.natappfree.cc -> 127.0.0.1:5000
```

**记下这个地址**：`https://abc123.natappfree.cc`

### 步骤4：配置后端CORS

```bash
# 在 NameGenerationAgent 目录下执行
setup_domain.bat

# 选择 "2. 配置natapp内网穿透地址"
# 输入：https://abc123.natappfree.cc
```

### 步骤5：重启后端服务

```bash
# 停止当前运行的后端（Ctrl+C）
# 重新启动
quick_start.bat
```

### 步骤6：在APP中配置

1. 打开APP
2. 点击底部"设置"
3. 找到"智能体连接" → "自定义服务器地址"
4. 点击"配置"按钮
5. 输入：`https://abc123.natappfree.cc`
6. 点击"测试连接"
7. 点击"保存并使用"

✅ **完成！** 现在APP可以通过内网穿透访问后端了。

### 注意事项

- 免费版natapp每次重启域名会变化
- 建议购买VIP隧道（¥9/月）获得固定域名
- 保持natapp窗口打开，关闭后隧道断开

---

## 🌐 方案2：云服务器 + 域名（生产环境）

### 适用场景
- 正式上线
- 长期稳定运行
- 支持大量用户

### 准备工作

需要准备：
1. ✅ 云服务器（阿里云、腾讯云等）
   - 最低配置：1核2G，1M带宽
   - 系统：Ubuntu 20.04 或 CentOS 7+
   - 预算：¥100-300/月
2. ✅ 域名（.com 约¥55/年）
3. ✅ 域名备案（如服务器在中国大陆，需15-30天）

### 快速部署

#### 方式A：自动化脚本（推荐）

```bash
# 1. 上传代码到服务器
scp -r NameGenerationAgent root@你的服务器IP:/home/

# 2. 连接到服务器
ssh root@你的服务器IP

# 3. 执行自动部署脚本
cd /home/NameGenerationAgent
chmod +x deploy/deploy_to_server.sh

# 修改脚本中的域名配置
nano deploy/deploy_to_server.sh
# 找到 DOMAIN_NAME="api.yourdomain.com"
# 改为你的域名

# 运行部署脚本
sudo ./deploy/deploy_to_server.sh
```

脚本会自动完成：
- ✅ 安装Python、Nginx等依赖
- ✅ 配置虚拟环境和安装Python包
- ✅ 配置systemd服务（开机自启）
- ✅ 配置Nginx反向代理
- ✅ 申请Let's Encrypt SSL证书
- ✅ 配置防火墙

#### 方式B：手动配置

详细步骤参见：`后端域名配置指南.md`

### 配置域名解析

登录域名服务商（阿里云、腾讯云等）：

```
记录类型：A
主机记录：api
记录值：你的服务器IP
TTL：600
```

等待5-10分钟后测试：

```bash
ping api.你的域名.com
```

### 配置SSL证书

```bash
# 在服务器上执行
sudo certbot --nginx -d api.你的域名.com

# 自动续期已配置，无需手动操作
```

### 在APP中配置

1. 打开APP → 设置 → 智能体连接
2. 输入：`https://api.你的域名.com`
3. 测试连接 → 保存

✅ **完成！** 现在APP可以通过自有域名访问了。

### 服务管理命令

```bash
# 查看服务状态
sudo systemctl status nameagent

# 启动/停止/重启
sudo systemctl start nameagent
sudo systemctl stop nameagent
sudo systemctl restart nameagent

# 查看实时日志
sudo journalctl -u nameagent -f

# 查看Nginx状态
sudo systemctl status nginx

# 重启Nginx
sudo systemctl restart nginx
```

---

## 🔍 测试验证

### 测试后端健康

```bash
# 浏览器访问
https://你的域名/health

# 或使用curl
curl https://你的域名/health

# 预期输出
{"status":"healthy","timestamp":"2025-01-27..."}
```

### 测试生成接口

```bash
curl -X POST https://你的域名/generate \
  -H "Content-Type: application/json" \
  -d '{
    "description": "温柔善良的女孩",
    "count": 3,
    "cultural_style": "modern",
    "gender": "female",
    "age": "youth"
  }'
```

### APP端测试

1. 打开APP
2. 进入"生成"页面
3. 输入描述："聪明活泼的男孩"
4. 点击"生成姓名"
5. 查看是否正常返回结果

---

## 🛠️ 常见问题

### Q1: natapp启动后立即断开

**原因**：后端服务未运行

**解决**：
```bash
cd NameGenerationAgent
quick_start.bat  # 确保后端在5000端口运行
```

### Q2: APP提示"连接失败"

**检查清单**：
1. ✅ 后端是否运行：访问 `http://127.0.0.1:5000/health`
2. ✅ CORS是否配置：检查 `.env` 中 `ALLOWED_ORIGINS`
3. ✅ 域名是否正确：确认输入的地址可以访问
4. ✅ 防火墙：云服务器需要开放80和443端口

### Q3: 云服务器部署后502错误

**原因**：Nginx无法连接到后端Flask应用

**解决**：
```bash
# 检查后端服务
sudo systemctl status nameagent

# 如果未运行，启动服务
sudo systemctl start nameagent

# 查看详细日志
sudo journalctl -u nameagent -n 50
```

### Q4: SSL证书申请失败

**可能原因**：
- 域名未正确解析到服务器IP
- 80端口未开放
- 防火墙阻止

**解决**：
```bash
# 测试域名解析
nslookup api.你的域名.com

# 测试80端口
curl http://api.你的域名.com

# 开放防火墙
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
```

### Q5: 免费natapp域名每次变化怎么办？

**方案A**：购买VIP隧道（¥9/月）获得固定域名

**方案B**：使用动态更新
```bash
# 每次natapp重启后
1. 记下新域名
2. 运行 setup_domain.bat 更新CORS
3. 重启后端服务
4. 在APP中更新域名
```

**方案C**：考虑使用云服务器（长期使用更划算）

---

## 📚 进一步阅读

- 📖 **完整配置指南**：`后端域名配置指南.md`
  - 详细的云服务器配置步骤
  - Nginx、SSL证书详细配置
  - 安全加固和监控

- 🐛 **问题诊断**：`问题诊断和解决.md`
  - 常见错误和解决方案
  - 日志分析方法

- 📱 **Android配置**：`Android模拟器配置指南.md`
  - Android模拟器网络配置
  - 不同模拟器的IP设置

- 🔧 **项目文档**：`CLAUDE.md`
  - 完整的项目架构说明
  - 开发和部署指南

---

## 💡 推荐方案

### 个人开发学习
→ 使用 **natapp免费版**，成本：免费

### 团队协作开发
→ 使用 **natapp VIP版**，成本：¥9/月

### 正式产品上线
→ 使用 **云服务器 + 域名**，成本：¥120/月起

---

## 🆘 需要帮助？

如果遇到问题：
1. 查看 `logs/app.log` 日志
2. 运行 `test_server_discovery.bat` 诊断
3. 参考 `后端域名配置指南.md`
4. 检查 `问题诊断和解决.md`

**祝配置顺利！🎉**
