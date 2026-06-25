#!/bin/bash
# GitHub 镜像加速脚本
# 用法: ./github_mirror.sh

echo "正在配置 GitHub 镜像代理..."

# 方案1: 使用 ghproxy 镜像代理
echo ""
echo "方案1: 设置 ghproxy 代理 (推荐，最简单)"
echo "执行命令:"
echo ""
echo "  git remote set-url origin https://ghproxy.com/https://github.com/miracleaty/note-app.git"
echo ""
echo "  git push -u origin main"
echo ""

# 方案2: 使用 SSH 方式
echo "方案2: 改用 SSH 方式 (如果已有 SSH 密钥)"
echo "执行命令:"
echo ""
echo "  git remote set-url origin git@github.com:miracleaty/note-app.git"
echo ""
echo "  git push -u origin main"
echo ""

# 方案3: 设置全局代理
echo "方案3: 设置 Git 全局代理 (如果你有 VPN 在运行)"
echo "执行命令:"
echo ""
echo "  git config --global http.proxy http://127.0.0.1:7890"
echo "  git config --global https.proxy http://127.0.0.1:7890"
echo "  git push -u origin main"
echo ""
echo "  (7890 是常见 VPN 端口，请根据你的 VPN 实际端口修改)"
echo ""

# 方案4: 使用 Gitee 中转
echo "方案4: 使用 Gitee 作为中转 (最可靠，但多一步)"
echo "1. 访问 https://gitee.com 导入 GitHub 仓库"
echo "2. 或者用 git 直接推送:"
echo ""
echo "  git remote add gitee https://gitee.com/你的用户名/note-app.git"
echo "  git push -u gitee main"
echo ""
echo "  (Streamlit Cloud 需要从 GitHub 部署，但 Gitee 可以用来存储代码)"
echo ""
