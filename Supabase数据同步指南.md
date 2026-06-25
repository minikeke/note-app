# Supabase 数据同步指南

把 `note_app` 的本地 SQLite 数据迁移到 **Supabase 云数据库**，实现：

- 手机、电脑、平板多终端数据同步
- 电脑关机后，数据依然在云端
- 换设备时数据不丢失

---

## 一、实现原理

`database.py` 已改为双后端：

```
启动.bat 设置 DATABASE_URL ──┐
                              ▼
                    database.py 启动时检测环境变量
                              │
            ┌─────────────────┴─────────────────┐
            ▼                                   ▼
    DATABASE_URL 存在                    DATABASE_URL 不存在
    连接 PostgreSQL                      连接本地 SQLite
    （Supabase 云端）                     （data/notes.db）
```

所以：**同一套代码，有云端地址就同步，没有就本地运行**。

---

## 二、Supabase 端配置

### 1. 注册账号

访问 https://supabase.com

- 用邮箱注册并登录

### 2. 创建项目

1. 点击 **New project**
2. **Organization**：选择或新建一个组织
3. **Project name**：填 `note-app`
4. **Database Password**：设置一个强密码（记下，后面要用）
5. **Region**：推荐选 `Asia Pacific (Singapore)`，国内访问更快
6. 点击 **Create new project**，等待 1-2 分钟

### 3. 获取连接字符串

1. 项目创建完成后，进入项目首页
2. 左侧菜单点击 **Project Settings**（齿轮图标）
3. 点击 **Database**
4. 找到 **Connection string** 区域
5. 选择 **URI** 格式，复制类似下面的地址：

   ```
   postgresql://postgres:你的密码@db.xxxxxxx.supabase.co:5432/postgres
   ```

   其中 `xxxxxxx` 是你的项目 Reference ID。

> 注意：不要把这串地址泄露给别人，它包含数据库密码。

---

## 三、应用端配置

### 1. 修改 `启动.bat`

打开 `note_app/启动.bat`，找到这一行：

```bat
set DATABASE_URL=postgresql://postgres:Wlmm1234?1234@db.diyjpopstlveidycmnmp.supabase.co:5432/postgres
```

把它替换成你从 Supabase 复制的连接字符串：

```bat
set DATABASE_URL=postgresql://postgres:你的密码@db.xxxxxxx.supabase.co:5432/postgres
```

### 2. 密码特殊字符处理

如果你的密码包含以下字符，必须替换成 URL 编码：

| 字符 | URL 编码 |
|------|----------|
| `@`  | `%40`    |
| `:`  | `%3A`    |
| `?`  | `%3F`    |
| `#`  | `%23`    |
| `&`  | `%26`    |
| `=`  | `%3D`    |
| `+`  | `%2B`    |
| 空格 | `%20`    |

**示例：**

- 真实密码：`Pass?word#123`
- 连接字符串里应写成：`Pass%3Fword%23123`

### 3. 保存并重启

1. 保存 `启动.bat`
2. 关闭旧的应用控制台窗口
3. 重新双击 `启动.bat`

---

## 四、验证同步是否成功

### 方法 1：看控制台

启动后如果能看到：

```
Uvicorn server started on 0.0.0.0:8502
```

且没有数据库连接报错，通常就是连接上了。

### 方法 2：在 Supabase 里查看数据

1. 打开网页版应用：`http://localhost:8502`
2. 新建一条笔记或日程
3. 回到 Supabase，左侧点击 **Table Editor**
4. 查看 `notes`、`events` 等表里是否出现了刚添加的数据

### 方法 3：手机访问验证

1. 启动 ngrok：`ngrok http 8502`
2. 手机访问 ngrok 给出的 https 地址
3. 在手机里添加一条笔记
4. 回到电脑网页刷新，看数据是否同步出现

---

## 五、常见问题

### Q：启动时报数据库连接错误？

可能原因：

1. **密码错误**：检查 `DATABASE_URL` 里的密码是否正确
2. **特殊字符未编码**：见上面的 URL 编码表
3. **Supabase 项目未创建完成**：新建项目后需要等 1-2 分钟
4. **网络问题**：Supabase 服务器在国外，偶尔可能连不上，多试几次

### Q：原来本地 SQLite 的数据会丢失吗？

不会。设置 `DATABASE_URL` 后，应用会改用新数据库，但原来的 `data/notes.db` 文件不会被删除。如果你想把旧数据导入 Supabase，需要手动导出 JSON 再导入，或者暂时不设置 `DATABASE_URL` 继续使用本地数据。

### Q：如何切回本地 SQLite？

把 `启动.bat` 里的 `set DATABASE_URL=...` 这一行删掉或前面加 `::` 注释掉：

```bat
:: set DATABASE_URL=postgresql://...
```

重启应用即可。

### Q：免费额度够用吗？

Supabase 免费版提供：

- 500 MB 数据库空间
- 每月 5 GB 带宽

个人使用完全足够。

---

## 六、数据安全提醒

- `启动.bat` 里保存了数据库密码，不要把这个文件分享给不信任的人
- 如果电脑是公用的，建议把密码改成临时文件或环境变量方式管理
- Supabase 本身提供加密传输和存储
