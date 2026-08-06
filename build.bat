@echo off
chcp 65001 >nul
title 小海桌宠 - 构建工具

echo ============================================
echo       小海桌宠构建工具 v2.0
echo ============================================
echo.

:: 检查 Python
where python >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo [错误] 未找到 Python！请先安装 Python 3.8+
    echo 下载地址: https://www.python.org/downloads/
    echo 安装时请勾选 "Add Python to PATH"
    pause
    exit /b 1
)

echo [OK] Python 已检测
python --version

:: 检查 pip
where pip >nul 2>&1
if %ERRORLEVEL% neq 0 (
    python -m ensurepip
)

echo.
echo [1/5] 安装依赖...
pip install --quiet --upgrade pip
pip install --quiet pillow pyinstaller PyQt5
echo [OK] 依赖安装完成

echo.
echo [2/5] 去除图片背景...
if exist character_nobg.png (
    echo 已存在去背景后的图片，跳过
) else (
    python remove_bg.py
)
echo [OK] 背景处理完成

echo.
echo [3/5] 生成图标...
python make_icon.py
echo [OK] 图标生成完成

echo.
echo [4/5] 构建 EXE...
pyinstaller --onefile --windowed --name "小海桌宠" ^
    --add-data "character_nobg.png;." ^
    --icon icon.ico ^
    --hidden-import PyQt5.sip ^
    --clean ^
    --noconfirm ^
    deskpet.py

if %ERRORLEVEL% neq 0 (
    echo [错误] 构建失败！
    pause
    exit /b 1
)
echo [OK] EXE 构建完成

echo.
echo [5/5] 清理临时文件...
rmdir /s /q build >nul 2>&1
del /q *.spec >nul 2>&1
echo [OK] 清理完成

echo.
echo ============================================
echo       构建成功！
echo       程序位置: dist\小海桌宠.exe
echo ============================================
echo.
echo 提示: 如需更换角色图片，替换 character.jpg 后重新构建
echo.
pause