@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

:: 姓名生成API - natapp内网穿透快速启动脚本
:: 使用方法：
:: 1. 在 https://natapp.cn 注册账号
:: 2. 获取免费或付费隧道的authtoken
:: 3. 双击运行此脚本
:: 4. 按提示输入authtoken

echo ============================================
echo    姓名生成API - natapp内网穿透配置工具
echo ============================================
echo.

:: 检查natapp是否存在
if not exist "natapp\natapp.exe" (
    echo [错误] 未找到 natapp.exe
    echo.
    echo 请按以下步骤操作：
    echo 1. 访问 https://natapp.cn/download
    echo 2. 下载 Windows 版本
    echo 3. 解压到当前目录的 natapp 文件夹
    echo 4. 确保路径为: natapp\natapp.exe
    echo.
    pause
    exit /b 1
)

:: 检查配置文件
if exist "natapp\config.ini" (
    echo [信息] 检测到已有配置文件
    choice /C YN /M "是否重新配置"
    if errorlevel 2 goto :start_natapp
)

:: 配置authtoken
:config
echo.
echo ============================================
echo    配置natapp authtoken
echo ============================================
echo.
echo 请访问 https://natapp.cn/ 获取authtoken
echo 免费隧道：注册后在"我的隧道"页面查看
echo 付费隧道：购买后在详情页面查看authtoken
echo.
set /p authtoken="请输入你的authtoken: "

if "%authtoken%"=="" (
    echo [错误] authtoken不能为空
    goto :config
)

:: 创建配置文件
echo [default] > natapp\config.ini
echo authtoken=%authtoken% >> natapp\config.ini
echo log=stdout >> natapp\config.ini
echo loglevel=INFO >> natapp\config.ini

echo.
echo [成功] 配置文件已创建: natapp\config.ini
echo.

:: 启动natapp
:start_natapp
echo ============================================
echo    启动natapp隧道
echo ============================================
echo.
echo [提示] 保持此窗口打开，natapp将持续运行
echo [提示] 按 Ctrl+C 可停止服务
echo.
echo 启动中...
echo.

cd natapp
natapp.exe -config=config.ini

:: 如果natapp异常退出
echo.
echo ============================================
echo    natapp已停止
echo ============================================
echo.
echo 可能的原因：
echo 1. authtoken无效或过期
echo 2. 网络连接问题
echo 3. 后端服务未启动（需要在5000端口）
echo.
echo 解决方案：
echo 1. 检查 natapp\config.ini 中的authtoken是否正确
echo 2. 确保后端服务正在运行（另一个窗口执行 quick_start.bat）
echo 3. 访问 https://natapp.cn/login 检查隧道状态
echo.
pause
exit /b 0
