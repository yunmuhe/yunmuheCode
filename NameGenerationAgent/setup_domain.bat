@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

:: 姓名生成API - 域名配置辅助工具
:: 自动更新后端CORS配置

echo ============================================
echo    域名/内网穿透地址配置工具
echo ============================================
echo.

:: 检查.env文件是否存在
if not exist ".env" (
    if exist ".env.example" (
        echo [信息] 从 .env.example 创建 .env 文件...
        copy .env.example .env >nul
    ) else (
        echo [错误] 未找到 .env 或 .env.example 文件
        echo 请确保在 NameGenerationAgent 目录下运行此脚本
        pause
        exit /b 1
    )
)

:: 显示当前配置
echo 当前CORS配置：
findstr "ALLOWED_ORIGINS" .env
echo.

:: 选择配置方式
echo ============================================
echo    选择配置方式
echo ============================================
echo.
echo 1. 配置云服务器域名（生产环境）
echo 2. 配置natapp内网穿透地址
echo 3. 配置ngrok内网穿透地址
echo 4. 配置花生壳动态域名
echo 5. 手动输入自定义地址
echo 6. 查看当前配置
echo 0. 退出
echo.
set /p choice="请选择 (0-6): "

if "%choice%"=="1" goto :cloud_domain
if "%choice%"=="2" goto :natapp
if "%choice%"=="3" goto :ngrok
if "%choice%"=="4" goto :oray
if "%choice%"=="5" goto :custom
if "%choice%"=="6" goto :view_config
if "%choice%"=="0" exit /b 0

echo [错误] 无效的选择
pause
exit /b 1

:: 云服务器域名配置
:cloud_domain
echo.
echo ============================================
echo    配置云服务器域名
echo ============================================
echo.
echo 示例：https://api.yourdomain.com
echo 提示：使用HTTPS协议更安全
echo.
set /p domain="请输入你的域名: "
if "%domain%"=="" (
    echo [错误] 域名不能为空
    pause
    exit /b 1
)
set ALLOWED_ORIGINS=%domain%
goto :update_env

:: natapp配置
:natapp
echo.
echo ============================================
echo    配置natapp地址
echo ============================================
echo.
echo 步骤：
echo 1. 启动natapp: start_natapp.bat
echo 2. 查看natapp窗口显示的Forwarding地址
echo 3. 复制 https://xxx.natappfree.cc 格式的地址
echo.
set /p natapp_url="请输入natapp分配的地址: "
if "%natapp_url%"=="" (
    echo [错误] 地址不能为空
    pause
    exit /b 1
)
set ALLOWED_ORIGINS=%natapp_url%
goto :update_env

:: ngrok配置
:ngrok
echo.
echo ============================================
echo    配置ngrok地址
echo ============================================
echo.
echo 步骤：
echo 1. 启动ngrok: ngrok http 5000
echo 2. 查看ngrok窗口显示的Forwarding地址
echo 3. 复制 https://xxxx.ngrok-free.app 格式的地址
echo.
set /p ngrok_url="请输入ngrok分配的地址: "
if "%ngrok_url%"=="" (
    echo [错误] 地址不能为空
    pause
    exit /b 1
)
set ALLOWED_ORIGINS=%ngrok_url%
goto :update_env

:: 花生壳配置
:oray
echo.
echo ============================================
echo    配置花生壳动态域名
echo ============================================
echo.
echo 示例：http://yourname.xicp.net
echo.
set /p oray_url="请输入花生壳分配的域名: "
if "%oray_url%"=="" (
    echo [错误] 域名不能为空
    pause
    exit /b 1
)
set ALLOWED_ORIGINS=%oray_url%
goto :update_env

:: 自定义配置
:custom
echo.
echo ============================================
echo    自定义地址配置
echo ============================================
echo.
echo 可以输入多个地址，用英文逗号分隔
echo 示例：https://api.domain.com,https://xxx.natappfree.cc
echo.
set /p custom_origins="请输入地址: "
if "%custom_origins%"=="" (
    echo [错误] 地址不能为空
    pause
    exit /b 1
)
set ALLOWED_ORIGINS=%custom_origins%
goto :update_env

:: 查看当前配置
:view_config
echo.
echo ============================================
echo    当前完整配置
echo ============================================
echo.
type .env
echo.
pause
exit /b 0

:: 更新.env文件
:update_env
echo.
echo ============================================
echo    更新配置文件
echo ============================================
echo.
echo 新的ALLOWED_ORIGINS: %ALLOWED_ORIGINS%
echo.
choice /C YN /M "确认更新配置"
if errorlevel 2 (
    echo [取消] 未修改配置
    pause
    exit /b 0
)

:: 备份原文件
copy .env .env.backup >nul

:: 创建临时文件
set temp_file=.env.tmp
if exist %temp_file% del %temp_file%

:: 读取并更新配置
set found=0
for /f "usebackq delims=" %%i in (".env") do (
    set line=%%i
    echo !line! | findstr /C:"ALLOWED_ORIGINS=" >nul
    if errorlevel 1 (
        echo %%i>>%temp_file%
    ) else (
        echo ALLOWED_ORIGINS=%ALLOWED_ORIGINS%>>%temp_file%
        set found=1
    )
)

:: 如果没找到ALLOWED_ORIGINS，追加到文件末尾
if !found!==0 (
    echo.>>%temp_file%
    echo # CORS配置>>%temp_file%
    echo ALLOWED_ORIGINS=%ALLOWED_ORIGINS%>>%temp_file%
)

:: 替换原文件
move /y %temp_file% .env >nul

echo.
echo [成功] 配置已更新
echo [备份] 原配置已保存到 .env.backup
echo.

:: 测试配置
echo ============================================
echo    验证配置
echo ============================================
echo.
echo 更新后的配置：
findstr "ALLOWED_ORIGINS" .env
echo.

choice /C YN /M "是否立即重启后端服务以应用配置"
if errorlevel 2 (
    echo.
    echo [提示] 请手动重启后端服务：
    echo   1. 停止当前运行的后端（Ctrl+C）
    echo   2. 重新运行: quick_start.bat
    echo.
    pause
    exit /b 0
)

:: 重启服务
echo.
echo [信息] 正在重启后端服务...
echo.

:: 查找并终止现有的Python进程（运行main.py）
for /f "tokens=2" %%i in ('tasklist ^| findstr /i "python.exe"') do (
    taskkill /PID %%i /F >nul 2>&1
)

timeout /t 2 /nobreak >nul

:: 启动后端
echo [启动] 后端服务启动中...
start "姓名生成API后端" cmd /k "call venv\Scripts\activate && python main.py"

timeout /t 5 /nobreak >nul

:: 测试连接
echo.
echo [测试] 检查服务健康状态...
curl -s http://127.0.0.1:5000/health
echo.
echo.

echo ============================================
echo    配置完成
echo ============================================
echo.
echo 下一步：
echo 1. 确认后端服务正常运行
echo 2. 打开APP，进入"设置"页面
echo 3. 在"自定义服务器地址"中输入：
echo    %ALLOWED_ORIGINS%
echo 4. 点击"测试连接"，然后"保存并使用"
echo.
echo 如果连接失败，请检查：
echo ✓ 后端服务是否正常运行
echo ✓ 域名/内网穿透是否正确配置
echo ✓ 防火墙是否允许访问
echo.
pause
exit /b 0
