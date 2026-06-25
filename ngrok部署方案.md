# ngrok 内网穿透部署方案（手机远程访问）

使用 ngrok 将本地 Streamlit 应用映射到公网地址，手机在任何网络下都能访问。

---

## 原理

```
手机 → 公网 URL（ngrok 提供） → ngrok 客户端 → 你的电脑（localhost:8502）
```

ngrok 是一个隧道工具，它会给你一个 `https://xxx.ngrok-free.app` 的公网地址。

---

## 第一步：下载 ngrok（1 分钟）

1. 访问 https://ngrok.com/download
2. 下载 Windows 版本（64-bit）
3. 解压到 `C:\ngrok` 文件夹

---

## 第二步：注册并获取 Authtoken（2 分钟）

1. 访问 https://ngrok.com/signup
2. 用邮箱注册
3. 登录后，在 Dashboard 页面找到 **Your Authtoken**
4. 点击复制，保存好这串字符

---

## 第三步：配置 ngrok（1 分钟）

打开 CMD，运行：

```cmd
cd C:\ngrok
ngrok.exe config add-authtoken 你的Authtoken
```

---

## 第四步：启动你的笔记应用（保持运行）

双击 `启动.bat`，保持控制台窗口运行。

确认控制台显示：
```
Local URL: http://localhost:8502
Network URL: http://192.168.x.x:8502
```

---

## 第五步：启动 ngrok 隧道（1 分钟）

在另一个 CMD 窗口中运行：

```cmd
cd C:\ngrok
ngrok.exe http 8502
```

你会看到类似输出：
```
Session Status                online
Account                       Your Name (Plan: Free)
Version                       3.x.x
Region                        United States (us)
Web Interface                 http://127.0.0.1:4040
Forwarding                    https://abc123def.ngrok-free.app -> http://localhost:8502
```

**复制 `Forwarding` 那一行的 https 地址**，比如：
```
https://abc123def.ngrok-free.app
```

---

## 第六步：手机访问

1. 在手机浏览器中输入 ngrok 提供的地址
2. 点击添加到桌面（iPhone：分享 → 添加到主屏幕；Android：菜单 → 添加到主屏幕）
3. 现在你可以在任何地方使用手机访问你的笔记应用！

---

## 关于数据同步

### 方案 A：单设备访问（最简）
- 电脑作为服务器，数据存储在本地 SQLite（`data/notes.db`）
- 手机通过 ngrok 访问电脑上的应用
- **缺点**：电脑关机后手机无法访问，且数据只存在电脑上

### 方案 B：使用 Supabase 数据库（推荐）
即使使用 ngrok，也可以连接 Supabase 云数据库，实现真正的数据同步：

1. 注册 Supabase：访问 https://supabase.com，用邮箱注册
2. 创建新项目，项目名填 `note-app`
3. 进入 **Project Settings** → **Database** → **Connection string** → 选择 **URI** 格式，复制连接字符串
4. 打开 `启动.bat`，找到 `set DATABASE_URL=` 这一行，把值替换成你的 Supabase URI：

   ```bat
   set DATABASE_URL=postgresql://postgres:你的密码@db.xxxxxxx.supabase.co:5432/postgres
   ```

   > **注意**：如果密码里包含 `@`、`:`、`?` 等特殊字符，需要改成 URL 编码形式。常见替换：
   > - `@` → `%40`
   > - `:` → `%3A`
   > - `?` → `%3F`
   > - `#` → `%23`

5. 保存 `启动.bat`，重新双击运行
6. 现在数据会写入 Supabase 云端数据库，电脑关机后数据依然在云端

**验证是否连接成功：**
启动后，控制台会显示 `Uvicorn server started`。打开浏览器访问 `http://localhost:8502`，新建一条笔记或日程，然后到 Supabase 的 Table Editor 里查看对应表是否有数据。

**自动切换机制：**
`database.py` 已改为双后端：
- 检测到 `DATABASE_URL` → 连接 PostgreSQL（Supabase）
- 没有 `DATABASE_URL` → 自动回退到本地 SQLite

所以即使暂时不配置 Supabase，应用也能正常使用。

---

## ngrok 免费版限制

| 限制 | 说明 |
|------|------|
| URL 变化 | 每次重启 ngrok，URL 会变 |
| 连接数 | 同时最多 40 个连接 |
| 带宽 | 1GB/月 |

**解决方法（URL 固定）：**
- 免费注册后，可以在 ngrok 后台设置一个固定的 subdomain（部分区域支持）
- 或者使用 `ngrok http --domain=你的固定域名 8502`（需要付费）

**替代方案（更稳定的内网穿透）：**
- 使用 Cloudflare Tunnel（免费、可固定域名、更稳定）
- 需要有一个域名（可以注册免费域名如 `.tk`）

---

## 常见问题

### Q：ngrok 连接不上？
检查防火墙：确保 ngrok 的出站连接没有被阻止。

### Q：手机访问很慢？
ngrok 免费版服务器在国外，可以：
- 使用国内内网穿透工具如 `花生壳`、`NATAPP`

### Q：如何关闭 ngrok？
在 ngrok 运行的 CMD 窗口按 `Ctrl+C`，然后关闭窗口。

### Q：ngrok 窗口可以关闭吗？
**不可以**。ngrok 窗口必须保持运行，手机才能访问。可以把窗口最小化。

---

## 方案对比

| 方案 | 优点 | 缺点 |
|------|------|------|
| 局域网 | 零配置 | 必须同一 WiFi |
| ngrok | 立刻可用，无需服务器 | URL 会变 |
| ngrok + Supabase | 数据云端同步 | URL 会变 |

**推荐路线：**
1. 现在先用 ngrok，立刻能用手机访问
2. 同时注册 Supabase，实现数据云端同步
3. 需要更稳定时，可以考虑 Cloudflare Tunnel 等替代方案
