@echo off
chcp 65001
cls
echo ==========================================
echo  正在启动个人笔记系统...
echo ==========================================
echo.
echo  电脑端访问: http://localhost:8502
echo.
echo  手机请访问: http://192.168.2.103:8502
echo  (如果手机打不开，请运行"防火墙放行.bat")
echo.
cd /d "%~dp0"
C:\Users\lin\.workbuddy\binaries\python\envs\noteapp\Scripts\streamlit.exe run app.py --server.port 8502 --server.headless false --server.address 0.0.0.0
pause
