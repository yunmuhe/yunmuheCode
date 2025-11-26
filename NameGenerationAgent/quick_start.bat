@echo off
chcp 65001 >nul
echo ========================================
echo 智能姓名生成系统 - 快速启动
echo ========================================
echo.

echo [1/2] 检查 .env 文件...
if not exist .env (
    echo ⚠ .env 文件不存在，正在创建...
    copy env.example .env >nul
    echo ✅ .env 文件创建成功
    echo 📝 请编辑 .env 文件配置你的 API 密钥
    echo.
    pause
) else (
    echo ✅ .env 文件已存在
)

echo.
echo [2/2] 启动 Web 服务...
echo.
python main.py

pause

