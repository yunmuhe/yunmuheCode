#!/bin/bash

# 姓名生成API服务 - 云服务器部署脚本
# 使用方法：
# 1. 将此脚本上传到服务器
# 2. 赋予执行权限: chmod +x deploy_to_server.sh
# 3. 以root身份执行: sudo ./deploy_to_server.sh

set -e  # 遇到错误立即退出

echo "============================================"
echo "姓名生成API服务 - 自动部署脚本"
echo "============================================"
echo ""

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 检测系统类型
if [ -f /etc/os-release ]; then
    . /etc/os-release
    OS=$NAME
    VER=$VERSION_ID
else
    OS=$(uname -s)
    VER=$(uname -r)
fi

echo -e "${GREEN}检测到系统: $OS $VER${NC}"
echo ""

# 配置变量（请根据实际情况修改）
APP_NAME="nameagent"
APP_DIR="/home/NameGenerationAgent"
DOMAIN_NAME="api.yourdomain.com"  # 修改为你的域名
REPO_URL="https://github.com/yourusername/nameagent.git"  # 修改为你的Git仓库

# 检查是否为root用户
if [ "$EUID" -ne 0 ]; then
    echo -e "${RED}错误: 请使用root权限运行此脚本${NC}"
    echo "使用: sudo ./deploy_to_server.sh"
    exit 1
fi

# 步骤1：安装系统依赖
echo -e "${YELLOW}[1/8] 安装系统依赖...${NC}"
if [[ "$OS" == *"Ubuntu"* ]] || [[ "$OS" == *"Debian"* ]]; then
    apt update
    apt install -y python3 python3-pip python3-venv nginx git curl certbot python3-certbot-nginx
elif [[ "$OS" == *"CentOS"* ]] || [[ "$OS" == *"Red Hat"* ]]; then
    yum update -y
    yum install -y python3 python3-pip nginx git curl certbot python3-certbot-nginx
else
    echo -e "${RED}不支持的系统: $OS${NC}"
    exit 1
fi
echo -e "${GREEN}✓ 系统依赖安装完成${NC}"
echo ""

# 步骤2：创建应用目录并克隆代码
echo -e "${YELLOW}[2/8] 部署应用代码...${NC}"
if [ -d "$APP_DIR" ]; then
    echo "目录已存在，拉取最新代码..."
    cd $APP_DIR
    git pull
else
    echo "克隆代码仓库..."
    git clone $REPO_URL $APP_DIR
    cd $APP_DIR
fi
echo -e "${GREEN}✓ 代码部署完成${NC}"
echo ""

# 步骤3：配置Python虚拟环境
echo -e "${YELLOW}[3/8] 配置Python环境...${NC}"
if [ ! -d "$APP_DIR/venv" ]; then
    python3 -m venv venv
fi
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
echo -e "${GREEN}✓ Python环境配置完成${NC}"
echo ""

# 步骤4：配置环境变量
echo -e "${YELLOW}[4/8] 配置环境变量...${NC}"
if [ ! -f "$APP_DIR/.env" ]; then
    if [ -f "$APP_DIR/.env.example" ]; then
        cp $APP_DIR/.env.example $APP_DIR/.env
    else
        cat > $APP_DIR/.env << EOF
# API配置（请修改为实际的API密钥）
PAIOU_API_KEY=sk_your_key_here
AISTUDIO_API_KEY=your_key_here
AISTUDIO_API_URL=https://api-xxx.aistudio-app.com/v1

# CORS配置
ALLOWED_ORIGINS=https://$DOMAIN_NAME

# 生产环境配置
DEBUG=False
LOG_LEVEL=INFO
EOF
    fi
    echo -e "${YELLOW}警告: 请编辑 $APP_DIR/.env 文件配置API密钥${NC}"
    echo "使用命令: nano $APP_DIR/.env"
    read -p "按Enter继续..."
fi
echo -e "${GREEN}✓ 环境变量配置完成${NC}"
echo ""

# 步骤5：配置systemd服务
echo -e "${YELLOW}[5/8] 配置systemd服务...${NC}"
if [ -f "$APP_DIR/deploy/nameagent.service" ]; then
    cp $APP_DIR/deploy/nameagent.service /etc/systemd/system/
else
    cat > /etc/systemd/system/nameagent.service << 'EOF'
[Unit]
Description=Name Generation Agent API Service
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/home/NameGenerationAgent
Environment="PATH=/home/NameGenerationAgent/venv/bin"
ExecStart=/home/NameGenerationAgent/venv/bin/python main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF
fi

