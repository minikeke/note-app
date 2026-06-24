@echo off
cd /d "%~dp0"

echo ==========================================
echo  Git Push 错误修复脚本
echo ==========================================
echo.

echo  检查当前分支...
git branch
echo.

echo  检查提交历史...
git log --oneline -5 2>nul || echo  无提交记录
echo.

echo  检查远程仓库...
git remote -v
echo.

:: 检查是否有 master 分支但没有 main
git show-ref --verify --quiet refs/heads/master
if %errorlevel% equ 0 (
    echo  发现 master 分支，重命名为 main...
    git branch -m master main
    git push -u origin main
    goto :done
)

:: 检查是否有提交
git log --oneline -1 >nul 2>nul
if %errorlevel% neq 0 (
    echo  错误：本地没有任何提交！
    echo  请先添加文件并提交：
    echo    git add .
    echo    git commit -m "first commit"
    goto :done
)

:: 检查 main 分支是否存在
git show-ref --verify --quiet refs/heads/main
if %errorlevel% neq 0 (
    echo  创建 main 分支...
    git checkout -b main
)

:: 推送到远程
echo  推送到 GitHub...
git push -u origin main

:done
echo.
pause
