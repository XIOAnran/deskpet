# 小海桌宠 - PowerShell 构建脚本
Write-Host @"
============================================
      小海桌宠构建工具 v2.0 (PowerShell)
============================================
"@ -ForegroundColor Cyan

# 检查 Python
$python = Get-Command python -ErrorAction SilentlyContinue
if (-not $python) {
    Write-Host "[错误] 未找到 Python！请先安装 Python 3.8+" -ForegroundColor Red
    Write-Host "下载地址: https://www.python.org/downloads/"
    pause
    exit 1
}

Write-Host "[OK] Python 已检测" -ForegroundColor Green
python --version

# 安装依赖
Write-Host "`n[1/5] 安装依赖..." -ForegroundColor Yellow
pip install --quiet --upgrade pip
pip install --quiet pillow pyinstaller PyQt5
Write-Host "[OK] 依赖安装完成" -ForegroundColor Green

# 去除背景
Write-Host "`n[2/5] 去除图片背景..." -ForegroundColor Yellow
if (Test-Path "character_nobg.png") {
    Write-Host "已存在去背景后的图片，跳过"
} else {
    python remove_bg.py
}
Write-Host "[OK] 背景处理完成" -ForegroundColor Green

# 生成图标
Write-Host "`n[3/5] 生成图标..." -ForegroundColor Yellow
python make_icon.py
Write-Host "[OK] 图标生成完成" -ForegroundColor Green

# 构建 EXE
Write-Host "`n[4/5] 构建 EXE..." -ForegroundColor Yellow
pyinstaller --onefile --windowed --name "小海桌宠" `
    --add-data "character_nobg.png;." `
    --icon icon.ico `
    --hidden-import PyQt5.sip `
    --clean `
    --noconfirm `
    deskpet.py

if ($LASTEXITCODE -ne 0) {
    Write-Host "[错误] 构建失败！" -ForegroundColor Red
    pause
    exit 1
}
Write-Host "[OK] EXE 构建完成" -ForegroundColor Green

# 清理
Write-Host "`n[5/5] 清理临时文件..." -ForegroundColor Yellow
Remove-Item -Recurse -Force build -ErrorAction SilentlyContinue
Remove-Item *.spec -ErrorAction SilentlyContinue
Write-Host "[OK] 清理完成" -ForegroundColor Green

Write-Host @"
`n
============================================
      构建成功！
      程序位置: dist\小海桌宠.exe
============================================
"@ -ForegroundColor Cyan
Write-Host "提示: 如需更换角色图片，替换 character.jpg 后重新构建" -ForegroundColor Yellow
pause