systemctl daemon-reload
systemctl enable $APP_NAME
systemctl start $APP_NAME

# 检查服务状态
sleep 2
if systemctl is-active --quiet $APP_NAME; then
    echo -e "${GREEN}✓ 服务启动成功${NC}"
else
    echo -e "${RED}✗ 服务启动失败，查看日志: journalctl -u $APP_NAME -n 50${NC}"
    exit 1
fi
echo ""

# 步骤6：配置Nginx
echo -e "${YELLOW}[6/8] 配置Nginx反向代理...${NC}"
if [ -f "$APP_DIR/deploy/nginx_config_template.conf" ]; then
    sed "s/api.yourdomain.com/$DOMAIN_NAME/g" $APP_DIR/deploy/nginx_config_template.conf > /etc/nginx/sites-available/$APP_NAME
else
    cat > /etc/nginx/sites-available/$APP_NAME << EOF
server {
    listen 80;
    server_name $DOMAIN_NAME;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
}
EOF
fi

# 启用站点
if [ ! -L /etc/nginx/sites-enabled/$APP_NAME ]; then
    ln -s /etc/nginx/sites-available/$APP_NAME /etc/nginx/sites-enabled/
fi

# 测试Nginx配置
if nginx -t; then
    systemctl restart nginx
    systemctl enable nginx
    echo -e "${GREEN}✓ Nginx配置完成${NC}"
else
    echo -e "${RED}✗ Nginx配置错误${NC}"
    exit 1
fi
echo ""

# 步骤7：配置防火墙
echo -e "${YELLOW}[7/8] 配置防火墙...${NC}"
if command -v ufw &> /dev/null; then
    ufw allow 80/tcp
    ufw allow 443/tcp
    ufw allow 22/tcp  # SSH
    echo "y" | ufw enable
    echo -e "${GREEN}✓ UFW防火墙配置完成${NC}"
elif command -v firewall-cmd &> /dev/null; then
    firewall-cmd --permanent --add-service=http
    firewall-cmd --permanent --add-service=https
    firewall-cmd --permanent --add-service=ssh
    firewall-cmd --reload
    echo -e "${GREEN}✓ firewalld防火墙配置完成${NC}"
else
    echo -e "${YELLOW}未检测到防火墙，请手动配置${NC}"
fi
echo ""

# 步骤8：配置SSL证书
echo -e "${YELLOW}[8/8] 配置SSL证书...${NC}"
echo -e "${YELLOW}提示: 确保域名 $DOMAIN_NAME 已解析到本服务器IP${NC}"
read -p "是否立即配置Let's Encrypt SSL证书？(y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    certbot --nginx -d $DOMAIN_NAME --non-interactive --agree-tos --register-unsafely-without-email
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ SSL证书配置完成${NC}"

        # 设置自动续期
        systemctl enable certbot.timer
        systemctl start certbot.timer
    else
        echo -e "${YELLOW}SSL证书配置失败，可能原因：${NC}"
        echo "  1. 域名未解析到本服务器"
        echo "  2. 80端口未开放"
        echo "  3. 请稍后手动运行: certbot --nginx -d $DOMAIN_NAME"
    fi
else
    echo -e "${YELLOW}跳过SSL配置，后续可手动执行: certbot --nginx -d $DOMAIN_NAME${NC}"
fi
echo ""

# 完成
echo "============================================"
echo -e "${GREEN}部署完成！${NC}"
echo "============================================"
echo ""
echo "服务信息："
echo "  - 应用目录: $APP_DIR"
echo "  - 域名: $DOMAIN_NAME"
echo "  - HTTP访问: http://$DOMAIN_NAME"
echo "  - HTTPS访问: https://$DOMAIN_NAME"
echo ""
echo "常用命令："
echo "  - 查看服务状态: systemctl status $APP_NAME"
echo "  - 查看实时日志: journalctl -u $APP_NAME -f"
echo "  - 重启服务: systemctl restart $APP_NAME"
echo "  - 重启Nginx: systemctl restart nginx"
echo "  - 查看应用日志: tail -f $APP_DIR/logs/app.log"
echo ""
echo "下一步："
echo "  1. 编辑 $APP_DIR/.env 配置API密钥"
echo "  2. 重启服务: systemctl restart $APP_NAME"
echo "  3. 测试访问: curl http://$DOMAIN_NAME/health"
echo "  4. 在APP中配置域名: https://$DOMAIN_NAME"
echo ""
echo -e "${GREEN}祝使用愉快！${NC}"
